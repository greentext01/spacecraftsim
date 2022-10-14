"""Custom textual widgets"""

from rich.text import Text
from textual import events
from textual.reactive import Reactive
from textual.widget import Widget

from client.messages import SendCommand
from client.utils import del_char, insert_str


class Input(Widget):
    """Text input widget"""

    content = Reactive("")
    cursor_pos = Reactive(0)

    def clear(self):
        self.content = ""
        self.cursor_pos = 0

    async def on_key(self, event: events.Key):
        if event.key == "ctrl+h" and self.content:
            self.content = del_char(self.content, self.cursor_pos)
            self.cursor_pos -= 1
        elif event.key == "left" and self.cursor_pos >= 1:
            self.cursor_pos -= 1
        elif event.key == "right" and self.cursor_pos <= len(self.content) - 1:
            self.cursor_pos += 1
        elif event.key == "enter":
            await self.emit(SendCommand(self, self.content))
            self.content = ""
        elif event.key == "end":
            self.cursor_pos = len(self.content)
        elif event.key == "home":
            self.cursor_pos = 0
        elif len(event.key) == 1:
            # Is it not a modifier key?
            self.content = insert_str(self.content, event.key, self.cursor_pos)
            self.cursor_pos = len(self.content)

    def render(self):
        content = "> " + insert_str(self.content, "|", self.cursor_pos)
        return Text(content)
