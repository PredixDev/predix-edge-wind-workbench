
import random
""" Simple simulation of the weather for a wind farm Edge programming exercise """

class RandWalk():
    """Class that implements a Random Walk"""
    def __init__(self, step, start, max, min):
        self.step = abs(step)
        self.current = start
        self.max = max
        self.min = min

    def __call__(self):
        """ Allows the direct calling of the object to get next value """
        self.current += random.uniform(-self.step, self.step)
        while self.current > self.max:
            self.current += random.uniform(-self.step, 0)
        while self.current < self.min:
            self.current += random.uniform(0, self.step)
        return(self.current)

    def modify_current(self,mod):
        """Adds to the current but doesn't violate the limits"""
        self.current = mod
        if self.current > self.max:
            self.current = self.max
        if self.current < self.min:
            self.current = self.min


class Weather():
    """ Class to simulate the weather (or parts of it) very crude """
    def __init__(self):
        self.wind_dir = RandWalk(5.0,180,360.0,0.0)
        self.wind_speed = RandWalk(0.5,8.0,23.0,0.0)
        self.air_density = RandWalk(0.005,1.225,1.552,1.12)

    def __call__(self):
        """ Gets the next weather measurements """
        wind_dir_value = self.wind_dir()
        wind_speed_value = self.wind_speed()
        air_density_value = self.air_density()
        measurement = {
            "wind_dir": wind_dir_value,
            "wind_speed": wind_speed_value,
            "air_density": air_density_value
        }
        return(measurement)

    def modify_wind_speed(self,mod):
        self.wind_speed.modify_current(mod)

    def modify_wind_dir(self,mod):
        self.wind_dir.modify_current(mod)

    def modify_air_density(self,mod):
        self.air_density.modify_current(mod)
