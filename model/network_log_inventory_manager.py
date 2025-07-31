from pathlib import Path
import json
from netmiko import ConnectHandler
from typing import Final, List, Dict

from core.syslogger import logger
from core.constants import Const
from model.file_manager import FileManager

class NetworkLogInventoryManager:
    FOLDER_PATH: Final = "data"
    FILENAME: Final = "network_inventory.json"
    RCHBLTY: Final = "Reachability"
    LOG: Final = "Log"
    
    def __init__(self):
        self.__data = {}
        self.init_import_data()
        
    def init_import_data(self):
        path = Path(self.FOLDER_PATH) / self.FILENAME
        
        if path.exists():
            self.fetch()
                
        else:
            logger.info("Network log inventory does not exist. New file will be created.")
            self.write()
        
    def fetch(self):
        logger.info("Importing data for table.")
        
        try:            
            path = Path(self.FOLDER_PATH) / self.FILENAME
            
            with open(path, mode="r", encoding="utf-8") as file:
                self.__data = json.load(file)
                logger.info("Table data successfuly imported.")
                
        except Exception as e:
            logger.error(f"Unexpected error during import: {e}")
            self.reset_data()
    
    def update(self, hostname:str , column: str, value: bool) -> None:
        self.__data.setdefault(hostname, {})[column] = value
    
    def write(self):
        try:
            if not FileManager.create_directory(self.FOLDER_PATH):
                raise OSError(f"Failed to created directory: {self.FOLDER_PATH}")
            
            path = Path(self.FOLDER_PATH) / self.FILENAME
            
            with open(path, mode="w", encoding="utf-8") as file:
                json.dump(self.__data, file, indent=4)
                
            logger.info("Network inventory has been successfully updated.")
            return True
        
        except Exception as e:
            logger.error(f"Error encountered: {e}")
            return False
    
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
                    sh_data = log_result.get(col)
                    
                    if sh_data is not None:
                        status = sh_data.get("status", "-")
                        
                    self.update(host, col, status)
                    
        self.write()
    
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
    
    def update_log_collection_stats(self, device_log_stats: Dict[str, str]):
        if isinstance(device_log_stats, dict) and device_log_stats:
            for hostname, status in device_log_stats.items():
                if status:
                    self.update(hostname, self.LOG, True)
                else:
                    self.update(hostname, self.LOG, False)
                    
            self.write()
            self.fetch()
                
    def filter_reachable_devices(self, device_configs):
        reachable_devices_config = []
        
        for device in device_configs:
            hostname = device["hostname"]
            reachability_status = self.get_reachability_status(hostname)
            
            if not (isinstance(reachability_status, bool) and reachability_status):
                logger.warning(f"[SKIPPED] Hostname [{hostname}] is unreachable.")
                self.update(hostname, self.LOG, False)
                continue
            
            reachable_devices_config.append(device)
        
        return reachable_devices_config
    
    def get_reachability_status(self, hostname):
        host_data = self.__data.get(hostname)
        
        if host_data is not None:
            return host_data.get(self.RCHBLTY)
    
    def set_host_default_column_values(self, hostname: str, columns: List[str]) -> None:
        self.__data.setdefault(hostname, {})
        self.__data[hostname].setdefault(self.RCHBLTY, "-")
        self.__data[hostname].setdefault(self.LOG, "-")
        self.__data[hostname].update({cmd: "-" for cmd in columns})
    
    def get_data(self):
        return self.__data
    
    def validate_devices_reachability(self, device_configs):
        if not device_configs:
            logger.error("Invalid device configuration parameter.")
            return
        
        for device in device_configs:
            config = device_configs.create_configuration(device)
            
            is_reachable = self._check_device_reachability(config)
            logger.info(f"Hostname: {device['hostname']} is {'reachable' if is_reachable else 'not reachable'}.")
            self.update(device["hostname"], self.RCHBLTY, is_reachable)
            
        self.write()
        self.fetch()
    
    def _check_device_reachability(self, config):
        try:
            net_connect = ConnectHandler(**config)
            net_connect.enable()
            net_connect.disconnect()
            return True
        
        except Exception as e:
            logger.error(f"COnnection faield: {e}")
            return False
    
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
        self.write()
        
        
    
    
    