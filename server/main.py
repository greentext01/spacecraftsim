"""
The server
"""

from collections import deque
import threading

from server.networking import Server
from server.rocketry import BaseRocket, Rocket

HOST = "127.0.0.1"
PORT = 5000
GRAVITY = 9.807


class Runner:
    """Runs a entire rocket."""

    def __init__(self, rocket: BaseRocket, server: Server):
        self.server = server
        self.rocket = rocket.set_server(self.server)

        self.rocket_thread = threading.Thread(target=self.rocket.launch)
        self.srv_thread = threading.Thread(target=self.server.run_server)

    def start(self):
        """Starts the rocket and server."""
        self.server.start_server()
        self.srv_thread.start()
        self.rocket_thread.start()


def main():
    """The main function."""
    rocket_to_server_mq = deque()
    server_to_rocket_mq = deque()

    rocket = (
        Rocket(server_to_rocket_mq, rocket_to_server_mq)
        .set_engine_power(10)
        .set_fuel_s(10)
        .set_mass(1)
    )
    server = Server(rocket_to_server_mq, server_to_rocket_mq)

    Runner(rocket, server).start()


if __name__ == "__main__":
    main()
