import json
from pathlib import Path
from typing import Final, Dict, List

from core.syslogger import logger
from core.timestamp_services import shared_timestamp_service

from .sys_config_manager import ConfigManager


class LogInventoryManager:
    FOLDER_PATH: Final = "data"
    FILENAME: Final = "log_inventory.json"
    
    def __init__(self):
        self.__data = {}
        self.file_path = Path(self.FOLDER_PATH) / self.FILENAME
        self.init_import_data()
        
    def init_import_data(self):
        path = Path(self.FOLDER_PATH) / self.FILENAME
        
        if path.exists():
            self.__data = ConfigManager.import_json(self.file_path)
                
        else:
            logger.info("Log inventory does not exist. New file will be created.")
            ConfigManager.write_json(self.FOLDER_PATH, self.FILENAME, self.__data)
                        
    def update(self, data: dict):
        self.__data = data
        ConfigManager.write_json(self.FOLDER_PATH, self.FILENAME, self.__data)
        
    def __iter__(self):
        return iter(self.__data.items())
    
    def __bool__(self):
        return len(self.__data) > 0
    
    def get_host_log_comparison_result(self, hostname: str):
        return self.__data.get(hostname)
    
    def get_log_data(self):
        return self.__data
    
    def get_export_logs(self) -> Dict[str, str]:
        logger.info("Get logs for export purpose.")
        
        shared_timestamp_service.refresh()
        timestamp_cmp_log = shared_timestamp_service.generate_timestamp()
        logs_to_export = {}
                
        for hostname, cmd_data in self.__data.items():
            for cmd, data in cmd_data.items():
                output = data.get("text_log_output")
                
                if output is None or not output:
                    logger.error(f"No logs to export for {cmd} from {hostname}.")
                    continue
                
                export_output = "\n".join(output)
                
                # Construct filename with timestamp
                filename = f"{hostname}_{cmd}_{timestamp_cmp_log}.log"
                path = Path(hostname) / filename
                
                logs_to_export.setdefault(hostname, {}).update({path: export_output})
                
        return logs_to_export