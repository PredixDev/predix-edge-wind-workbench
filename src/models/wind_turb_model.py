from numpy import genfromtxt
from numpy.polynomial import polynomial
import numpy as np
from scipy import interpolate
import math
import sys

# Given
# wind_speed_m_s - Wind Speed m/s
# pA - Air_density kg/m3 1.225 at sea level at 15C
# Beta - Blade pitch degs -5 to 6 degs
# Calculate
# Power

class TurbineModel():
    def define_cp(self):
        Beta = genfromtxt('pitch_x.csv', delimiter=',')
        tsr = genfromtxt('tsr_y.csv', delimiter=',')
        cp = genfromtxt('cp_f.csv', delimiter=',')
        print 'Beta (blade,pitch -5 to 6)',Beta.shape
        print 'tsr (tip speed ratio)',tsr.shape
        print 'cp',cp.shape
        # This is the CP function
        self.cp_f = interpolate.interp2d(Beta, tsr, cp, kind='cubic')

    def __init__(self):
        # Constants
        self.rotor_radius_m = 63.0
        self.rotor_speed_rpm_cut_in = 6.9
        self.rotor_speed_rpm_rated = 12.1
        self.rotor_precone_angle_deg = 2.5
        # Constants
        self.wind_speed_m_s_cut_in = 3.0
        self.wind_speed_m_s_rated = 11.41
        self.wind_speed_m_s_cut_out = 25.0
        # Derived Constants
        self.rotor_eff_dia_m = math.cos(math.radians(self.rotor_precone_angle_deg)) * \
                             (self.rotor_radius_m*2.0)
        self.rotor_swept_area_mE3=(np.pi/4)*(self.rotor_eff_dia_m)**2

        # From the NREL 5 MW refrence turbine
        # 2.5 degs -upwind precone
        # swept_area=12445.3 #m2
        # air_density=1.225  #kg/m3  nominal at sea level 15C
        # rotor_speed_rpm=12.1 #rpm
        # rotor_radius=63 #m
        # get data to create look up table
        # Define the CP function
        self.define_cp()

        # Environmental values will be changed by call to update_env
        self.wind_speed_m_s = 11.41
        self.wind_angle_deg = 0.0
        self.air_density_kg_mE3 = 1.225

    def rotor_speed(self, ws):
        # Only used for viz
        # Swag 5000W to get blade moving
        #if ws >
        if ws <= self.wind_speed_m_s_cut_in:
            rs =(self.rotor_speed_rpm_cut_in/self.wind_speed_m_s_cut_in) * ws
        elif ws <= self.wind_speed_m_s_rated:
            rs = self.rotor_speed_rpm_cut_in + \
                 ( (self.rotor_speed_rpm_rated - self.rotor_speed_rpm_cut_in) / \
                 (self.wind_speed_m_s_rated - self.wind_speed_m_s_cut_in) ) * \
                 (ws - self.wind_speed_m_s_cut_in);
        else:
            rs = self.rotor_speed_rpm_rated
        return(rs)

    def tsr(self, wind_speed_m_s, rotor_speed_rpm):
        if wind_speed_m_s <= 0.0 or rotor_speed_rpm <= 0.0:
            tsr = 0.0
        else:
            tsr = ((2.0 * math.pi * self.rotor_radius_m)/ (60/rotor_speed_rpm)) / wind_speed_m_s
        return(tsr)

    def find_best_pitch(self, wind_speed_m_s, rotor_speed_rpm):
        current_tsr = self.tsr( wind_speed_m_s, rotor_speed_rpm)
        cp_max = -5000
        bang_max = 0
        for bang in range(-5,6):
            cp = self.cp_f(bang,current_tsr)
            if cp > cp_max:
                cp_max = cp
                bang_mac = bang
        return(bang)

    def clamp(self,x,ul,ll):
        y = x if x < ul else ul
        y = y if y > ll else ll
        return(y)

    def yaw_error(self, source_angle_deg, turbine_angle_deg):
        # source points to wind
        # if source_angle is 120 and turbine_angle is 300 error is 180
        # abs(source_angle - turbine_angle) = yaw_error
        # s = 5 t = 345
        # abs(5-345) = 340
        # if greater then 180 subtract from 360
        # 360 - 340 = 20
        # abs(5-25) = 20
        # abs(5 - 186) = 181 (greater than 180) 360-181=179
        # abs(359-5) = 354 (greater than 180) 360 - 354=6
        # abs(179-323) = 144
        delta = abs(source_angle_deg - turbine_angle_deg)
        if delta > 180.0:
            delta = 360.0 - delta
        return(delta)

    def update_env(self,wind_speed=0.0,wind_dir=0.0,air_density=1.225):
        """ Apply weather updates here
        wind_speed in meters/second
        wind_dir in degrees
        air_density in kg/m^3
        """
        # Call this to update environment
        self.wind_speed_m_s = self.clamp(wind_speed,25.0,0.0)
        self.wind_angle_deg = divmod(wind_dir,360.0)[1]
        self.air_density_kg_mE3 = self.clamp(air_density,1.522,1.1)

    def power_rspeed(self,beta_angle_deg=0,turbine_angle_deg=0.0):
        # Call this to recalc power and rotor_speed
        debug = False
        # sanity clamping
        beta_angle_deg = self.clamp(beta_angle_deg,6,-5)

        oa_angle = 0.0

        if turbine_angle_deg == -1.0:
            oa_angle = 0.0
        else:
            turbine_angle_deg = divmod(turbine_angle_deg,360)[1]
            oa_angle = self.yaw_error(self.wind_angle_deg, turbine_angle_deg)

        # Find the normal component of the wind due to yaw error
        wind_speed_m_s_corr = self.wind_speed_m_s * (0.5 * (math.cos(math.radians(oa_angle)) + 1.0))
        if debug:
            print >>sys.stderr,"Corrected WS",wind_speed_m_s_corr
        # Find the rotor speed in RPM
        rotor_speed_rpm = self.rotor_speed(wind_speed_m_s_corr)

        # Get the Tip Speed Ratio
        tsr = self.tsr(wind_speed_m_s_corr,rotor_speed_rpm)
        if debug:
            print >>sys.stderr,"tsr",tsr

        # Calculate the Cp (Coeffeicient of Power ~= efficency)
        cp = self.cp_f(beta_angle_deg,tsr)
        # Clamp
        cp = cp if cp > 0.0 else np.array([0.0])
        if debug:
            print >>sys.stderr,"cp",cp

        # Mass flow
        pA_2 = (self.air_density_kg_mE3*self.rotor_swept_area_mE3)/2.0

        #P = cp*pA_2*inv_v_3
        P = cp * pA_2 * (wind_speed_m_s_corr**3)

        if P >= 5.0e6:
            P= np.array([5.0e6])

        return([P[0],rotor_speed_rpm])

if __name__ == '__main__':
    # Create the worker
    tm = TurbineModel()
    # look at power versus wind speed
    print "Wind Speed *********************************************"
    for ws_m in xrange(0,22):
        ws = ws_m
        tm.update_env(ws)
        p_r = tm.power_rspeed()
        print ws,p_r
    print "Wind Angle *********************************************"
    for wd_ang in xrange(0,180):
        ws = 10 # m/s
        tm.update_env(ws,wd_ang)
        p_r = tm.power_rspeed()
        print wd_ang,p_r #,p1,p2
    print "Beta Angle *********************************************"
    for beta_ang in xrange(-5,7):
        ws = 10 # m/s
        wd_ang = 0.0
        tm.update_env(ws,wd_ang)
        p_r = tm.power_rspeed(beta_ang)
        print beta_ang,p_r #,p1,p2

# Wind speeds range
# Cut in speed 3 m/s
# Cut out speed 22 m/s
