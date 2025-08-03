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
        
    def get_current_log_dir(self, folder_name: str):
        time = shared_timestamp_service.generate_by_hm()
        date = shared_timestamp_service.generate_by_date()
        path = Path(folder_name) / date / time
        
        if FileManager.create_directory(path):
            return path
            
    @staticmethod    
    def create_directory(path):
        path = Path(path)
        
        if path.exists():
            return True
        
        try:
            path.mkdir(exist_ok=True, parents=True)
            logger.info(f"Directory created: {path}")
            
            return True    
        
        except Exception as e:
            logger.error(e)
            return False

    @classmethod
    def export(cls, path, logs: dict) -> str:
        logger.info("Exporting logs.test")
        
        dt_hm = shared_timestamp_service.generate_timestamp()
        filename = f"comparison_log_{dt_hm}.zip"
        file_path = Path(path) / filename
        
        try:
            with zipfile.ZipFile(file_path, mode="w", compression=zipfile.ZIP_DEFLATED) as zipf:
                for cmd_data in logs.values():
                    for log_path, data, in cmd_data.items():
                        zipf.writestr(str(log_path), data)
            
        except Exception as e:
            logger.error(f"Error encounterd during export: {e}")
            return Const.EXP_BAD
        
        return Const.EXP_GOOD
        
        