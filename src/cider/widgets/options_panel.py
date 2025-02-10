import cider.interfaces.actions.actions as ca
from cider.interfaces.controller.config_wrapper import ConfigurationWrapper

from cider.screens.quit_screen import QuitScreen
from cider.screens.help_screen import HelpScreen

from textual.containers import Vertical
from textual.visual import SupportsVisual
from textual.widgets import Button, Static


class OptionPanel(Static):
    def __init__(
        self,
        configuration: ConfigurationWrapper | None,
        session: str,
        content: str | SupportsVisual = "",
        *,
        expand: bool = False,
        shrink: bool = False,
        markup: bool = True,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(
            content,
            expand=expand,
            shrink=shrink,
            markup=markup,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )

        self._configuration = configuration
        self._session_name = session

    def compose(self):
        yield Vertical(
            Button("[bold white]Help", id="help_button", classes="options_button"),
            Button(
                "[bold white]Save and Copy",
                id="save_and_copy_button",
                classes="options_button",
            ),
            # Button("[bold white]Save To Database", id="save_to_database_button", classes="options_button"),
            Button(
                "[bold white]Reset",
                id="undo_changes_button",
                classes="options_button",
            ),
            Button("[bold white]Quit", id="quit_button", classes="options_button"),
            id="option_panel",
        )

    def open_new_session(self, configuration: ConfigurationWrapper, session_name: str):
        self._session_name = session_name
        self._configuration = configuration

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "help_button":
            self.app.push_screen(HelpScreen(classes="pop_up_screen"))
        elif event.button.id == "save_and_copy_button":
            if self._configuration is not None and self._session_name:
                ca.CopyFullConfigurationAction(self._configuration)(
                    "current_config.data.xml"
                )
        elif event.button.id == "save_to_database_button":
            pass
        elif event.button.id == "undo_changes_button":
            # Reset everything!
            self.app.get_screen("shifter_view_screen").open_new_file()
        elif event.button.id == "quit_button":
            self.app.push_screen(
                QuitScreen(
                    self._session_name,
                    ConfigurationWrapper("current_config.data.xml"),
                    classes="pop_up_screen",
                )
            )
        else:
            pass
