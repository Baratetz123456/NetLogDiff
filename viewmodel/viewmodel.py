import tkinter as tk
from pathlib import Path
from typing import Dict, List

from core.syslogger import logger
from core.constants import Const
from core.utility import Utility
from core.timestamp_services import shared_timestamp_service

from model.log_manager import LogManager
from model.device_config_manager import DeviceConfigManager
from model.timestamp_manager import TimestampManager
from model.log_inventory_manager import LogInventoryManager
from model.network_log_inventory_manager import NetworkLogInventoryManager
from model.sys_config_manager import SystemConfigManager, ConfigManager


class ViewModel:
    def __init__(self):
        self.sys_cofig = SystemConfigManager()
        self.log_model = LogManager()

        # Import device configurations and show commands
        if not self.import_device_config():
            return

        # Import and manage runtime json files
        self.import_execution_timestamp()
        self.import_net_inventory()
        self.import_log_inventory()

        self.sync_net_inventory_data()

    def import_device_config(self) -> bool:
        """
        Initializes the device configuration manager and verifies
        that network devices are available for analysis.
        """
        try:
            self.device_config = DeviceConfigManager()

            # If device config is initialized and has devices, return success
            if self.device_config:
                logger.info("Network device configuration imported successfully.")
                return True

        except Exception as e:
            raise e

        # Return False if initialization failed or no devices found
        return False

    def import_execution_timestamp(self):
        self.exec_timestamp = TimestampManager()

    def import_net_inventory(self):
        self.net_inventory = NetworkLogInventoryManager()

    def import_log_inventory(self):
        self.log_inventory = LogInventoryManager()

    def sync_net_inventory_data(self):
        # Update the network inventory with the latest configurations
        show_commands = self.device_config.get_show_commands()
        hostnames = self.device_config.get_hostnames()

        self.net_inventory.sync_data(hostnames, show_commands)

    def get_window_title_helper(self):
        return self.sys_cofig.get_title()

    def get_window_dimensions_helper(self):
        return self.sys_cofig.get_window_dimensions()

    def get_window_icon_path_helper(self):
        return self.sys_cofig.get_icon_path()

    def init_tk_variables(self):
        self.export_status = tk.StringVar()
        self.compare_status = tk.StringVar()
        self.collect_status = tk.StringVar()
        self.pre_log_status = tk.StringVar()
        self.post_log_status = tk.StringVar()

        self.config_status = tk.StringVar()
        self.content_status = tk.StringVar()

    def get_show_commands_helper(self):
        logger.info("Retrieving all show commands.")
        return self.device_config.get_show_commands()

    def get_table_data(self):
        return self.net_inventory.get_data()

    def get_host_log_comparison_result_helper(self, hostname: str) -> dict:
        return self.log_inventory.get_host_log_comparison_result(hostname)

    def get_log_collection_timestamp(self) -> str:
        return self.exec_timestamp.log_collection_timestamp

    def get_log_comparison_timestamp(self) -> str:
        return self.exec_timestamp.log_comparison_timestamp

    def load_pre_log_files(self, folder_path: str):
        # Check if any hostnames have show command configs
        if not self.device_config.has_hostnames_with_commands():
            self.pre_log_status.set(Const.NO_SH_CMD_CONF_PRE)
            return

        # Get filenames from folder
        filenames = Utility.get_log_filesnames(folder_path)

        if not filenames:
            self.pre_log_status.set(Const.PRE_PATH_INVALID_FILENAME_ERR)
            return

        # Import logs
        imported_logs = ConfigManager.import_logs(folder_path, filenames)

        if not imported_logs:
            self.pre_log_status.set(Const.NO_VALID_LOG_HOST_PRE)
            return

        # Filter logs by hostnames that have configured commands
        filtered_logs = self.device_config.filter_hosts_with_commands(imported_logs)

        if not filtered_logs:
            self.pre_log_status.set(Const.NO_VALID_LOG_HOST_PRE)
            return
        
        # Save filtered logs
        self.log_model.pre_logs = filtered_logs

    def load_post_log_files(self, folder_path: str):
        # Check if any hostnames have show command configs
        if not self.device_config.has_hostnames_with_commands():
            self.post_log_status.set(Const.NO_SH_CMD_CONF_POST)
            return

        # Get filenames from folder
        filenames = Utility.get_log_filesnames(folder_path)

        if not filenames:
            self.post_log_status.set(Const.POST_PATH_INVALID_FILENAME_ERR)
            return

        # Import logs
        imported_logs = ConfigManager.import_logs(folder_path, filenames)

        if not imported_logs:
            self.post_log_status.set(Const.NO_VALID_LOG_HOST_POST)
            return

        # Filter logs by hostnames that have configured commands
        filtered_logs = self.device_config.filter_hosts_with_commands(imported_logs)

        if not filtered_logs:
            self.post_log_status.set(Const.NO_VALID_LOG_HOST_POST)
            return

        # Save filtered logs
        self.log_model.post_logs = filtered_logs
        
    def export_comparison_logs(self, path: str) -> None:
        """
        Export the comparison logs to the specified path.
        
        :param path: The destination directory where the logs will be exported.
        """
        logger.info("Export log comparison result.")
        path = Path(path)

        if not path.is_dir():
            logger.error("Invalid export path.")
            self.export_status.set(Const.EXP_INVALID_PATH)
            return

        logs_to_export = self.log_inventory.get_export_logs()

        if not logs_to_export:
            logger.error("No data to export.")
            self.export_status.set(Const.EXP_NO_DATA)
            return

        export_result = Utility.export(path, logs_to_export)

        self.export_status.set(export_result)
        
    def compare_logs_helper(self) -> None:
        """
        Handles the process of comparing logs, updating the inventories, and refreshing the timestamp.
        It updates the comparison status and notifies the View.
        """
        try:
            # Perform the log comparison using the Model
            result = self.log_model.compare_logs()

            if result == Const.COMP_LOG_GOOD:
                # If comparison is successful, update inventories
                self._update_log_inventory()

                # Sync with network inventory
                log_results = self.log_inventory.get_log_data()
                self.net_inventory.bulk_update(log_results)

                # Update execution timestamp after comparison
                self._update_comparison_timestamp()

            # Set the result of the comparison (can be displayed in the UI)
            self.compare_status.set(result)

        except Exception as e:
            # Handle any errors gracefully and set status to indicate failure
            logger.error(f"Error during log comparison: {e}")
            self.compare_status.set(Const.COMP_LOG_BAD)
            raise

    def _update_log_inventory(self) -> None:
        """Updates the log inventory with the comparison result."""
        self.log_inventory.update(self.log_model.comparison_result)

    def _update_comparison_timestamp(self) -> None:
        """Refreshes the execution timestamp and updates the comparison timestamp."""
        shared_timestamp_service.refresh()
        timestamp = shared_timestamp_service.generate_readable_format()
        self.exec_timestamp.update_log_comparison_timestamp(timestamp)
    
    def collect_logs_helper(self) -> None:
        """
        Orchestrates the collection of logs from network devices, updates status, 
        and stores collected logs. Updates timestamps and statuses.
        """
        try:
            # Collect logs using the Model
            commands = self.device_config.hostname_with_commands
            result = self.log_model.collect_logs(self.device_config, commands)

            # Handle potential errors or skipped collection
            if result == Const.LOG_COLL_BAD or result == Const.LOG_COLL_SKIP:
                self.collect_status.set(result)
                return

            # Update network device reachability status
            self._update_device_reachability()

            # Update log collection statistics in the inventory
            self._update_log_collection_stats()

            # Store collected logs
            self._store_collected_logs()

            # Update the execution timestamp after collecting logs
            self._update_collection_timestamp()

            # Set the final collection status
            self.collect_status.set(result)

        except Exception as e:
            logger.error(f"Error occurred during log collection: {e}")
            self.collect_status.set(Const.LOG_COLL_BAD)
            raise

    def _update_device_reachability(self) -> None:
        """Update the reachability status of devices."""
        self.net_inventory.get_reachable_devices_status(self.device_config, self.log_model.reachable_devices)

    def _update_log_collection_stats(self) -> None:
        """Update the log collection statistics in the network inventory."""
        self.net_inventory.update_log_collection_stats(self.log_model.device_log_stats)

    def _store_collected_logs(self) -> None:
        """Store the collected logs as files."""
        hostname_with_logs = self.log_model.get_hostname_with_logs()
        host_paths = Utility.generate_host_paths(hostname_with_logs)
        self.log_model.store_network_logs(host_paths)

    def _update_collection_timestamp(self) -> None:
        """Update the timestamp of the log collection."""
        shared_timestamp_service.refresh()
        timestamp = shared_timestamp_service.generate_readable_format()
        self.exec_timestamp.update_log_collection_timestamp(timestamp)
