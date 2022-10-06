"""A client for spacecraftsim"""

import socket
import struct
from collections import deque
from threading import Thread
from time import sleep

from rich import box
from rich.align import Align
from rich.text import Text
from textual import events
from textual.app import App
from textual.reactive import Reactive
from textual.widget import Panel, Widget
from textual.widgets import Placeholder
from textual.events import Key

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


def insert_str(string: str, char: str, index: int):
    return string[:index] + char + string[index:]


def del_char(string: str, index: int):
    return string[: index - 1] + string[index:]


class Input(Widget):
    content = Reactive("")
    cursor_pos = Reactive(0)

    async def on_key(self, event: events.Key):

        if event.key == "ctrl+h" and self.content:
            self.content = del_char(self.content, self.cursor_pos)
            self.cursor_pos -= 1
        elif event.key == "ctrl+h" and self.content:
            self.content = del_char(self.content, self.cursor_pos)
            self.cursor_pos -= 1
        elif event.key == "left" and self.cursor_pos >= 1:
            self.cursor_pos -= 1
        elif event.key == "right" and self.cursor_pos <= len(self.content) - 1:
            self.cursor_pos += 1
        elif event.key == "enter":
            await self.emit(Key(self, "enter"))
        elif len(event.key) == 1:
            self.content = insert_str(self.content, event.key, self.cursor_pos)
            self.cursor_pos = len(self.content)

    def render(self):
        content = "> " + insert_str(self.content, "|", self.cursor_pos)
        return Panel(
            Align.left(Text(content)), height=3, box=box.ROUNDED, border_style="none"
        )


class Frontend(App):
    """Handles showing info to users."""

    async def on_mount(self):
        """On mount"""

        await self.view.dock(Input(), edge="bottom", size=3)
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
