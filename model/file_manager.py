import pytz
import zipfile
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Final

from core.syslogger import logger
from core.constants import Const


class FileManager:
    LOCATION: Final = "Asia/Manila"
    TIMESTAMP_TEMP: Final = "%Y%m%d_%H%M%S"
    
    def __init__(self):
        self.__timezone = pytz.timezone(self.LOCATION)
        self.date_time = datetime.now(self.__timezone)
        self.date_today = self.date_time.today().strftime("%Y%m%d")
        self.prev_cmp_log_dir = ""
        
        self.timestamp_cmp_log = ""
        self.dir_cmp_log = ""
        
    def generate_host_paths(self, hostnames: List[str]) -> Dict[str, str]:
        paths = {}
        folder_name = "logs"
        dt_hm = self.date_time.today().strftime(self.TIMESTAMP_TEMP)
        directory = self.get_current_log_dir(folder_name)
        
        for host in hostnames:
            filename = f"{host}_{dt_hm}.log"
            dir = Path(directory) / filename
            paths.update({host: dir})
        
        return paths
    
    def set_comparison_log_timestamp(self):
        self.timestamp_cmp_log = self.date_time.today().strftime(self.TIMESTAMP_TEMP)
        
    def get_comparison_log_dir(self, hostname: str, command: str):
        filename = f"{hostname}_{command}_{self.timestamp_cmp_log}.log"
        path = Path(hostname) / filename
        
        return path
    
    def get_current_log_dir(self, folder_name: str):
        time = self.date_time.today().strftime("%H%M")
        path = Path(folder_name) / self.date_today / time
        
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
        
    def get_timestamp(self):
        return self.date_time.today().strftime("%b %d, %Y %I:%M %p")
    
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


class ExportLogManager:
    @classmethod
    def export(cls, filename: str, logs: dict) -> str:
        logger.info("Exporting logs.")
        
        try:
            with zipfile.ZipFile(filename, mode="w", compression=zipfile.ZIP_DEFLATED) as zipf:
                for cmd_data in logs.values():
                    for log_path, data, in cmd_data.items():
                        zipf.writestr(log_path, data)
            
        except Exception as e:
            logger.error(e)
            return Const.EXPORT_BAD
        
        return Const.EXPORT_GOOD
        
        