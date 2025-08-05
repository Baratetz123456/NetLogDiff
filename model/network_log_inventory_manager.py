from pathlib import Path
import json
from netmiko import ConnectHandler
from typing import Final, List, Dict

from core.syslogger import logger
from core.constants import Const
from core.utility import Utility

from .sys_config_manager import ConfigManager


class NetworkLogInventoryManager:
    FOLDER_PATH: Final = "data"
    FILENAME: Final = "network_inventory.json"
    RCHBLTY: Final = "Reachability"
    LOG: Final = "Log"
    
    def __init__(self):
        self.__data = {}
        self.file_path = Path(self.FOLDER_PATH) / self.FILENAME
        self.init_import_data()
        
    def init_import_data(self):
        path = Path(self.FOLDER_PATH) / self.FILENAME
        
        if path.exists():
            self.__data = ConfigManager.import_json(self.file_path)
                
        else:
            logger.info("Network log inventory does not exist. New file will be created.")
            ConfigManager.write_json(self.FOLDER_PATH, self.FILENAME, self.__data)
        
    def update(self, hostname:str , column: str, value: bool) -> None:
        self.__data.setdefault(hostname, {})[column] = value
        
    def bulk_update(self, log_result: dict):
        logger.info("Bulk update of network inventory.")
        
        if not (isinstance(log_result, dict) and log_result):
            logger.error(f"Invalid log result found: {log_result}")
            return
        
        for host, columns, in self.__data.items():
            if log_result is None:
                for col, _ in columns.items():
                    if col != self.RCHBLTY and col != self.LOG:
                        self.update(host, col, "-")
            
            else:
                for col, _ in columns.items():
                    if col == self.RCHBLTY or col == self.LOG:
                        continue
                    
                    status = "-"
                    sh_data = log_result.get(host)
                    
                    if sh_data is None:
                        self.update(host, col, status)
                        continue
                        
                    sh_result = sh_data.get(col)
                    
                    if sh_result is not None:
                        status = sh_result.get("status", "-")
                        
                    self.update(host, col, status)
        
        ConfigManager.write_json(self.FOLDER_PATH, self.FILENAME, self.__data)
    
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
    
    def update_log_collection_stats(self, device_log_stats: Dict[str, str]):
        logger.info("Updating log collection status result.")
        
        if isinstance(device_log_stats, dict) and device_log_stats:
            for hostname, status in device_log_stats.items():
                if status:
                    self.update(hostname, self.LOG, True)
                else:
                    self.update(hostname, self.LOG, False)
                    
            ConfigManager.write_json(self.FOLDER_PATH, self.FILENAME, self.__data)
            self.__data = ConfigManager.import_json(self.file_path)
    
    def set_host_default_column_values(self, hostname: str, columns: List[str]) -> None:
        self.__data.setdefault(hostname, {})
        self.__data[hostname].setdefault(self.RCHBLTY, "-")
        self.__data[hostname].setdefault(self.LOG, "-")
        self.__data[hostname].update({cmd: "-" for cmd in columns})
    
    def get_data(self):
        return self.__data
    
    def get_reachable_devices_status(self, device_configs, reachable_devices):
        logger.info("Updating network devices reachability status.")
        
        if not device_configs:
            logger.error("Invalid device configuration parameter.")
            return
        
        for device in device_configs:
            is_reachable = device["hostname"] in reachable_devices
            self.update(device["hostname"], self.RCHBLTY, is_reachable)
            
        ConfigManager.write_json(self.FOLDER_PATH, self.FILENAME, self.__data)
        self.__data = ConfigManager.import_json(self.file_path)
        
    def sync_data(self, hostnames: List[str], show_commands: List[str]) -> None:
        logger.info("Sync network inventory.")
        
        if not(isinstance(hostnames, list) and hostnames):
            logger.warning("No hostnames found.")
            return
        
        if not(isinstance(show_commands, list) and show_commands):
            logger.warning("No show_commands found.")
            return
        
        for hostname in hostnames:
            if hostname not in self.__data:
                self.set_host_default_column_values(hostname, show_commands)
                logger.info(f"{hostname} hostname is added to the table data.")
                
            else:
                # When new show commands columns added
                new_columns = set(show_commands) - set(self.get_host_columns(hostname))
                new_columns_count = len(new_columns)
                
                if new_columns_count:
                    logger.info(f"The number of new columns added to {hostname} is {new_columns_count}.")
                    self.set_host_default_column_values(hostname, new_columns)
                    
        # Update network inventory
        ConfigManager.write_json(self.FOLDER_PATH, self.FILENAME, self.__data)
        
        
    
    
    