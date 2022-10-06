"""
Classes for Rokt commands
"""
from abc import ABC, abstractmethod
from typing import Type

from server.rocketry import BaseRocket


class BaseCommand(ABC):
    """Represents a rokt command"""

    def __init__(self, rocket: BaseRocket, command: str, args: list[str]) -> None:
        self.rocket = rocket
        self.command = command
        self.args = args

    @abstractmethod
    def execute(self):
        """Runs that command"""


class EngineCommand(BaseCommand):
    """Sets the engine throttle"""

    def execute(self) -> None | str:
        try:
            # Clamp throttle between 0 and 1
            self.rocket.throttle = max(min(float(self.args[0]), 1), 0)
            return None
        except IndexError:
            return "Missing throttle"
        except ValueError:
            return "Throttle isn't a number"


class Command:
    """Factory for commands"""
    def __init__(self, rocket, command, args):
        try:
            command_mapping: dict[str, Type[BaseCommand]] = {
                "engine": EngineCommand,
            }

            self.command = command_mapping[command](rocket, command, args)
        except KeyError:
            pass

    def execute(self):
        """Runs that command"""
        if hasattr(self, "command") and self.command:
            return self.command.execute()
