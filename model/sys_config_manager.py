import json
import pandas as pd
from pathlib import Path
from typing import Final, List, Dict, Any, Optional, Union


from core.syslogger import logger
from core.utility import Utility


class SystemConfigManager:
    SYS_CONFIG_PATH: Final = "config/sys_config.json"

    def __init__(self):
        """Initialize and load system configuration."""
        self.__data = ConfigManager.import_json(self.SYS_CONFIG_PATH, temp_data=False)

        if not self.__data:
            raise ValueError(
                f"Configuration file {self.SYS_CONFIG_PATH} could not be loaded."
            )

    def get_title(self) -> str:
        """Get the window title from the configuration."""
        return self.__data.get("window_title", "Default Title")

    def get_window_dimensions(self) -> tuple[int, int]:
        """Get window dimensions (width, height)."""
        height = self.__data.get("window_height", 800)
        width = self.__data.get("window_width", 1700)

        return width, height

    def get_icon_path(self) -> str:
        """Get the icon path from the configuration."""
        return Utility.resource_path(self.__data.get("icon_path", "icon/technology.ico"))


class ConfigManager:
    @classmethod
    def import_json(cls, path: Union[str, Path], temp_data: bool=True) -> Dict:
        """Import a JSON file into a dictionary."""
        if temp_data:
            path = Path(path)
        else:
            path = Utility.resource_path(path)
            
        logger.debug(f"Attempting to import JSON file from {path}")
        
        try:
            content = path.read_text(encoding="utf-8")
            data = json.loads(content)
            logger.info(f"Successfully imported JSON file from {path}")
            return data
        
        except FileNotFoundError:
            logger.error(f"File not found: {path}")
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decoding error in {path}: {e}")
            
        except Exception as e:
            logger.error(f"An error occurred during JSON import from {path}: {e}")
            
        return {}

    @classmethod
    def write_json(cls, folder_path: Union[str, Path], filename: str, value: Any) -> bool:
        """Write a JSON object to a file."""
        folder = Path(folder_path)
        logger.debug(f"Attempting to write JSON file to {folder / filename}")

        try:
            if not Utility.create_directory(folder):
                raise OSError(f"Failed to create directory: {folder}")

            file_path = folder / filename
            file_path.write_text(json.dumps(value, indent=4), encoding="utf-8")
            logger.info(f"Successfully wrote JSON file to {file_path}")
            return True
        
        except Exception as e:
            logger.error(f"An error occurred while writing JSON to {file_path}: {e}")
            return False

    @classmethod
    def import_file(cls, path: Union[str, Path]) -> Optional[str]:
        """Import a file as a string."""
        path = Path(path)
        logger.debug(f"Attempting to import file from {path}")
        
        try:
            return path.read_text(encoding="utf-8")
        
        except Exception as e:
            logger.error(f"Error occurred while importing file {path}: {e}")
            return None

    @classmethod
    def import_file_by_lines(cls, path: Union[str, Path]) -> List[str]:
        """Import a file and return its lines as a list of strings."""
        path = Utility.resource_path(path)
        logger.debug(f"Attempting to import file by lines from {path}")
        
        try:
            return path.read_text(encoding="utf-8").splitlines()
        
        except Exception as e:
            logger.error(f"Error occurred while importing file lines from {path}: {e}")
            return []

    @classmethod
    def import_logs(cls, folder_path: Union[str, Path], filenames: List[str]) -> Dict[str, List[str]]:
        """Import logs from a list of filenames and return them as a dictionary."""
        folder = Path(folder_path)
        logger.debug(f"Attempting to import logs from {len(filenames)} files in {folder}")
        host_with_logs = {}

        for filename in filenames:
            try:
                hostname = Utility.extract_hostname(filename)
                data = cls.import_file(folder / filename)
                
                if data:
                    host_with_logs[hostname] = data
                logger.debug(f"Imported logs for {hostname} from {filename}")
                
            except Exception as e:
                logger.error(f"Error processing log file {filename}: {e}")

        logger.info(f"Imported logs for {len(host_with_logs)} hosts")
        return host_with_logs

    @classmethod
    def import_csv(cls, path: Union[str, Path]) -> Optional[pd.DataFrame]:
        """Import a CSV file and return as DataFrame. Returns None if failed."""
        path = Utility.resource_path(path)
        logger.debug(f"Attempting to import CSV file from {path}")

        try:
            if not path.exists():
                logger.error(f"CSV file not found at {path}")
                return None

            df = pd.read_csv(path, encoding="utf-8-sig")

            if df.empty:
                logger.warning(f"CSV file at {path} is empty.")
                return pd.DataFrame()

            logger.info(f"Successfully imported CSV file from {path}")
            return df

        except FileNotFoundError:
            logger.error(f"CSV file not found: {path}")
            
        except pd.errors.EmptyDataError:
            logger.error(f"CSV file is empty: {path}")
            
        except pd.errors.ParserError as e:
            logger.error(f"Error parsing CSV file {path}: {e}")
            
        except Exception as e:
            logger.error(f"An error occurred while importing CSV file {path}: {e}")

        return None
