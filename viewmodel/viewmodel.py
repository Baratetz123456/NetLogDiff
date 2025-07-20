import os
import tkinter as tk
from typing import Dict, List

from core.syslogger import logger
from core.constants import Const

from model.log_model import LogModel
from model.config_manager import DeviceConfigManager
from model.file_manager import LogFileManager, ExportLogManager
from model.timestamp_manager import ExecutionTimestampManager
from model.log_inventory_manager import LogInventory
from model.network_log_inventory_manager import NetworkInventory


class ViewModel:
    def __init__(self):
        self.export_status = tk.StringVar()
        self.compare_status = tk.StringVar()
        self.collect_status = tk.StringVar()
        self.pre_log_status = tk.StringVar()
        self.post_log_status = tk.StringVar()
        
        self.device_config_status = tk.StringVar()