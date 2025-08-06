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
            command_outputs = {}
            
            # Match command headers and outputs
            pattern = re.compile(
                rf"{re.escape(hostname)}#(show .+?)(?=\n{re.escape(hostname)}#show |\Z)", 
                re.DOTALL
            )
            
            matches = pattern.finditer(logs)
            
            for match in matches:
                full_output = match.group(1).strip()
                
                if "\n" in full_output:
                    command, output = full_output.split("\n", 1)
                else:
                    command, output = full_output, ""
                
                command_outputs[command.strip()] = output.strip()
            
            parsed_logs[hostname] = command_outputs

        return parsed_logs
    
    @classmethod
    def compare(cls, parsed_pre_logs, parsed_post_logs):
        logger.info("Compare pre-log and post-log.")
        results = {}
        
        for hostname, pre_logs in parsed_pre_logs.items():
            post_logs = parsed_post_logs.get(hostname)
            sh_cmd_results = {}
            
            for sh_cmd, pre_sh_cmd_log in pre_logs.items():
                post_sh_cmd_log = post_logs.get(sh_cmd)
                
                if post_sh_cmd_log is None or not post_sh_cmd_log:
                    logger.error(f"No post log found for {sh_cmd} for {hostname}.")
                    continue
                
                pre_sh_cmd_log = pre_sh_cmd_log.splitlines()
                post_sh_cmd_log = post_sh_cmd_log.splitlines()
                
                # Log comparison for text based results
                line_results = cls.compare_line_by_line(
                    pre_sh_cmd_log, post_sh_cmd_log
                )
                
                if not line_results:
                    msg = f"Unable to determine log comparison result for {hostname} with show command: {sh_cmd}"
                    logger.error(msg)
                    continue
                
                # Log comparison for UI based results
                char_results, status = cls.compare_char_by_char(pre_sh_cmd_log, post_sh_cmd_log)
                sh_cmd_results[sh_cmd] = {
                    "status": cls.convert_status(status),
                    "ui_log_output": char_results,
                    "text_log_output": line_results
                }
            
            results[hostname] = sh_cmd_results
        
        return results
    
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