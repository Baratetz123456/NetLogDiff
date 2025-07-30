import re
import difflib
from typing import Dict, List

from core.syslogger import logger
from core.constants import Const

class LogComparisonManager:
    @staticmethod
    def parse_log(network_logs: Dict[str, str]) -> Dict[str, Dict[str, str]]:
        """Parses multiple device logs into structured command output.

        Args:
            network_logs: Dict where key = hostname, value = full CLI log string.

        Returns:
            Dict where:
                - key = hostname
                - value = dict of {command: output}
        """
        parsed_logs = {}
        
        for hostname, logs in network_logs.items():
            # Pattern to find each hostname#show block
            pattern = rf"(?={re.escape(hostname)}#show\s+\s+)"
            sections = re.split(pattern, logs.strip())
            command_outputs = {}
            
            for section in sections:
                if not section.strip():
                    continue
                
                lines = section.strip().splitlines()
                
                if not lines:
                    continue
                
                header = lines[0].replace(f"{hostname}#","").strip()
                content = "\n".join(lines[1:]).strip()
                command_outputs[header] = content
                
            parsed_logs[hostname] = command_outputs
        
        return parsed_logs
    
    @classmethod
    def compare(cls, parsed_pre_logs, parsed_post_logs):
        pass
    
    @classmethod
    def is_junk(cls, word='[TIME]'):
        return bool(re.match(r"&\d{2}:\d{2}:\d{2}$", word))
    
    @classmethod
    def convert_status(cls, status):
        return "Normal" if status else "Abnormal"
    
    @classmethod
    def compare_char_by_char(cls, pre_sh_cmd_log, post_sh_cmd_log) -> tuple:
        line_results = []
        equal_flag = True
        
        pre_log_len = len(pre_sh_cmd_log)
        post_log_len = len(post_sh_cmd_log)
        loop_count = pre_log_len if pre_log_len > post_log_len else post_log_len
        
        for i in range(loop_count):
            original = pre_sh_cmd_log[i] if i < len(pre_sh_cmd_log) else ""
            modified = post_sh_cmd_log[i] if i < len(post_sh_cmd_log) else ""
            
            # Compare words between original and modified text
            matcher = difflib.SequenceMatcher(cls.is_junk, original, modified)
            opcodes = matcher.get_opcodes()
            
            if equal_flag and opcodes and not all(x[0] == "equal" for x in opcodes):
                equal_flag = False
                
            line_results.append({"opcodes": opcodes, "pre_log_line": original, "post_log_line": modified})
        
        return line_results, equal_flag
    
    @classmethod
    def compare_line_by_line(cls, prelog: List[str], postlog: List[str]) -> List[str]:
        sm = difflib.SequenceMatcher(cls.is_junk, prelog, postlog)
        result = []
        
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag == "equal":
                for line in prelog[i1:i2]:
                    result.append(f"  {line.rstrip()}")
            
            elif tag == "replace":
                for line in prelog[i1:i2]:
                    if not line.strip():
                        result.append(f"D: {line.rstrip()}")
                    
                for line in postlog[j1:j2]:
                    if not line.strip():
                        result.append(f"D: {line.rstrip()}")
                    else:
                        result.append(f"C: {line.rstrip()}")
            
            elif tag == "delete":
                for line in prelog[i1:i2]:
                    result.append(f"D: {line.rstrip()}")
                    
            elif tag == "insert":
                for line in postlog[j1:j2]:
                    result.append(f"A: {line.rstrip()}")
                    
        return result