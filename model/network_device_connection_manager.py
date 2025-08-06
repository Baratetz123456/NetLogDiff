from netmiko import ConnectHandler, NetmikoTimeoutException
from typing import Dict, List

from core.syslogger import logger


class NetworkDeviceConnectionManager:
    def __init__(self, device_params):
        self.device_params = device_params
        self.connection = None
        
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        # perform cleanup
        self.disconnect()
        
    def connect(self):
        """Establish SSH connection to the network device."""
        
        try:
            self.connection = ConnectHandler(**self.device_params)
            self.connection.enable()    
        
            logger.info(f"Connected to {self.device_params['host']}")
            
        except NetmikoTimeoutException as e:
            logger.error(f"Connection failed: {e}")
            raise
        
        except Exception as e:
            logger.error(f"Failed to connect to {self.device_params['host']}: {e}")
            raise

    def run_show_command(self, command):
        """Run a single show command and return the output."""
        
        if self.connection is None:
            raise Exception("Not connected to any device.")
        
        logger.info(f"Running command: {command}")
        
        return self.connection.send_command(command)

    def run_multiple_commands(self, commands: List[str]):
        """Run multiple show commands and return a dict with their output."""
        
        results = {}
        
        for cmd in commands:
            results[cmd] = self.run_show_command(cmd)
            
        return results

    def disconnect(self):
        """Close the SSH connection."""
        
        if self.connection:
            self.connection.disconnect()
            logger.info("Disconnected from device.")
    
    @classmethod
    def transform_config(cls, device_config: List[Dict[str, str]]) -> Dict[str, Dict[str, str]]:        
        if not device_config:
            logger.error("Invalid device_config parameter. Must be a non-empty dicts of list.")
            return {}
        
        transformed_config = {}
        
        for device in device_config:
            try:
                transformed = cls.construct_config(device)
                transformed_config.update({device["hostname"]: transformed})
            
            except Exception as e:
                logger.error(f"Missing key in device config: {e}")
            
        return transformed_config            
    
    @classmethod
    def construct_config(cls, device: Dict[str, str]) -> Dict[str, str]:
        device_os = device['device_os']
        conn_type = device['connection_type']
        device_type = f"{device_os}_telnet" if conn_type.strip().lower() == "telnet" else device_os
        return {
                'device_type': device_type,
                'host': device['ipaddress'],
                'username': device['username'],
                'password': device['password'],
                'secret': device['admin_password']
            }
    

    