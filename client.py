"""A client for spacecraftsim"""

import socket
import struct
from collections import deque
from threading import Thread
from time import sleep

from textual.app import App
from textual.widgets import Placeholder

HOST = "127.0.0.1"
PORT = 5000

backend_bound_mq = deque()
frontend_bound_mq = deque()


def client_thread():
    """Handles the networking part."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        print("Connected!")
        while data := s.recv(1024):
            frontend_bound_mq.appendleft(struct.unpack("f", data)[0])


class Frontend(App):
    """Handles showing info to users."""

    async def on_mount(self):
        """On mount"""

        await self.view.dock(Placeholder(), edge="bottom", size=3)
        await self.view.dock(Placeholder(), edge="top")


def main():
    """The program's entry point"""
    network_thread = Thread(target=client_thread)
    frontend_thread = Thread(target=Frontend.run)

    network_thread.start()
    frontend_thread.start()

    # Don't ignore KeyboardInterrupt
    while True:
        sleep(100)


if __name__ == "__main__":
    main()
