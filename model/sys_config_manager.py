import json
from typing import Final
from core.syslogger import logger
from core.utility import resource_path

class SystemConfigManager:
    SYS_CONFIG_PATH: Final = "config/sys_config.json"
    def __init__(self):
        self.__data = {}
        self.fetch()
    
    def get_title(self) -> str:
        return self.__data.get("window_title")
    
    def get_window_dimensions(self) -> tuple:
        height = self.__data.get("window_height")
        width = self.__data.get("window_width")
        
        return width, height
    
    def get_icon_path(self) -> str:
        return self.__data.get("icon_path")
    
    def reset_data(self):
        self.__data = {}
        
    def fetch(self):
        logger.info("Importing system configurations.")
        
        try:
            path = resource_path(self.SYS_CONFIG_PATH)
            
            with open(path, mode="r", encoding="utf-8") as file:
                self.__data = json.load(file)
                logger.info("System configuration imported successfully.")
                
        except Exception as e:
            logger.error(f"Error occured during import: {e}")
            self.reset_data()
            
    def write(self):
        try:
            
            with open(self.SYS_CONFIG_PATH, mode="w", encoding="utf-8") as file:
                json.dump(self.__data, file, indent=4)
            
            logger.info("System configuration exported successfully.")
            return True
        
        except Exception as e:
            logger.error(f"Error occured during export: {e}")
            return False
    