"""Implements the networking part of the server."""

import socket
import threading
from server.commands import Command

from server.config import config


class Clients:
    """
    A wrapper for both a client list and a lock.
    """

    def __init__(self) -> None:
        self.clients_lock = threading.Lock()
        self.clients: list[socket.socket] = []

    def add_client(self, client: socket.socket):
        """Adds a client"""
        self.clients.append(client)
        return len(self.clients) - 1

    def del_client(self, client_idx):
        """Removes a client"""
        del self.clients[client_idx]


class Server:
    """
    Handles networking for rockets.
    """

    def __init__(self, rocket):
        self.clients = Clients()
        self.rocket = rocket

    def run_server(self):
        """Accepts connections, and adds them to the client list."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind((config.get("host", "127.0.0.1"), config.get("port", 5000)))
            sock.listen()
            print("Server listening!")
            while True:
                conn, _ = sock.accept()

                listen_thread = threading.Thread(
                    target=self.listen, args=(conn,), name=str(conn.getpeername())
                )
                listen_thread.start()

    def broadcast(self, message):
        """Sends a message to all clients."""
        with self.clients.clients_lock:
            for i, conn in enumerate(self.clients.clients):
                try:
                    conn.sendall(message)
                except socket.error:
                    self.clients.del_client(i)

    def listen(self, conn: socket.socket):
        """Listens to communications from the client."""
        try:
            while True:
                header = conn.recv(4)
                size = int.from_bytes(header)
                buffer = ""
                while size >= 0:
                    data = conn.recv(min(size, 1024))
                    size -= min(size, 1024)

                    if not data:
                        raise socket.error

                    buffer += data

                unparsed_command = buffer.split(" ")
                command = Command(
                    self.rocket, unparsed_command[0], unparsed_command[1:]
                )
                if error := command.execute():
                    conn.sendall(error)
        except socket.error:
            # Client disconnected
            return
