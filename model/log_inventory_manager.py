import json
from pathlib import Path
from typing import Final

from core.syslogger import logger
from core.constants import Const
from core.utility import resource_path

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
        