"""
Simple wrapper for talking to config-management
"""

from config_management.ConfPool import ConfPool
from cider.utils.shifter_config_reader import ShifterConfigReader
from cider.utils.config_path_reader import ConfigPathReader

import re
from abc import ABC, abstractmethod

class ManagementInterface(ABC):
    def __init__(self, interface_config):
        self._interface_config = interface_config

    @property
    def interface_config(self):
        return self._interface_config

    @abstractmethod
    def get_confs(self):
        pass
    

class RemoteManagementInterface(ManagementInterface):
    '''
    Interface to the remote configuration management system
    '''
    def __init__(self, interface_config: ShifterConfigReader, apparatus: str) -> None:
        super().__init__(interface_config)

        self._pool = ConfPool(interface_config.download_directory,
                              apparatus=apparatus,
                              operation_url=interface_config.operation_url,
                              base_url=interface_config.base_url)
            
        self._release = None
        self._release_str = None

    def get_config_version(self):
        return self._pool.get_daq_versions()

    @property
    def release(self) -> re.Pattern | None:
        return self._release

    @release.setter
    def release(self, release: str | None) -> None:
        if release is None:
            self._release = None
            return

        self._release_str = release
        self._release = re.compile(release)

    def get_confs(self):
        if self._release is None:
            return []
        return self._pool.get_confs(self._release)

    def checkout_conf(self, config):
        if self._release is None:
            return None
        self._pool.checkout_conf(config, str(self._release_str))

class LocalManagementInterfcae(ManagementInterface):
    '''
    Interface to the local configuration management system
    '''
    def __init__(self, interface_config: ShifterConfigReader) -> None:
        super().__init__(interface_config)

    def get_confs(self):
        return ConfigPathReader()(self.interface_config.config_directories)
    