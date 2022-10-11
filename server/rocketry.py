"""
All the rocket classes.
"""

from collections import deque
import struct
from abc import ABC, abstractmethod
from time import sleep, time
from typing import TYPE_CHECKING

from server.config import config

if TYPE_CHECKING:
    from server.commands import BaseCommand


class BaseRocket(ABC):
    """
    The base class for every rocket. Holds common variables
    """

    def __init__(self, m_queue_in: deque["BaseCommand"], m_queue_out: deque):
        self.mass_kg = None
        self.fuel_s = None
        self.engine_power_newt = None
        self.server = None
        self.speed_m_s = 0
        self.altitude_m = 0
        self.flight_start = 0
        self.time_passed = 0
        self.deltatime = 0
        self.throttle = 0
        self.flown = False
        self.m_queue_in = m_queue_in
        self.m_queue_out = m_queue_out

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
        self._fly_next()

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
                self.server.broadcast(str(self.altitude_m))
                last_emitted = self.time_passed

            self.fly()
            sleep(0.2)

    def _fly_next(self):
        force = 0
        if self.fuel_s > 0:
            self.fuel_s -= self.deltatime * self.throttle
            force += self.engine_power_newt * self.throttle

        force -= config.get("gravity", 9.807) * self.mass_kg

        acceleration_ms2 = force / self.mass_kg

        if self.deltatime >= 1:
            pass

        self.speed_m_s += acceleration_ms2 * self.deltatime

        # Cap the speed, so that it doesn't go through the ground.
        self.speed_m_s = max(-self.altitude_m, self.speed_m_s)

        self.altitude_m += self.speed_m_s

        for command in self.m_queue_in:
            command.execute(self)

        self.m_queue_in.clear()


class InstantRocket(BaseRocket):
    """
    A rocket where deltatime is always 1.
    Speeds up running the rocket for development purposes
    """

    def measure_deltatime(self):
        return 1


class Rocket(InstantRocket):
    """
    A rocket with real deltatime.
    """

    def __init__(self, m_queue_in: deque, m_queue_out: deque):
        super().__init__(m_queue_in, m_queue_out)
        self.prev_time = time()

    def measure_deltatime(self):
        now = time()
        out = now - self.prev_time
        self.prev_time = now
        return out
