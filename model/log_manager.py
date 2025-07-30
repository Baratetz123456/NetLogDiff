import re
import os
from pathlib import Path
from typing import Dict, List, Final
from netmiko import ConnectHandler

from core.syslogger import logger
from core.constants import Const
from core.utility import resource_path


from .log_comparison_manager import LogComparisonManager

class LogManager:
    def __init__(self):
        self.pre_logs = {}
        self.post_logs = {}
        self.device_log_stats = {}
        self.comparison_result = {}
    
    def collect_logs(self, device_configs, reachable_devices):
        if not device_configs:
            logger.error("No devices available for log collection.")
            return Const.LOG_COLL_SKIP
        
        logger.info(f"Collecting network logs from {len(device_configs)} devices")
        
        self.reset_device_log_stats()
        collection_flag = False
        
        for device in device_configs:
            hostname = device["hostname"]
            conn_type = device["connection_type"]
            self.device_log_stats.setdefault(hostname, [])
            
            if device not in reachable_devices:
                continue
            
            config = DeviceConfigManager.create_configuration(device)
            show_commands = device_configs.get_show_commands(hostname)
            
            if not show_commands or show_commands is None:
                logger.error(f"No show commands for hostname: {hostname}")
                self.device_log_stats.update({hostname: []})
                continue
            
            logger.info(f"Connection type: {conn_type}")
            log_output = self.connect(hostname, config, show_commands)
            
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
        if not self.pre_logs:
            return Const.COMP_PRE_LOG_EMP
        
        if not self.post_logs:
            return Const.COMP_POST_LOG_EMP
        
        parsed_pre_logs = LogComparisonManager.parse_log(self.pre_logs)
        parsed_post_logs = LogComparisonManager.parse_log(self.post_logs)
        self.comparison_result = LogComparisonManager.compare(parsed_pre_logs, parsed_post_logs)
        
        self.reset_logs()
        
        return Const.COMP_LOG_GOOD
    
    def import_logs(self, folder_path: str, filenames: List[str]) -> Dict[str, List[str]]:
        logger.info("Importing log files")
        logger.info(f"Number of files to import: {len(filenames)}")
        
        host_with_logs = {}
        
        for filename in filenames:
            hostname = self.extract_hostname(filename)
            path = Path(folder_path) / filename
            
            try:
                with open(path, mode="r") as file:
                    data = file.read()
                    host_with_logs.update({hostname: data})
            except Exception as e:
                logger.error(e)
                
        return host_with_logs
    
    def extract_hostname(self, filename: str) -> str:
        pattern = r"^(.+)_\d{8}_\d{6}\.log$"
        match = re.match(pattern, filename)
        
        if match:
            return match.group(1)
    
    def connect(self, hostname: str, config: Dict[str, str], commands: List[str]):
        logger.info(f"Connecting to {hostname}")
        
        try:
            output = ""
            net_connect = ConnectHandler(**config)
            net_connect.enable()
            
            for cmd in commands:
                logger.info(f"Executing command: {cmd}")
                command_output = net_connect.send_command(cmd)
                
                if self.validate_log_output(command_output):
                    output += f"{hostname}#{cmd}\n{command_output}\n\n"
                else:
                    msg = f"Invalid output from {cmd}: \n{hostname}#{cmd}\n{command_output}\n"
                    logger.error(msg)
                    
            net_connect.disconnect()
            logger.info(f"Connection to {hostname} closed successfully.")
            return output
        
        except Exception as e:
            logger.error(f"Error from {hostname}: {e}")
            return
    
    def validate_log_output(self):
        output = output.strip()
        return "Invalid" not in output
                
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
            
            try:
                with open(file_path, mode="w", encoding="utf-8") as file:
                    file.write(log)
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
    