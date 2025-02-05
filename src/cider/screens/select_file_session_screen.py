from cider.widgets.file_select_widget import FileSelectWidget
from cider.widgets.session_select_widget import SessionSelectWidget
from cider.interfaces.controller.config_wrapper import ConfigurationWrapper

from cider.interfaces.actions.actions import (GetDalObjectAction,
                                              CopyDalAction,
                                              GetRelatedDalsAction)
from cider.screens.disable_object_screen import DisableObjectScreen


from textual.screen import Screen
from textual.containers import Container, Grid
from textual.widgets import Button, Select, Label, Select
from textual.message import Message

from typing import Any, List
import datetime
import sys

class SelectFileSessionScreen(Screen):
    def __init__(self, session_folder: List[str], consolidate: bool=True, name: str | None = None, id: str | None = None, classes: str | None = None) -> None:
        super().__init__(name, id, classes)

        self._folder = session_folder
        self._selected_config_name  = ""
        self._selected_session_name = ""
        self._consolidate = consolidate

    def compose(self):
        yield Grid(
            FileSelectWidget(self._folder, id="select_file"),
            SessionSelectWidget(id="select_session"),
            Button(id="create_config", label="Generate Configuration", variant="success")
        )

    def on_select_changed(self, event: Select.Changed):
        
        if event.select.id == "config_file_select":
            try:
                self._selected_config_name: str = event.value[0]
                self.query_one("SessionSelectWidget").change_config(self._selected_config_name)
                self._selected_session_name = ""


            except Exception as e:
                raise e
        elif event.select.id == "session_select":
            self._selected_session_name: str = getattr(event.value, 'id')
            
    def create_config(self):
        if not self._selected_config_name:
            raise Exception(f"Couldn't find {self._selected_config_name}")
        elif not self._selected_session_name:
            raise Exception(f"Couldn't find {self._selected_session_name}")

        config_name = self._selected_config_name
        
        if self._consolidate:
            
            db_consolidator = ConsolidateDB(self._selected_config_name,
                                            self._selected_session_name, "Session")
            db_consolidator()

            config_name = db_consolidator.get_generated_config()        
        
        
        # Push the DisableObjectScreen with the selected configuration and session
        self.app.push_screen(
            DisableObjectScreen(
                ConfigurationWrapper(config_name),
                self._selected_session_name,
                name="disable"
            ),
        )

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "create_config":
            self.create_config()

# TODO DELETE THIS!!!!

class ConsolidateDB:
    # YES THIS EXiSTS 
    def __init__(self, current_config_name: str, top_level_object_name: str, top_level_object_class: str):
        self._top_level_object_name = top_level_object_name
        self._top_level_object_class = top_level_object_class
        
        self._current_config_name = current_config_name
        self._new_config_name = self.create_timestamped_file_string(current_config_name)
        
    
    def get_generated_config(self):
        return self._new_config_name
        
    # I need a utils package...
    @classmethod
    def create_timestamped_file_string(cls, file_path: str)->str:
        basepath = file_path.strip(".data.xml")
        ts = datetime.datetime.now().isoformat()
        
        ts=ts.replace(":",".")

        
        return f"{basepath}_{ts}.data.xml"
        # return "test_config.data.xml"
    # 
    def get_all_includes(self, db, file):
        includes = db.get_includes(file)
        for include in includes:
            if "data.xml" in include:
                includes += self.get_all_includes(db, include)

        return list(set(includes))

    def open_files(self)->ConfigurationWrapper:
        database = ConfigurationWrapper(f"{self._current_config_name}")
        
        # Grab included schema
        includes = [i for i in self.get_all_includes(database, None) if ".schema.xml" in i]

        new_database = ConfigurationWrapper("")
        new_database.create_db(self._new_config_name, includes)
        
        new_database.commit()
    
    # Now the fun bit
    def populate_configuration(self):
        sys.setrecursionlimit(10000)  # for example

        # Now we make the configuration
        # TODO: Simplify all of this
        current_configuration = ConfigurationWrapper(self._current_config_name)
        new_configuration = ConfigurationWrapper(self._new_config_name)
        
        # Now we need to get the top level DAL [usually a session]
        top_level_dal = GetDalObjectAction(current_configuration)(self._top_level_object_name, self._top_level_object_class)
        
        
        CopyDalAction(new_configuration)(top_level_dal)
        
        related_objs = self.__populate_configuration(current_configuration, top_level_dal)
        print(related_objs)
        
        # Now we just need to make sure everything's unique
        related_objs = list(set(related_objs))
        
        
        # Now we write to the configuration
        for d in related_objs:
            CopyDalAction(new_configuration)(d)
        
        new_configuration.commit(f"Copied from {self._new_config_name}")
        
    
    def __populate_configuration(self, configuration, dal_obj):

        related_objs = GetRelatedDalsAction(configuration)(dal_obj)
        
        relation_list = []
        for r in related_objs:
            for dal_list in list(r.values())[0]:
                if not isinstance(dal_list, list):
                    dal_list = [dal_list]

                if len(dal_list)==0:
                    return 
                
                for d in dal_list:
                    relation_list.append(d)
                    relation_list += list(self.__populate_configuration(configuration, d) for d in dal_list)[0]


        return relation_list
    

    
    def __call__(self) -> Any:
        self.open_files()
        self.populate_configuration()