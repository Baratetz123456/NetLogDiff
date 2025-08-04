import os
import re
import sys
import zipfile
from pathlib import Path
from typing import List, Dict

from core.syslogger import logger
from core.constants import Const
from core.timestamp_services import shared_timestamp_service


class Utility:
    @staticmethod
    def resource_path(relative_path: str) -> str:
        """Get the absolute path to resource

        Args:
            relative_path (str): path
        """
        
        try:
            base_path = sys._MEIPASS
        
        except Exception:
            base_path = os.path.abspath(".")
            
        return os.path.join(base_path, relative_path)

    @staticmethod
    def create_directory(path: str) -> bool:
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
    def generate_host_paths(cls, hostnames: List[str]) -> Dict[str, str]:
        paths = {}
        folder_name = "logs"
        dt_hm = shared_timestamp_service.generate_timestamp()
        directory = cls.get_current_log_dir(folder_name)
        
        for host in hostnames:
            filename = f"{host}_{dt_hm}.log"
            dir = Path(directory) / filename
            paths.update({host: dir})
        
        return paths
    
    @classmethod
    def get_current_log_dir(cls, folder_name: str):
        time = shared_timestamp_service.generate_by_hm()
        date = shared_timestamp_service.generate_by_date()
        path = Path(folder_name) / date / time
        
        if cls.create_directory(path):
            return path
    
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
    
    @staticmethod
    def extract_hostname(filename: str) -> str:
        pattern = r"^(.+)_\d{8}_\d{6}\.log$"
        match = re.match(pattern, filename)
        
        if match:
            return match.group(1)
    
    @staticmethod
    def get_log_filesnames(path: str) -> List[str]:
        # Validate input paths
        path = Path(path)

        if not path.is_dir():
            logger.error(f"Invalid file path: {path}")
            return []

        filenames = [
            f.name for f in path.iterdir() if f.is_file() and f.suffix.lower() == ".log"
        ]

        if not filenames:
            logger.warning(f"No .log files found in: {path}")

        return filenames