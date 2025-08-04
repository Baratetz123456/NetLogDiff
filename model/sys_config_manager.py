import json
from pathlib import Path
from typing import Final, List, Dict, Any

from core.syslogger import logger
from core.utility import Utility

class SystemConfigManager:
    SYS_CONFIG_PATH: Final = "config/sys_config.json"
    
    def __init__(self):
        self.__data = ConfigManager.import_json(self.SYS_CONFIG_PATH)
            
    def get_title(self) -> str:
        return self.__data.get("window_title")
    
    def get_window_dimensions(self) -> tuple:
        height = self.__data.get("window_height")
        width = self.__data.get("window_width")
        
        return width, height
    
    def get_icon_path(self) -> str:
        return self.__data.get("icon_path")
    
        
class ConfigManager:
    def __init__(self):
        pass
    
    @classmethod
    def import_json(cls, path: str) -> dict:
        logger.info(f"Importing JSON file from {path}")
        output = None
        
        try:
            path = Utility.resource_path(path)
            
            with open(path, mode="r", encoding="utf-8") as file:
                output = json.load(file)
                logger.info("JSON file imported successfully.")
                
        except Exception as e:
            logger.error(f"Error occured during import: {e}")
        
        return output
    
    @classmethod
    def write_json(cls, folder_path: str, filename: str, value: Any) -> bool:
        logger.info(f"Writing JSON file into {folder_path}")
        
        try:
            if not Utility.create_directory(folder_path):
                raise OSError(f"Failed to created directory: {folder_path}")
            
            path = Path(folder_path) / filename
            
            with open(path, mode="w", encoding="utf-8") as file:
                json.dump(value, file, indent=4)
                
            logger.info("JSON file written successfully.")
            return True
        
        except Exception as e:
            logger.error(f"Error occured during writing JSON file: {e}")
            return False
    
    @classmethod
    def import_file(cls, path: str) -> str:
        logger.info(f"Importing file from {path}")
        
        path = Path(path)
        output = None
            
        try:
            with open(path, mode="r") as file:
                output = file.read()
                
        except Exception as e:
            logger.error(f"Error occured during file import: {e}")
        
        return output
    
    @classmethod
    def import_logs(cls, folder_path: str, filenames: List[str]) -> Dict[str, List[str]]:
        logger.info("Importing log files.")
        logger.info(f"Number of files to import: {len(filenames)}")
        
        host_with_logs = {}
        
        for filename in filenames:
            hostname = Utility.extract_hostname(filename)
            path = Path(folder_path) / filename
            
            data = cls.import_file(path)
            
            if data is not None:
                host_with_logs.update({hostname: data})
                
        return host_with_logs