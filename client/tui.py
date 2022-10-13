"""The client's user interface."""

from collections import deque
from textual.app import App
from textual.reactive import Reactive
from textual.widgets import ScrollView
from client.networking import Client

from client.widgets import Input
from client.messages import SendCommand


class Frontend(App):
    """Handles showing info to users."""

    content = Reactive("")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.input = None
        self.body = None
        self.client = None
        self.queue: deque[str] = deque()

    async def add_to_content(self, string: str):
        """
        Add a string to content and cut content if it is bigger than 1000.

        Returns:
            content, after being cut.
        """
        self.content += f"\n{self.body.y}; {self.body.max_scroll_y}"
        self.content = self.content[-1000:]
        await self.body.update(self.content)
        if self.body.y >= self.body.max_scroll_y - 10:
            self.body.y = self.body.max_scroll_y

    async def on_load(self):
        """On load"""
        self.client = Client(self.queue)
        self.client.connect()
        self.client.start_client()

    async def on_mount(self):
        """On mount"""
        self.input = Input()
        self.body = ScrollView("")

        await self.view.dock(self.input, edge="bottom", size=1)
        await self.view.dock(self.body, edge="top")

        self.set_interval(0.1, self.print_messages)

    async def print_messages(self):
        """Prints all the messages in the queue"""
        while self.queue:
            await self.add_to_content(self.queue[0])
            self.queue.popleft()

    async def handle_send_command(self, event: SendCommand):
        """When the user sends a command."""
        self.client.send(event.content)
