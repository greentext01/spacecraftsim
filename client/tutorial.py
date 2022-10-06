from rich.align import Align
from rich.text import Text
from textual import events
from textual.app import App
from textual.reactive import Reactive
from textual.widget import Panel, Widget
from rich import box


def insert_str(string: str, char: str, index: int):
    return string[:index] + char + string[index:]


def del_char(string: str, index: int):
    return string[: index - 1] + string[index:]



class MyApp(App):
    async def on_mount(self):
        await self.view.dock(Input())


MyApp.run()
