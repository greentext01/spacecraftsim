"""
All the rocket classes.
"""

import struct
from abc import ABC, abstractmethod
from time import time

from server.config import config


class BaseRocket(ABC):
    """
    The base class for every rocket. Holds common variables
    """

    def __init__(self):
        self.mass_kg = None
        self.fuel_s = None
        self.engine_power_newt = None
        self.server = None
        self.speed_m_s = 0
        self.altitude_m = 0
        self.altitudes = []
        self.flight_start = 0
        self.time_passed = 0
        self.times = []
        self.deltatime = 0
        self.throttle = 0
        self.flown = False

    def set_mass(self, val):
        """
        Sets the mass of the rocket.
        """
        self.mass_kg = val
        return self

    def set_engine_power(self, val):
        """
        Sets the engine power of the rocket.
        """
        self.engine_power_newt = val
        return self

    def set_fuel_s(self, val):
        """
        Sets the fuel of the rocket.
        """
        self.fuel_s = val
        return self

    @abstractmethod
    def measure_deltatime(self):
        """
        Measure the deltatime. The biggest difference between
        an InstantRocket and a normal rocket.
        """

    def fly(self):
        """A wrapper for `fly_next`. Measures the deltatime, then calls the method."""
        self.deltatime = self.measure_deltatime()
        self.time_passed += self.deltatime
        self.times.append(self.time_passed)
        self._fly_next()

    @abstractmethod
    def _fly_next(self):
        pass

    def set_server(self, server):
        """
        Sets the server of the rocket.
        """
        self.server = server
        return self

    def launch(self):
        """
        Launches the rocket!
        """
        last_emitted = 0
        while self.altitude_m >= 0 or self.flown:
            if last_emitted < self.time_passed - 0.5:
                self.server.broadcast(struct.pack("f", self.altitude_m))
                print(self.altitude_m)
                last_emitted = self.time_passed
            self.fly()


class InstantRocket(BaseRocket):
    """
    A rocket where deltatime is always 1.
    Speeds up running the rocket for development purposes
    """

    def measure_deltatime(self):
        return 1

    def _fly_next(self):
        force = 0
        if self.fuel_s > 0:
            self.fuel_s -= self.deltatime
            force += self.engine_power_newt * self.throttle

        force -= config.get("gravity", 9.807) * self.mass_kg

        acceleration_ms2 = force / self.mass_kg

        if self.deltatime >= 1:
            pass

        self.speed_m_s += acceleration_ms2 * self.deltatime

        if self.altitude_m + self.speed_m_s > 0:
            self.altitude_m += self.speed_m_s
            self.flown = True
        else:
            self.altitude_m = 0

        self.altitudes.append(self.altitude_m)


class Rocket(InstantRocket):
    """
    A rocket with real deltatime.
    """

    def __init__(self):
        super().__init__()
        self.prev_time = time()

    def measure_deltatime(self):
        now = time()
        out = now - self.prev_time
        self.prev_time = now
        return out
