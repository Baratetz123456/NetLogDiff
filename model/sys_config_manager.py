import json
import pandas as pd
from pathlib import Path
from typing import Final, List, Dict, Any, Optional


from core.syslogger import logger
from core.utility import Utility


class SystemConfigManager:
    SYS_CONFIG_PATH: Final = "config/sys_config.json"

    def __init__(self):
        """Initialize and load system configuration."""
        self.__data = ConfigManager.import_json(self.SYS_CONFIG_PATH)

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
        return self.__data.get("icon_path", "icon/technology.ico")


class ConfigManager:
    @classmethod
    def import_json(cls, path: str) -> Dict:
        """Import a JSON file into a dictionary."""
        logger.debug(f"Attempting to import JSON file from {path}")
        output = None

        try:
            path = Utility.resource_path(path)

            with open(path, mode="r", encoding="utf-8") as file:
                output = json.load(file)

            logger.info(f"Successfully imported JSON file from {path}")

        except FileNotFoundError:
            logger.error(f"File not found: {path}")

        except json.JSONDecodeError as e:
            logger.error(f"JSON decoding error in {path}: {e}")

        except Exception as e:
            logger.error(f"An error occurred during JSON import from {path}: {e}")

        return output

    @classmethod
    def write_json(cls, folder_path: str, filename: str, value: Any) -> bool:
        """Write a JSON object to a file."""
        logger.debug(f"Attempting to write JSON file to {folder_path}/{filename}")

        try:
            if not Utility.create_directory(folder_path):
                raise OSError(f"Failed to create directory: {folder_path}")

            path = Path(folder_path) / filename

            with open(path, mode="w", encoding="utf-8") as file:
                json.dump(value, file, indent=4)

            logger.info(f"Successfully wrote JSON file to {path}")
            return True

        except OSError as e:
            logger.error(f"Directory creation failed: {e}")

        except Exception as e:
            logger.error(
                f"An error occurred while writing to {folder_path}/{filename}: {e}"
            )

        return False

    @classmethod
    def import_file(cls, path: str) -> str:
        """Import a file as a string."""
        logger.debug(f"Attempting to import file from {path}")
        output = None

        try:
            path = Path(path)

            with open(path, mode="r", encoding="utf-8") as file:
                output = file.read()

            logger.info(f"Successfully imported file from {path}")

        except Exception as e:
            logger.error(f"Error occurred while importing file {path}: {e}")

        return output

    @classmethod
    def import_file_by_lines(cls, path: str) -> List[str]:
        """Import a file and return its lines as a list of strings."""
        logger.debug(f"Attempting to import file by lines from {path}")
        output = None

        try:
            path = Path(path)

            with open(path, mode="r", encoding="utf-8") as file:
                output = [line.strip() for line in file.readlines()]

            logger.info(f"Successfully imported file by lines from {path}")

        except Exception as e:
            logger.error(f"Error occurred while importing file by lines {path}: {e}")

        return output

    @classmethod
    def import_logs(
        cls, folder_path: str, filenames: List[str]
    ) -> Dict[str, List[str]]:
        """Import logs from a list of filenames and return them as a dictionary."""
        logger.debug(
            f"Attempting to import logs from {len(filenames)} files in {folder_path}"
        )
        host_with_logs = {}

        for filename in filenames:
            try:
                hostname = Utility.extract_hostname(filename)
                path = Path(folder_path) / filename
                data = cls.import_file(str(path))

                if data:
                    host_with_logs[hostname] = data

                logger.debug(f"Imported logs for {hostname} from {filename}")

            except Exception as e:
                logger.error(f"Error processing log file {filename}: {e}")

        logger.info(f"Imported logs for {len(host_with_logs)} hosts")

        return host_with_logs

    @classmethod
    def import_csv(cls, path: str) -> Optional[pd.DataFrame]:
        """Import a CSV file and return as dataframe. Returns None if failed."""
        logger.debug(f"Attempting to import CSV file from {path}")

        try:
            path = Path(path)

            # Ensure the file exists before attempting to read
            if not path.exists():
                logger.error(f"CSV file not found at {path}")
                return None

            # Read the CSV into a pandas DataFrame
            output = pd.read_csv(path, encoding="utf-8-sig")

            if output.empty:
                logger.warning(f"CSV file at {path} is empty.")
                return pd.DataFrame()  # Return an empty DataFrame instead of None

            logger.info(f"Successfully imported CSV file from {path}")
            return output

        except FileNotFoundError:
            logger.error(f"CSV file not found: {path}")

        except pd.errors.EmptyDataError:
            logger.error(f"CSV file is empty: {path}")

        except pd.errors.ParserError as e:
            logger.error(f"Error parsing CSV file {path}: {e}")

        except Exception as e:
            logger.error(f"An error occurred while importing CSV file {path}: {e}")

        return None
