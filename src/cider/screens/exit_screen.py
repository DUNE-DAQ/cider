from textual.widgets import Static, Switch, Button, TextArea, Label
from textual.containers import Horizontal, Grid
from textual.screen import Screen


class ExitScreen(Screen):
    """Screen with a dialog to quit."""
    CSS_PATH = "quit_screen.tcss"

    def __init__(self, message: str, name: str | None = None, id: str | None = None, classes: str | None = None) -> None:        
        super().__init__(name, id, classes)
        self._message = message

    def compose(self):
        yield Grid(
            Label(f"Are you happy with the config?", id="question"),
            # Button("Copy Command", variant="success", id="copy"),
            Button("Yep!", variant="success", id="quit"),
            Button("Nope!", variant="warning", id="cancel"),

            id="dialog",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "quit":
            self.app.exit(self._message)
        else:
            self.app.pop_screen()
