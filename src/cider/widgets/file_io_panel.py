import cider.interfaces.actions.actions as ca
from cider.interfaces.controller.config_wrapper import ConfigurationWrapper
from cider.utils.file_system_watcher import FileSystemWatcher
from watchdog.observers import Observer
import threading
from textual.containers import Grid
from textual.visual import SupportsVisual
from textual.widgets import Button, Static, Select
from textual.message import Message
from textual.reactive import reactive
from typing import List, Optional, Tuple
import os
from pathlib import Path
import logging

from cider.utils.management_interface import ManagementInterface


class FileIOPanel(Static):
    '''
    I/O panel for selecting a configuration file and session.
    '''
    branch_options = reactive([])
    file_options = reactive([])

    
    def __init__(
        self,
        install_path=".",
        default_config: str="",
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

        self._default_config = default_config
        self._manager = ManagementInterface(install_path)

        self._branch_options = self._manager.get_base_branches()
        self._file_options = self._manager.get_configs()
    
    
        self._selected_branch = None
        self._selected_session_name = None
        self._selected_config_name = None
        self._configuration = None
    
    def compose(self):
        with Grid(id="file_io_panel_grid"):
            # Base branch menu
            yield Select(
                [(b,b) for b in self._branch_options],
                prompt="Select a Base Branch",
                id="select_base_branch",
                classes="file_select",
            )
            
            yield Select(
                [(f,f) for f in self._file_options],
                prompt="Select a File",
                id="select_file",
                classes="file_select",
            )
            
            yield Select(
                [],
                prompt="Select a Session",
                id="select_session",
                classes="file_select",
                disabled=True,
            )

            yield Button(
                "Open",
                id="open_file_button",
                disabled=True,
                classes="file_io_button",
            )

            yield Button(
                "Refresh Branches",
                id="refresh_branch_button",
                disabled=True,
                classes="file_io_button",
            )

            yield Static(
                "[bold medium_violet_red]   No file loaded\n  ",
                id="file_io_panel_message",
            )
            

    def on_select_changed(self, event: Select.Changed) -> None:
        """Handles changes to the select widgets."""
        if event.select.id == "select_base_branch":
            self.file_options = self._manager.get_configs()
        elif event.select.id == "select_file":
            self._open_new_file(event.value)
        elif event.select.id == "select_session":
            self._selected_session_name = (
                event.value if event.value != Select.BLANK else ""
            )
            self._update_button_state()


    def _update_button_state(self) -> None:
        """Updates the state of the open button based on selected config and session."""
        self.query_one("#open_file_button").disabled = not (
            self._selected_config_name and self._selected_session_name
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handles the button press event."""
        if event.button.id=="open_file_button" and self._selected_config_name and self._selected_session_name:
            self.query_one("#file_io_panel_message").update(
                f"   [bold green]Current Config[/bold green]: [deep_pink4]{self._configuration.file_name}[/deep_pink4]\n   [bold green]Session[/bold green]:  [deep_pink4]{self._selected_session_name}"
            )
        elif event.button.id == "refresh_branch_button":
            self._branch_options = self._manager.get_base_branches()
            self._file_options = self._manager.get_configs()

            
        else:
            self._deconfigure()

    def _open_new_file(self, file_name: str) -> None:
        """Handles opening a new file and updating the session list."""
        if file_name == Select.BLANK:
            self._selected_config_name = None
            self._selected_session_name = None
            self._update_session_select([])
            return

        self._selected_config_name = file_name
        self._manager.checkout_conf(file_name)
        
        self._configuration = ConfigurationWrapper(self._selected_config_name)

        # Grab all the sessions available
        session_list = [
            (
                ca.GetAttributeAction(self._configuration)(i, "id"),
                ca.GetAttributeAction(self._configuration)(i, "id"),
            )
            for i in ca.GetDalsOfClassAction(self._configuration)("Session")
        ]

        self._update_session_select(session_list)

    def _update_session_select(self, options: List[Tuple[str, str]]) -> None:
        """Updates the session select widget with the given options."""
        try:
            self.query_one("#select_session").set_options(options)
        except Exception as e:
            logging.warning(f"Failed to update session select: {e}")


    def _deconfigure(self) -> None:
        """Resets the panel to its default state."""
        self._selected_config_name = ""
        self._configuration = None
        self._selected_session_name = Select.BLANK
        self._update_session_select([])
        self.query_one("#file_io_panel_message").update(
            "[bold medium_violet_red]   No file loaded\n  "
        )
        self.post_message(self.Deconfigured())


    @property
    def selected_config_name(self) -> str | None:
        """Returns the selected configuration name."""
        return self._selected_config_name

    @property
    def selected_session_name(self) -> str | None:
        """Returns the selected session name."""
        return self._selected_session_name



    class Deconfigured(Message):
        """Message sent when the panel is deconfigured."""

    class PathChanged(Message):
        """Message sent when the file list changes."""
