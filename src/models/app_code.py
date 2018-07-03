from edgeworker import Worker, monitor_worker
from envhelpers import *
from weather_sim import Weather
from wind_turb_model import TurbineModel

class WindturbineWorker(Worker):
    def initialization(self):
        self.info("Start the Wind Turbine World")
        self.weather = Weather()
        self.turbine = TurbineModel()
        # Read some environment variables that might change things
        self.getEnv()
        # Initlize the environment for the wind turbine
        self.count = 0
        measurement = self.weather()
        self.turbine.update_env(**measurement)
        self.pitch = 0.0
        self.yaw = 0.0
        # Listen for new control signals
        self.add_subscription(self.turbine_in_channel)
        self.add_subscription("from_ui")
        # Run the models at a regular
        self.setup_timer(self.update_rate_sec,self.run_weather_turbine)
        self.start_timer()

    def work(self,channel,in_object):
        if (channel == self.turbine_in_channel):
            # TODO: Filter pitch and yaw commands
            obj_fault = False
            if 'pitch' in in_object:
                self.pitch = in_object['pitch']
            else:
                self.warning("Received turbine_control without a 'pitch'")
                obj_fault = True
            if 'yaw' in in_object:
                self.yaw = in_object['yaw']
            else:
                self.warning("Received turbine_control without a 'yaw'")
                obj_fault = True
            if obj_fault:
                self.warning("This is what was received %s" % str(in_object))
            else:
                self.info("Received a good turbine_control update")
        if (channel == "from_ui"):
            if 'wind_speed_mod' in in_object:
                mod = in_object['wind_speed_mod']
                self.weather.modify_wind_speed(mod)
            if 'wind_dir_mod' in in_object:
                mod = in_object['wind_dir_mod']
                self.weather.modify_wind_dir(mod)
            if 'air_density_mod' in in_object:
                mod = in_object['air_density_mod']
                self.weather.modify_air_density(mod)

    def run_weather_turbine(self):
        """ Function called at UPDATE_RATE_SEC to maintain the simulation """
        # Get a weather measurement
        measurement = self.weather()
        self.publish(self.weather_out_channel ,measurement)
        # apply to turbine model
        self.turbine.update_env(**measurement)
        power,rpm = self.turbine.power_rspeed(self.pitch,self.yaw)
        out_object = {}
        out_object['power'] = power
        out_object['rpm'] = rpm
        self.publish(self.turbine_out_channel,out_object)
        # make an object to send to the web server
        out_object['pitch'] = self.pitch
        out_object['yaw'] = self.yaw
        out_object.update(measurement)
        self.publish(self.web_viz_out_channel,out_object)
        self.info("Run_weather_turbine has run")

    def getEnv(self):
        self.update_rate_sec = getEnvVarFloat('UPDATE_RATE_SEC',1.0)
        self.web_viz_out_channel = 'viz_updates'
        self.turbine_in_channel = getEnvVarStr('TURBINE_IN_CHANNEL','turbine_control')
        self.turbine_out_channel = getEnvVarStr('TURBINE_OUT_CHANNEL','turbine_measurement')
        self.weather_out_channel = getEnvVarStr('WEATHER_OUT_CHANNEL','weather')

if __name__ == '__main__':
    # Create and start the worker
    windturbine_worker = WindturbineWorker()
    # Worker started and now monitor it
    monitor_worker(windturbine_worker)
