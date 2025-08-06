import pandas as pd
import re
from pathlib import Path
from typing import Dict, List, Final, Union, Optional

from core.syslogger import logger
from core.constants import Const
from core.utility import Utility
from .sys_config_manager import ConfigManager


class DeviceConfigManager:
    imported_commands = {}
    CONFIG_FILE: Final = "config/config.csv"
    DEFAULT_FOLDER_PATH: Final = "commands"

    def __init__(self):
        self.__data: List[Dict[str, str]] = []
        self.hostname_with_commands = {}

        # Initialize configuration and commands
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
        Get the show commands for every hostname listed in the network device configuration.
        """
        logger.info("Importing show commands for devices.")

        for device in self.__data:
            hostname = device.get("hostname")
            show_commands = device.get("show_commands")
            
            if not hostname or not show_commands:
                logger.warning(f"Missing 'hostname' or 'show_commands' for device: {device}")
                continue

            # Import and assign commands
            commands = self.import_commands(show_commands)

            if not commands:
                logger.warning(f"No show commands found for hostname: {hostname}")
                continue

            self.hostname_with_commands[hostname] = commands

        logger.info(f"Number of network devices with show commands imported: {len(self.hostname_with_commands)}")

    def import_commands(self, filename: str) -> Union[List[str], str, None]:
        """
        Import network device show commands from a file and return them.
        Returns cached commands if already imported.

        :param filename: The name of the command file to import.
        :return: List of commands, empty string, or None.
        """
        logger.info(f"Importing network device show commands from: {filename}")

        # Return cached commands if already imported
        if filename in self.imported_commands:
            logger.debug(f"Commands for {filename} already imported. Returning cached data.")
            return self.imported_commands[filename]

        path = Path(self.DEFAULT_FOLDER_PATH) / filename

        try:
            # Attempt to read the file and cache the commands
            commands = ConfigManager.import_file_by_lines(path)

            if not commands:
                logger.warning(f"No commands found in {filename}. Returning empty list.")
                commands = []  # Return an empty list if no commands are found

            # Cache the imported commands for future use
            self.imported_commands[filename] = commands
            logger.info(f"Successfully imported commands from {filename}.")

            return commands

        except FileNotFoundError:
            logger.error(f"File not found: {filename}.")
            
        except IOError as e:
            logger.error(f"Error reading the file {filename}: {e}")
            
        except Exception as e:
            logger.error(f"Unexpected error encountered during import of {filename}: {e}")

        return None

    def import_config(self) -> None:
        """Import network device configuration from a CSV file and process records."""
        
        try:
            # Import configuration CSV file
            config_file = ConfigManager.import_csv(self.CONFIG_FILE)
            
            # Check if the file was not found or is empty
            if config_file is None or config_file.empty:
                raise ValueError("The network device configuration file is not found or is empty.")

            actual_headers = config_file.columns.to_list()

            # Validate headers presence
            if not actual_headers:
                raise ValueError("The network device configuration file has no headers.")
            
            # Validate headers against expected headers
            self.validate_headers(actual_headers)

            # Process records and collect non-skipped devices
            records = config_file.to_dict(orient="records")

            if not records:
                raise ValueError("No target network device records found in the configuration file.")

            # Collect devices that are not skipped
            devices_processed = 0
            
            for row in records:
                row = self.clean_data(row)

                if self.is_device_skipped(row):
                    continue

                self.__data.append(row)
                devices_processed += 1

            logger.info(f"Successfully processed {devices_processed} network devices.")
            
        except ValueError as ve:
            logger.error(f"ValueError encountered during import: {ve}")
            raise
        
        except FileNotFoundError as fnfe:
            logger.error(f"FileNotFoundError: Configuration file {self.CONFIG_FILE} not found.")
            raise fnfe
        
        except Exception as e:
            logger.error(f"Unexpected error encountered during import: {e}")
            raise

    def is_device_skipped(self, data: Dict[str, str]) -> bool:
        """Check if the device is marked as skipped."""
        return data.get("skip", "").upper() == "TRUE"

    def clean_data(self, data: Dict[str, str]) -> Dict[str, str]:
        """
        Clean the input dictionary by stripping whitespace from both the keys and values.
        
        :param data: A dictionary with string keys and values.
        :return: A cleaned dictionary with stripped keys and values.
        """
        if not isinstance(data, dict):
            raise ValueError("Input must be a dictionary.")
        
        return {k.strip(): str(v).strip() if v is not None else "" for k, v in data.items()}

    def get_show_commands(self, hostname: Optional[str] = None) -> List[str]:
        """
        Get the list of show commands for a specific hostname or all hostnames.
        
        :param hostname: The hostname to filter the commands (optional).
        :return: A list of commands.
        """
        if hostname:
            # Return commands for the specified hostname if it exists
            return self.hostname_with_commands.get(hostname, [])

        # Collect all commands from all hostnames
        commands = []
        
        for host_commands in self.hostname_with_commands.values():
            commands.extend(host_commands)

        # Remove duplicates
        return list(dict.fromkeys(sorted(commands)))

    def filter_hosts_with_commands(self, hosts_to_check: Dict[str, str]) -> Dict[str, str]:
        """
        Filter the given dictionary of hosts to include only those that have commands defined.
        
        :param hosts_to_check: Dictionary of hosts to check.
        :return: A filtered dictionary of hosts that have associated commands.
        """
        return {host: ip for host, ip in hosts_to_check.items() if host in self.hostname_with_commands}

    def has_hostnames_with_commands(self) -> bool:
        """
        Check if there are any hostnames with commands in the class.
        
        :return: True if there are hostnames with commands, False otherwise.
        """
        return bool(self.hostname_with_commands)

    def get_hostnames(self) -> List[str]:
        """
        Retrieve the list of hostnames from the data.

        :return: A list of hostnames.
        """
        return [entry["hostname"] for entry in self.__data if "hostname" in entry]

    def validate_headers(self, actual_headers: List[str]) -> None:
        """Validate if headers in the CSV match the expected headers."""
        expected_headers = [
            "hostname",
            "ipaddress",
            "username",
            "password",
            "admin_password",
            "device_os",
            "connection_type",
            "skip",
            "show_commands",
        ]

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
