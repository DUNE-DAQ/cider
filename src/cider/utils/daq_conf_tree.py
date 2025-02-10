# Essentially the tree from https://github.com/DUNE-DAQ/daqconf/blob/develop/scripts/daqconf_inspector

import cider.interfaces.actions.actions as ca
from cider.interfaces.controller.config_wrapper import ConfigurationWrapper

from typing import Union
from rich import print
from rich.tree import Tree
from rich.console import Console
from io import StringIO



from typing import Union

class DaqConfTree:
    '''
    Class to represent the daq configuration tree.
    '''

    
    def __init__(self, configuration: ConfigurationWrapper | None = None, session: str | None = None):
        ''' Constructor for the DaqConfTree class.'''
        
        self._tree = Tree("[bold red]No Configuration Loaded")        
        self.open_new_session(configuration, session)



    def open_new_session(self, configuration: ConfigurationWrapper, session: str):
        ''' Open a new session.'''
        self._configuration = configuration
        self._session = session
        
        if configuration is not None and session is not None:
            self.generate_tree()
        
        
    def generate_tree(self)->Tree:
        ''' Generate the tree.'''
        # Add the session        
        self._tree = Tree(f"[bold red1] {self._session}")
        
        # We're now going to recurssively loop through relations to session
        session_dal = ca.GetDalObjectAction(self._configuration)(self._session, "Session")        
        
        session_segment = ca.GetAttributeAction(self._configuration)(session_dal, "segment")
        # seg_level_tree = self._tree.add(f"[bold orange]{ca.GetAttributeAction(self._configuration)(session_segment, 'id')}")
        
        self.build_tree(session_segment, self._tree, False)
        return self._tree
    
 
    def get_related_segments(self, segment):
        '''
        Get related segments
        '''
        return ca.GetAttributeAction(self._configuration)(segment, "segments")
        
    def get_related_apps(self, segment):
        '''
        Get related apps
        '''
        return ca.GetAttributeAction(self._configuration)(segment, "applications")
        
    def build_tree(self, segment, tree_branch: Tree, is_disabled: bool = False):
        # Get segmeents
        
        if not self.get_related_segments(segment):
            return 

        if self.get_related_segments(segment):
            segs = tree_branch.add("[bold dark_orange3]Segments")

        for seg in self.get_related_segments(segment):
            
            seg_name = ca.GetAttributeAction(self._configuration)(seg, 'id')
            
            if ca.CheckIsDisabledAction(self._configuration)(seg, self._session) or is_disabled:
                seg_disabled = True
                colour = "grey35"
                message = "DISABLED"

            else:
                seg_disabled = False
                colour = "green"
                message = "ENABLED"


            seg_name = f"[{colour}]{seg_name}   [bold]{message}"            
            seg_branch = segs.add(f"{seg_name}")
            
            
            seg_apps = seg_branch.add("[bold deep_pink4]Applications")
            for app in self.get_related_apps(seg):

                app_name = ca.GetAttributeAction(self._configuration)(app, 'id')

                if ca.CheckIsDisabledAction(self._configuration)(app, self._session) or seg_disabled:
                    colour = "grey35"
                    message = "DISABLED"
                else:
                    colour = "green"
                    message = "ENABLED"

                app_name = f"[{colour}]{app_name}   [bold]{message}"
                
                seg_apps.add(app_name)
        
        return segs

    def print_tree(self):
        ''' Print the tree.'''
        return self._tree
    
