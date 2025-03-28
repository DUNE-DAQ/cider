import cider.interfaces.actions.actions as ca
from cider.interfaces.controller.config_wrapper import ConfigurationWrapper

from pathlib import Path
from typing import List, Tuple
import os

class ConfigPathReader:
    @classmethod
    def get_db_from_path(cls, file_path: Path):
        """Returns a database path if the file is a valid configuration."""
        if file_path.is_file() and ".data.xml" in str(file_path):
            if cls._get_number_of_sessions(str(file_path)) > 0:
                return file_path
        return None

    @classmethod
    def _get_number_of_sessions(cls, config_file_path: str) -> int:
        """Returns the number of sessions in the given configuration file."""
        try:
            config_file = ConfigurationWrapper(config_file_path)
            return len(ca.GetDalsOfClassAction(config_file)("Session"))
        except Exception:
            return 0

    # FILE STUFF
    @classmethod
    def __call__(
        cls, session_directories: str | List[str]
    ) -> List[Tuple[str, str]]:
        """Generates a list of file options from the given directories."""
        if isinstance(session_directories, str):
            session_directories = (
                [os.getcwd()]
                if not session_directories
                else [Path(p) for p in session_directories.split(":")]
            )
        else:
            session_directories = [Path(p) for p in session_directories]

        database_list = []
        for directory in session_directories:
            if not directory.is_dir():
                continue

            for item in directory.iterdir():
                db = cls.get_db_from_path(item)
                if db:
                    database_list.append((str(db.name), str(db)))

                if not item.is_dir():
                    continue

                for sub_item in item.iterdir():
                    db = cls.get_db_from_path(sub_item)
                    if db:
                        database_list.append(str(db))

        return database_list
 