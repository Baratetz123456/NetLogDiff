import json
from pathlib import Path
from typing import Final

from core.syslogger import logger
from model.file_manager import FileManager

class TimestampManager:
    FOLDER_PATH: Final = "data"
    FILENAME: Final = "execution_timestamps.json"
    LOG_COLL: Final = "log collection"
    LOG_COMP: Final = "log comparison"
    
    def __init__(self):
        self.__data = {self.LOG_COLL: None, self.LOG_COMP: None}
        self.init_import_data()
                
    @property
    def log_collection_timestamp(self):
        return self.__data.get(self.LOG_COLL, None)
    
    @property
    def log_comparison_timestamp(self):
        return self.__data.get(self.LOG_COMP, None)
    
    def init_import_data(self):
        path = Path(self.FOLDER_PATH) / self.FILENAME
        
        if path.exists():
            self.fetch()
                
        else:
            logger.info("Timestamp does not exist. New file will be created.")
            self.write()
    
    def reset_timestamp(self):
        self.__data = {self.LOG_COLL: None, self.LOG_COMP: None}
        
    def update_log_collection_timestamp(self, timestamp: str):
        self.__update_timestamp(self.LOG_COLL, timestamp)
    
    def update_log_comparison_timestamp(self, timestamp: str):
        self.__update_timestamp(self.LOG_COMP, timestamp)
        
    def __update_timestamp(self, key: str, timestamp: str):
        if isinstance(timestamp, str):
            self.__data[key] = timestamp
            self.write()
            
        else:
            logger.error(f"Invalid timestamp for {key}.")
            
    def fetch(self):
        try:
            # Construct the full path
            path = Path(self.FOLDER_PATH) / self.FILENAME
            
            with open(path, mode="r", encoding="utf-8") as file:
                self.__data = json.load(file)
                logger.info("Exection timestamps successfully imported.")
                
        except Exception as e:
            logger.error(f"Error occured: {e}")
            self.reset_timestamp()
            
    def write(self) -> bool:
        try:
            if not FileManager.create_directory(self.FOLDER_PATH):
                raise OSError(f"Failed to create directory: {self.FOLDER_PATH}")

            path = Path(self.FOLDER_PATH) / self.FILENAME
            
            with open(path, mode="w", encoding="utf-8") as file:
                json.dump(self.__data, file, indent=4)
            
            logger.info("Execution timestmaps has been successfully updated.")
            return True
        
        except Exception as e:
            logger.error(f"Execution timestamps error occured: {e}")
            return False
    
    def __str__(self):
        return (
            f"Log collection timestamp: {self.log_collection_timestamp}\n"
            f"Log comparison timestamp: {self.log_comparison_timestamp}\n"
        )
            