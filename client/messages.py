"""Custom Textual messages."""

from textual._types import MessageTarget
from textual.events import Message


class SendCommand(Message):
    """When enter is pressed on an Input widget."""
    def __init__(self, sender: MessageTarget, content: str) -> None:
        super().__init__(sender)
        self.content = content
