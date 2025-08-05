import json
from pathlib import Path
from typing import Final

from core.syslogger import logger
from core.utility import Utility
from .sys_config_manager import ConfigManager

class TimestampManager:
    FOLDER_PATH: Final = "data"
    FILENAME: Final = "execution_timestamps.json"
    LOG_COLL: Final = "log collection"
    LOG_COMP: Final = "log comparison"
    
    def __init__(self):
        self.__data = {self.LOG_COLL: None, self.LOG_COMP: None}
        self.file_path = Path(self.FOLDER_PATH) / self.FILENAME
        self.init_import_data()
                
    @property
    def log_collection_timestamp(self):
        return self.__data.get(self.LOG_COLL, None)
    
    @property
    def log_comparison_timestamp(self):
        return self.__data.get(self.LOG_COMP, None)
    
    def init_import_data(self):
        if self.file_path.exists():
            self.__data = ConfigManager.import_json(self.file_path)
                
        else:
            logger.info("Timestamp does not exist. New file will be created.")
            ConfigManager.write_json(self.FOLDER_PATH, self.FILENAME, self.__data)
        
    def update_log_collection_timestamp(self, timestamp: str):
        self.__update_timestamp(self.LOG_COLL, timestamp)
    
    def update_log_comparison_timestamp(self, timestamp: str):
        self.__update_timestamp(self.LOG_COMP, timestamp)
        
    def __update_timestamp(self, key: str, timestamp: str):
        if isinstance(timestamp, str):
            self.__data[key] = timestamp
            ConfigManager.write_json(self.FOLDER_PATH, self.FILENAME, self.__data)
            
        else:
            logger.error(f"Invalid timestamp for {key}.")
                
    def __str__(self):
        return (
            f"Log collection timestamp: {self.log_collection_timestamp}\n"
            f"Log comparison timestamp: {self.log_comparison_timestamp}\n"
        )
            