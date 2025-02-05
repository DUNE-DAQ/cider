# APPLE: Accessible Platform for Plain and Lightweight Editing

from cider.screens.disable_object_screen import DisableObjectScreen
from cider.screens.select_file_session_screen import SelectFileSessionScreen
from cider.interfaces.controller.config_wrapper import ConfigurationWrapper

from textual.app import App
from textual.driver import Driver
from textual.binding import Binding
import click

import os

class ShifterView(App):
    def __init__(
        self,
        configuration_folder: str,
        consolidate: bool,
        driver_class: type[Driver] | None = None,
        css_path: str | None = None,
        watch_css: bool = False,
        ansi_color: bool = False,
    ):
        super().__init__(driver_class, css_path, watch_css, ansi_color)

        self._configuration_folder = configuration_folder
        self._consolidate = consolidate
        self._exit_message = ""

    def exit_message(self):
        return self._exit_message

    def on_mount(self):
        self.theme = "textual-light"

        self.install_screen(
            SelectFileSessionScreen(self._configuration_folder, self._consolidate),
            name="session_select",
        )

        # Start with the SelectFileSessionScreen
        self.push_screen("session_select")

    def exit(self, message: str | None = None) -> None:
        """Override the exit method to store the exit message."""
        self._exit_message = message
        super().exit()  # Call the original exit method


@click.command()
@click.option("-d", "--input-directory", "input_directory", default="", required=True)
@click.option("-c", "--consolidate", "consolidate", default=True, required=False)
def main(input_directory, consolidate):
    # CONFIGURATION_PATH = "/home/hwallace/scratch/dune_software/daq/daq_work_areas/NFD_DEV_241218_A9/nd_generated_file/"

    app = ShifterView(input_directory, consolidate)
    app.run()
    print("To run DRUNC please copy/paste: ")
    print(app.exit_message())
