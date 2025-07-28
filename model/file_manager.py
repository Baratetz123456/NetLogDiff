import pytz
import zipfile
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Final

from core.syslogger import logger
from core.constants import Const
from core.timestamp_services import shared_timestamp_service

class FileManager:
    def __init__(self):
        self.prev_cmp_log_dir = ""        
        self.timestamp_cmp_log = ""
        self.dir_cmp_log = ""
        
    def generate_host_paths(self, hostnames: List[str]) -> Dict[str, str]:
        paths = {}
        folder_name = "logs"
        dt_hm = shared_timestamp_service.generate_timestamp()
        directory = self.get_current_log_dir(folder_name)
        
        for host in hostnames:
            filename = f"{host}_{dt_hm}.log"
            dir = Path(directory) / filename
            paths.update({host: dir})
        
        return paths
    
    def set_comparison_log_timestamp(self):
        self.timestamp_cmp_log = shared_timestamp_service.generate_timestamp()
        
    def get_comparison_log_dir(self, hostname: str, command: str):
        filename = f"{hostname}_{command}_{self.timestamp_cmp_log}.log"
        path = Path(hostname) / filename
        
        return path
        
    def get_current_log_dir(self, folder_name: str):
        time = shared_timestamp_service.generate_timestamp_by_hm()
        date = shared_timestamp_service.generate_timestamp_by_date()
        path = Path(folder_name) / date / time
        
        if FileManager.create_directory(path):
            return path
    
    @staticmethod    
    def create_directory(path):
        if path.exist():
            return True
        
        try:
            path.mkdir(exist_ok=True)
            logger.info(f"Directory created: {path}")
            
            return True    
        
        except Exception as e:
            logger.error(e)
            return False
            
    def extract_logs(self, logs):
        logger.info("Extract logs from log inventory.")
        self.set_comparison_log_timestamp()
        logs_to_export = {}
        
        for hostname, cmd_data in logs:
            for cmd, data in cmd_data.items():
                output = data.get("text_log_output")
                
                if output is None or not output:
                    logger.error(f"No logs to export for {cmd} from {hostname}.")
                    continue
                
                export_output = "\n".join(output)
                dir = self.get_comparison_log_dir(hostname, cmd)
                logs_to_export.setdefault(hostname, {}).update({dir: export_output})
                
        return logs_to_export

    @classmethod
    def export(cls, path, logs: dict) -> str:
        logger.info("Exporting logs.")
        
        filename = f"comparison_log_{cls.timestamp_cmp_log}.zip"
        file_path = Path(path) / filename
    
        try:
            with zipfile.ZipFile(file_path, mode="w", compression=zipfile.ZIP_DEFLATED) as zipf:
                for cmd_data in logs.values():
                    for log_path, data, in cmd_data.items():
                        zipf.writestr(log_path, data)
            
        except Exception as e:
            logger.error(e)
            return Const.EXPORT_BAD
        
        return Const.EXPORT_GOOD
        
        