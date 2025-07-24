import pathlib
import json
from netmiko import ConnectHandler
from typing import Final, List, Dict

class NetworkLogInventoryManager:
    FOLDER_PATH: Final = "data"
    FILENAME: Final = "network_inventory.json"
    RCHBLTY: Final = "Reachability"
    LOG: Final = "Log"
    
    def __init__(self):
        self.__data = {}
        self.fetch()
        
    def fetch(self):
        pass
    
    def update(self):
        pass
    
    def write(self):
        pass
    
    def bulk_update(self, log_inventory):
        pass
    
    def reset_data(self):
        self.__data = {}
        
    def __iter__(self):
        return iter(self.__data)
    
    def __setitem__(self, key, value):
        self.__data[key] = value
        
    def __contains__(self, value):
        return value in self.__data
    
    def get_hostnames(self):
        return list(self.__data.keys())
    
    def get_host_columns(self, hostname: str) -> List[str]:
        columns = self.__data.get(hostname)
        
        if columns is not None:
            return list(columns.keys())
        
        return None
    
    def update_log_collection_stats(self):
        pass
    
    def filter_reachable_devices(self):
        pass
    
    def get_reachability_status(self, hostname):
        pass
    
    def set_host_default_column_values(self):
        pass
    
    def get_data(self):
        return self.__data
    
    def validate_devices_reachability(self, device_configs):
        pass
    
    def _check_device_reachability(self, config):
        pass
    
    def sync_data(self):
        pass
    
    
    