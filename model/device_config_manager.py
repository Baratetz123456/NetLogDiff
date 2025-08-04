import pandas as pd
import re
from pathlib import Path
from typing import Dict, List, Final

from core.syslogger import logger
from core.constants import Const
from core.utility import Utility


class DeviceConfigManager:
    imported_commands  = {}
    CONFIG_FILE: Final = "config/config.csv"
    DEFAULT_FOLDER_PATH: Final = "commands"

    def __init__(self):
        self.__data: List[Dict[str, str]] = []
        self.hostname_with_commands = {}

        self.import_config()
        self.get_hostname_with_commands()
        
    def __iter__(self):
        return iter(self.__data)

    def __len__(self):
        return len(self.__data)

    def __bool__(self):
        return len(self.__data) > 0

    def __contains__(self, item):
        return any(x.get("hostname") == item for x in self.__data)
    
    def get_hostname_with_commands(self) -> None:
        """
        Get the show commands of every hostname listed in the
        network device configuration.
        """
        logger.info("Importing show commands for devices.")

        for x in self.__data:
            commands: List[str] = self.import_commands(x["show_commands"])

            if not commands:
                logger.warning(f"No show commands found for hostname: {x["hostname"]}")
                continue
            
            self.hostname_with_commands.update({x["hostname"]: commands})

        logger.info(
            f"Number of network devices with show commands imported: {len(self.hostname_with_commands)}"
        )

    def import_commands(self, filename: str):
        logger.info(f"Importing network device show commands from: {filename}")        
        commands = []
        
        if filename in self.imported_commands:
            return self.imported_commands[filename]
        
        try:
            path = Utility.resource_path(Path(self.DEFAULT_FOLDER_PATH) / filename)
            
            with open(path, mode="r") as file:
                commands = file.readlines()
                commands = [x.strip() for x in commands]
            
            self.imported_commands.update({filename: commands})
            
        except Exception as e:
            logger.error(e)
            raise(e)
        
        return commands
            
    def import_config(self) -> None:
        expected_headers = ["hostname", "ipaddress", "username", "password", "admin_password", "device_os", "connection_type", "skip", "show_commands"]
        path = Utility.resource_path(self.CONFIG_FILE)
        
        try:
            df = pd.read_csv(path, encoding="utf-8-sig")
            actual_headers = df.columns.to_list()
            
            # Validate headers presence
            if actual_headers is None:
                raise ValueError("The network device configuration file is empty. No headers found.")
            
            # Normalize headers for comparison
            actual_headers_lower = [h.lower().strip() for h in actual_headers]
            
            missing = set(expected_headers) - set(actual_headers_lower)
            extra = set(actual_headers_lower) - set(expected_headers)

            if missing or extra:
                message = (
                    "The configuration table headers don't match the required format.\n"
                    f"Missing headers: {missing}\n"
                    f"Unexpected headers: {extra}\n"
                    f"Expected: {expected_headers}\n"
                    f"Found: {actual_headers}"
                )
                raise ValueError(message)
            
            records = df.to_dict(orient="records")
            
            if not records:
                raise ValueError("No target network device available.")
            
            # Collect not skipped network devices
            for row in records:
                row = self.clean_data(row)
                
                if self.is_device_skipped(row):
                    continue
                
                self.__data.append(row)
                
        except Exception as e:
            logger.error(f"Error encountered during import: {e}")
            raise
                
    def is_device_skipped(self, data):
        value = data.get("skip", "").upper()
        return value == "TRUE"        
        
    def clean_data(self, data: Dict[str, str]):
        return {k.strip(): str(v).strip() for k, v in data.items()}
    
    def get_show_commands(self, hostname: str=None) -> List[str]:
        commands = []
        
        if hostname is not None:
            return self.hostname_with_commands.get(hostname)
        
        _ = list(map(lambda x: commands.extend(x), self.hostname_with_commands.values()))
        
        return list(set(commands))
    
    def filter_hosts_with_commands(self, hosts: Dict[str, str]):
        return dict(filter(lambda x: x[0] in self.hostname_with_commands, hosts.items()))
    
    def has_hostnames_with_commands(self):
        return bool(self.hostname_with_commands)
    
    def get_hostnames(self):
        return list(map(lambda x: x["hostname"], self.__data))