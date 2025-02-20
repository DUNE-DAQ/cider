'''
Simple wrapper for talking to config-management
'''

from config_management.ConfPool import ConfPool
import os

class ManagementInterface:
    def __init__(self, path, base="ssh://git@gitlab.cern.ch:7999/dune-daq/online/ehn1-daqconfigs.git",
                 operation="ssh://git@gitlab.cern.ch:7999/dune-daq/online/np02-configs-operation.git",
                 release = os.environ["SPACK_RELEASE"]
                ) -> None:

        self._pool = ConfPool(path, operation_url=operation, base_url=base)
        self._release = release        
        
    def get_base_branches(self):
        return self._pool.get_daq_versions()

    def get_configs(self):
        return self._pool.get_configs()
    
    def checkout_conf(self, config):
        self._pool.checkout_conf(config)
        
    