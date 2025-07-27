import os
import tkinter as tk
from typing import Dict, List

from core.syslogger import logger
from core.constants import Const

from model.log_manager import LogManager
from model.device_config_manager import DeviceConfigManager
from model.file_manager import FileManager, ExportLogManager
from model.timestamp_manager import TimestampManager
from model.log_inventory_manager import LogInventoryManager
from model.network_log_inventory_manager import NetworkLogInventoryManager
from model.sys_config_manager import SystemConfigManager


class ViewModel:
    def __init__(self):
        self.sys_cofig = SystemConfigManager()
        self.log_model = LogManager()

        # Import device configurations and show commands
        if not self.import_device_config():
            return

        # Import data files and create directories
        self.import_runtime_data_files()

        # Import and manage runtime json files
        self.import_execution_timestamp()
        self.import_net_inventory()
        self.import_log_inventory()

        # self.sync_net_inventory_data()

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

    def import_runtime_data_files(self):
        self.file_manager = FileManager()

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

    def collect_logs_helper(self):
        # Validate reachability of network devices
        self.net_inventory.validate_device_reachability(self.device_config)

        # Filter only reachable network devices
        reachable_device_config = self.net_inventory.filter_reachable_devices(
            self.device_config
        )

        # Collect logs by sending show commands to network devices
        result = self.log_model.collect_logs(
            self.device_config, reachable_device_config
        )

        # Update the log collection status for table data
        self.net_inventory.update_log_collection_stats(self.log_model.device_log_stats)

        # Update execution timestamp
        timestamp = self.file_manager.get_timestamp()
        self.exec_timestamp.update_log_collection_timestamp(timestamp)

        if result == Const.LOG_COLL_BAD or result == Const.LOG_COLL_SKIP:
            self.collect_status.set(result)
            return

        hostname_with_logs = self.log_model.get_hostname_with_logs()
        host_paths = self.file_manager.generate_host_paths(hostname_with_logs)

        # Store collected logs as log file
        self.log_model.store_network_logs(host_paths)

        self.collect_status.set(result)
