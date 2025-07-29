import json
from pathlib import Path
from typing import Final, Dict, List

from core.syslogger import logger
from core.constants import Const
from core.utility import resource_path
from core.timestamp_services import shared_timestamp_service

from model.file_manager import FileManager


class LogInventoryManager:
    FOLDER_PATH: Final = "data"
    FILENAME: Final = "log_inventory.json"
    
    def __init__(self):
        self.__data = {}
        self.fetch()
    
    def reset_data(self):
        self.__data = {}
        
    def fetch(self):
        logger.info("Importing log inventory data.")
        
        try:
            path = Path(self.FOLDER_PATH) / self.FILENAME
            
            with open(path, mode="r", encoding="utf-8") as file:
                self.__data = json.load(file)
                logger.info("Log inventory data successfully imported.")
                
        except Exception as e:
            logger.error(f"Error encountered during import: {e}")
            self.reset_data()
    
    def write(self):
        try:
            if not FileManager.create_directory(self.FOLDER_PATH):
                raise OSError(f"Failed to created directory: {self.FOLDER_PATH}")
            
            path = Path(self.FOLDER_PATH) / self.FILENAME
            
            with open(path, mode="w", encoding="utf-8") as file:
                json.dump(self.__data, file, indent=4)
                
            logger.info("Log inventory has been successfully updated.")
            return True
        
        except Exception as e:
            logger.error(f"Error encountered: {e}")
            return False
    
    def update(self, data: dict):
        self.__data = data
        
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