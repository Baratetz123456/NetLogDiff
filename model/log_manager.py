import re
import os
from pathlib import Path
from typing import Dict, List, Final
from netmiko import ConnectHandler

from core.syslogger import logger
from core.constants import Const
from core.utility import Utility

from .sys_config_manager import ConfigManager

from .log_comparison_manager import LogComparisonManager
from .network_device_manager import NetworkDeviceManager

class LogManager:
    def __init__(self):
        self.pre_logs = {}
        self.post_logs = {}
        self.device_log_stats = {}
        self.comparison_result = {}
        self.reachable_devices = []
        
    def collect_logs(self, device_configs, device_show_commands: Dict[str, str]):
        if not device_configs:
            logger.error("No devices available for log collection.")
            return Const.LOG_COLL_SKIP
        
        logger.info(f"Collecting network logs from {len(device_configs)} devices")
        
        self.reset_device_log_stats()
        collection_flag = False
        self.reachable_devices = []
        
        transformed_configs = NetworkDeviceManager.transform_config(device_configs)
        
        for hostname, device in transformed_configs.items():
            self.device_log_stats.setdefault(hostname, [])
            
            with NetworkDeviceManager(device) as net_manager:
                net_manager.connect()
                
                if not net_manager.connection:
                    continue
                
                self.reachable_devices.append(hostname)                
                show_commands = device_show_commands.get(hostname)
                
                if show_commands is None:
                    logger.error(f"No show commands for hostname: {hostname}")
                    self.device_log_stats.update({hostname: []})
                    continue
            
                log_output = net_manager.run_multiple_commands(show_commands)
                
                if not log_output:
                    logger.warning(f"No network logs generated for {hostname}.")
                    self.device_log_stats.update({hostname: log_output})
                    continue
                
                collection_flag = True
                self.device_log_stats.update({hostname: log_output})
                        
        if collection_flag:
            return Const.LOG_COLL_GOOD
        
        return Const.LOG_COLL_SKIP
            
    def reset_device_log_stats(self):
        self.device_log_stats = {}
    
    def compare_logs(self):
        logger.info("Comparing Logs.")
        
        if not self.pre_logs:
            logger.error("Empty pre-logs.")
            return Const.COMP_PRE_LOG_EMP
        
        if not self.post_logs:
            logger.error("Empty post-logs.")
            return Const.COMP_POST_LOG_EMP
        
        parsed_pre_logs = LogComparisonManager.parse_log(self.pre_logs)
        parsed_post_logs = LogComparisonManager.parse_log(self.post_logs)
        
        self.comparison_result = LogComparisonManager.compare(parsed_pre_logs, parsed_post_logs)
        
        self.reset_logs()
        
        return Const.COMP_LOG_GOOD
    
    def is_log_valid(self, output):
        output = output.strip().lower()
        return "invalid" not in output
                
    def reset_logs(self):
        self.pre_logs = {}
        self.post_logs = {}
    
    def get_hostname_with_logs(self):
        return dict(filter(lambda x: len(x[1]), self.device_log_stats.items()))
    
    def store_network_logs(self, host_paths: Dict[str, str]):
        if not self.device_log_stats:
            logger.warning("No network logs available to compile.")
            return
        
        if not host_paths:
            logger.error("No host paths found.")
            return
        
        flag = False
        
        for hostname, log in self.device_log_stats.items():
            file_path = host_paths.get(hostname)
            
            if file_path is None:
                logger.error(f"No host path found for {hostname}")
                continue
            
            combined_logs = self.combine_logs(hostname, log)
            
            try:
                with open(file_path, mode="w", encoding="utf-8") as file:
                    file.write(combined_logs)
                    flag = True
                    
                logger.info(f"Network logs stored for {hostname}")
            
            except Exception as e:
                logger.error(e)
                return Const.LOG_COLL_FILE_SAVE_BAD
            
        if not flag:
            logger.error(f"Failed to store network logs.")
            return Const.LOG_COLL_FILE_SAVE_BAD
        
        logger.info("Network logs stored successfully.")
        return Const.LOG_COLL_FILE_SAVE_GOOD
    
    def combine_logs(self, hostname:str, logs: Dict[str, str]):
        output = ""
        
        for cmd, log in logs.items():
            if self.is_log_valid(log):
                output += f"{hostname}#{cmd}\n{log}\n\n"
            else:
                msg = f"Invalid output from {cmd}: \n{hostname}#{cmd}\n{log}\n"
                logger.error(msg)
        
        return output