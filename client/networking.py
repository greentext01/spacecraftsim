"""Handles sending and recieving commands"""

from collections import deque
import socket
from threading import Thread
from time import sleep
from client.config import config
from client.utils import divide_size


class Client:
    """Networking class"""

    def __init__(self, queue: deque):
        self.host = config.get("host", "127.0.0.1")
        self.port = config.get("port", 5000)
        self.message_queue = queue
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        """Connect the socket to the server"""
        self.sock.connect((self.host, self.port))
        self.message_queue.appendleft("Connected!")

    def client_thread(self):
        """Handles the networking part."""
        while True:
            data_size = int.from_bytes(self.sock.recv(3), "big")
            message = ""
            for size in divide_size(data_size, 1024):
                data = self.sock.recv(size)
                message += data.decode("utf-8")
                print(data.decode("utf-8"))

            self.message_queue.appendleft(message)

    def start_client(self):
        """Start a new thread that recieves messages"""
        Thread(target=self.client_thread).start()

    def send(self, message: str):
        """Send a message to the server"""
        try:
            self.sock.sendall(len(message).to_bytes(3, "big"))
            self.sock.sendall(message.encode("utf-8"))
        except socket.error:
            self.message_queue.appendleft("Trying to reconnect...")

            while not self.reconnect():
                sleep(1)
                self.message_queue.appendleft("Trying to reconnect...")

    def reconnect(self):
        """Try to reconnect to the server"""
        try:
            self.sock.connect((self.host, self.port))
            self.message_queue.appendleft("Connected!")
            return True

        except ConnectionRefusedError:
            return False

        except socket.error:
            self.sock.close()
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            return False
