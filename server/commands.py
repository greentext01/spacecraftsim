"""
Classes for Rokt commands
"""
from abc import ABC, abstractmethod
from typing import Type

from server.rocketry import BaseRocket


class BaseCommand(ABC):
    """Represents a rokt command"""

    def __init__(self, command: str, args: list[str]) -> None:
        self.command = command
        self.args = args

    @abstractmethod
    def execute(self, rocket: BaseRocket) -> None | str:
        """Runs that command"""


class EngineCommand(BaseCommand):
    """Sets the engine throttle"""

    def execute(self, rocket) -> None | str:
        try:
            # Clamp throttle between 0 and 1
            rocket.throttle = max(min(float(self.args[0]), 1), 0)
            return None
        except IndexError:
            return "Missing throttle"
        except ValueError:
            return "Throttle isn't a number"


class Command:
    """Factory for commands"""

    def __init__(self, command, args):
        try:
            command_mapping: dict[str, Type[BaseCommand]] = {
                "engine": EngineCommand,
            }

            self.command = command_mapping[command](command, args)
        except KeyError:
            pass

    def execute(self, rocket: BaseRocket) -> None | str:
        """Runs that command"""
        if hasattr(self, "command") and self.command:
            return self.command.execute(rocket)

        return "Invalid command"
