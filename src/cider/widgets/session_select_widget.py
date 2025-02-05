from cider.interfaces.controller.config_wrapper import ConfigurationWrapper
from cider.interfaces.actions.actions import GetDalsOfClassAction, GetAttributeAction

from textual.widgets import Select, Static

class SessionSelectWidget(Static):
    def change_config(self, input_database):
        # Create Session
        sessions = []

        if input_database:
            config = ConfigurationWrapper(input_database)            
            sessions = GetDalsOfClassAction(config)("Session")
        
        self._selection_list = [(GetAttributeAction(config)(s, 'id'), s) for s in sessions]
        
        select_widget = self.query_one("Select")
        
        select_widget.set_options(self._selection_list)
                
        
    def compose(self):
        yield Select(options=([]), id="session_select", prompt="Select a Session")
        
