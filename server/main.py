"""
The server
"""

import threading

from server.networking import Server
from server.rocketry import BaseRocket, Rocket

HOST = "127.0.0.1"
PORT = 5000
GRAVITY = 9.807


class Runner:
    """Runs a entire rocket."""

    def __init__(self, rocket: BaseRocket):
        self.server = Server(rocket)
        self.rocket = rocket.set_server(self.server)

        self.rocket_thread = threading.Thread(target=self.rocket.launch)
        self.srv_thread = threading.Thread(target=self.server.run_server)

    def start(self):
        """Starts the rocket and server."""
        self.srv_thread.start()
        self.rocket_thread.start()


def main():
    """The main function."""
    rocket = Rocket().set_engine_power(10).set_fuel_s(10).set_mass(1)

    Runner(rocket).start()


if __name__ == "__main__":
    main()
