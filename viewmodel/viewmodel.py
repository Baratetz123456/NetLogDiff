import os
import tkinter as tk
from typing import Dict, List

from core.syslogger import logger
from core.constants import Const

# from model.log_model import LogModel
# from model.config_manager import DeviceConfigManager
# from model.file_manager import LogFileManager, ExportLogManager
# from model.timestamp_manager import ExecutionTimestampManager
# from model.log_inventory_manager import LogInventory
# from model.network_log_inventory_manager import NetworkInventory
from model.sys_config_manager import SystemConfigManager

class ViewModel:
    def __init__(self):        
        self.sys_cofig = SystemConfigManager()
        
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
    
    