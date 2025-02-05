from textual.screen import Screen
from textual.widgets import Header, Footer, Button, Static
from textual.containers import Horizontal, ScrollableContainer

from cider.interfaces.controller.config_wrapper import ConfigurationWrapper
from cider.interfaces.actions.actions import (
    GetDalsOfClassAction,
    CommitConfigurationAction,
    GetAttributeAction,
    DisableDalAction,
    UpdateDalAction,
)


from cider.widgets.on_off_grid_widget import DisableObjectWidget, OnOffGridWidget
from cider.screens.exit_screen import ExitScreen

class DisableObjectScreen(Screen):
    # Okay lets go
    CSS_PATH = "toggle_screen.tcss"

    def __init__(
        self,
        configuration: ConfigurationWrapper,
        session: str,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name, id, classes)

        self._configuration = configuration
        # Get objects we want to display
        self.disableable_objs = GetDalsOfClassAction(self._configuration)("Component")

        self.session = session

        self.get_attribute = GetAttributeAction(self._configuration)

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "commit_button":
            CommitConfigurationAction(self._configuration)("")
        elif event.button.id == "quit_button":
            message = f"drunc-unified-shell ssh-standalone {self._configuration.file_name} {self.session}"
            self.app.push_screen(ExitScreen(message))

    def compose(self):
        # Okay we can sort by class id's
        yield Static(f"[bold blue]File[/bold blue]: [bold black]{self._configuration.file_name}", classes="table-header")

        with ScrollableContainer():
            disable_obj =  DisableObjectWidget(self._configuration, self.session)
            disable_obj.add_action_sequence("switch_changed", [DisableDalAction(self._configuration), UpdateDalAction(self._configuration)])        
            yield disable_obj
        
        
        yield Button("Save Local", id="commit_button", variant="success")
        yield Button("Quit", id="quit_button", variant="error")

        yield Header()
        yield Footer()

