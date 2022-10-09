"""Handles sending and recieving commands"""

import socket
from threading import Thread
from time import sleep
from typing import TYPE_CHECKING
from client.config import config
from client.utils import divide_size

if TYPE_CHECKING:
    from client.tui import Frontend


class Client:
    """Networking class"""

    def __init__(self, frontend: "Frontend"):
        self.frontend = frontend
        self.host = config.get("host", "127.0.0.1")
        self.port = config.get("port", 5000)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        """Connect the socket to the server"""
        self.sock.connect((self.host, self.port))
        self.frontend.add_to_content("Connected!")

    def client_thread(self):
        """Handles the networking part."""
        while True:
            data_size = int(self.sock.recv(3))
            message = ""
            for size in divide_size(data_size, 1024):
                while data := self.sock.recv(size):
                    message += data.decode("utf-8")

            self.frontend.post_message(message)

    def start_client(self):
        """Start a new thread that recieves messages"""
        Thread(target=self.client_thread)

    def send(self, message: str):
        """Send a message to the server"""
        try:
            self.sock.sendall(len(message).to_bytes(3, 'big'))
            self.sock.sendall(message.encode("utf-8"))
        except socket.error:
            self.frontend.add_to_content("Trying to reconnect...")

            while not self.reconnect():
                sleep(1)
                self.frontend.add_to_content("Trying to reconnect...")

    def reconnect(self):
        """Try to reconnect to the server"""
        try:
            self.sock.connect((self.host, self.port))
            self.frontend.log("Connected!")
            return True

        except ConnectionRefusedError:
            return False

        except socket.error:
            self.sock.close()
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            return False
