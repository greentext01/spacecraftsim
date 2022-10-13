"""Implements the networking part of the server."""

import socket
import threading
from collections import deque

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

    def __init__(self, m_queue_in: deque, m_queue_out: deque):
        self.clients = Clients()
        self.m_queue_in = m_queue_in
        self.m_queue_out = m_queue_out
        self.sock: socket.socket | None = None

    def start_server(self):
        """Starts the server socket."""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((config.get("host", "127.0.0.1"), config.get("port", 5000)))
        self.sock.listen()
        print("Server listening!")

    def run_server(self):
        """Accepts connections, and adds them to the client list."""
        while True:
            conn, _ = self.sock.accept()

            self.clients.add_client(conn)

            listen_thread = threading.Thread(
                target=self.listen, args=(conn,), name=str(conn.getpeername())
            )
            listen_thread.start()

    def send(self, message: str | bytes, sock: socket.socket, client_index: int):
        """Send a message to a client."""
        print(message)
        try:
            if isinstance(message, bytes):
                sock.sendall(len(message))
                sock.sendall(message)
            else:
                encoded = message.encode("utf-8")
                sock.sendall(len(encoded).to_bytes(4, "big"))
                sock.sendall(encoded)
        except socket.error:
            self.clients.del_client(client_index)

    def broadcast(self, message):
        """Sends a message to all clients."""
        with self.clients.clients_lock:
            for i, conn in enumerate(self.clients.clients):
                self.send(message, conn, i)

    def listen(self, conn: socket.socket):
        """Listens to communications from a client."""
        try:
            while True:
                header = conn.recv(4)
                size = int.from_bytes(header, byteorder="big")
                buffer = ""
                while size > 0:
                    data = conn.recv(min(size, 1024))
                    size -= min(size, 1024)

                    if not data:
                        raise socket.error

                    buffer += data.decode("utf-8")

                print(buffer)

                unparsed_command = buffer.split(" ")
                command = Command(unparsed_command[0], unparsed_command[1:])

                if hasattr(command, "command"):
                    print(command.command)

                self.m_queue_out.appendleft(command)
        except socket.error:
            # Client disconnected
            return
