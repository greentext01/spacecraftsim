"""The client's user interface."""

from textual.app import App
from textual.widgets import ScrollView
from client.networking import Client

from client.widgets import Input
from client.messages import SendCommand


class Frontend(App):
    """Handles showing info to users."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.content = ""
        self.input = None
        self.body = None
        self.client = None

    def add_to_content(self, string: str):
        """
        Add a string to content and cut content if it is bigger than 1000.

        Returns:
            content, after being cut.
        """
        self.content += string
        self.content = self.content[:1000]
        return self.content

    async def on_load(self):
        self.client = Client(self)
        self.client.connect()
        self.client.start_client()

    async def on_mount(self):
        """On mount"""
        self.input = Input()
        self.body = ScrollView()

        await self.view.dock(self.input, edge="bottom", size=1)
        await self.view.dock(self.body, edge="top")

    async def handle_send_command(self, event: SendCommand):
        """When the user sends a command."""
        self.client.send(event.content)
