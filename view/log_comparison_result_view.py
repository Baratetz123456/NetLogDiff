
import tkinter as tk
from tkinter import ttk
from .log_panel_view import LogPanelView
from core.syslogger import logger
from core.constants import Const

class LogComparisonResultView:
    def __init__(self, parent):
        self.parent = parent
        
        self.create_labels()
        self.create_comparison_log_panels()
        
    def create_labels(self):
        top_frame = ttk.Frame(self.parent)
        top_frame.pack(side=tk.TOP, fill=tk.X, padx=5)
        
        comparison_result_lbl = ttk.Label(top_frame, text=Const.COMPARISON_LBL)
        comparison_result_lbl.pack(side=tk.TOP, anchor="w")
        
        left_frame = ttk.Frame(top_frame)
        left_frame.pack(side=tk.LEFT, anchor="nw", pady=(5, 5))
        
        right_frame = ttk.Frame(top_frame)
        right_frame.pack(side=tk.RIGHT, anchor="nw", pady=(5,5))
        
        pre_log_lbl = ttk.Label(left_frame, text=Const.PRE_LOG_LBL)
        pre_log_lbl.pack(side=tk.TOP, anchor="w")
        
        post_log_lbl = ttk.Label(right_frame, text=Const.POST_LOG_LBL)
        post_log_lbl.pack(side=tk.TOP, anchor="e")
                
    def create_comparison_log_panels(self):
        self.log_panel = LogPanelView(self.parent)
        self.log_panel.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
    def get_blank_lines(self, ref_str):
        return " " * len(ref_str)
    
    def clear_panels(self):
        self.log_panel.set_normal_state()
        self.log_panel.prelog_panel.delete(1.0, tk.END)
        self.log_panel.postlog_panel.delete(1.0, tk.END)
        self.log_panel.clear_line_numbers()
        self.log_panel.set_disabled_state()
        
    def populate_log_results(self, sh_result):
        self.clear_panels()
        self.log_panel.set_normal_state()
        
        for x in sh_result["ui_log_output"]:
            original = x["pre_log_line"]
            modified = x["post_log_line"]
            
            for op, i1, i2, j1, j2 in x["opcodes"]:
                # Words that are unchanged
                if op == "equal":
                    val = ["end", "".join(original[i1:i2]), Const.TAG_E]
                    self.log_panel.prelog_panel.insert(*val)
                    self.log_panel.postlog_panel.insert(*val)
                
                # Words that are replaced
                elif op == "replace":                    
                    self.log_panel.prelog_panel.insert("end", "".join(original[j1:j2]), Const.TAG_RP)
                    self.log_panel.postlog_panel.insert("end", "".join(modified[j1:j2]), Const.TAG_RP)
                
                # Words that are inserted (only on the modified side)
                elif op == "insert":
                    self.log_panel.postlog_panel.insert("end", "".join(modified[j1:j2]), Const.TAG_A)
                    
                    if not original.strip():
                        self.log_panel.prelog_panel.insert("end", self.get_blank_lines(modified), Const.TAG_AB)
                
                elif op == "delete":
                    self.log_panel.postlog_panel.insert("end", self.get_blank_lines(original), Const.TAG_RMB)
           
            self.log_panel.prelog_panel.insert("end", "\n")
            self.log_panel.postlog_panel.insert("end", "\n")
            
        self.log_panel.update_panel_line_numbers()
        self.log_panel.set_disabled_state()
        
    def display_comparison_result(self, hostname: str, show_command: str):
        logger.info("Display log comparison result.")
        
        show_command_results = self.parent.vm.get_host_log_comparison_result_helper(hostname)
        
        if show_command_results is None:
            msg = f"No log comparison result found for {show_command} from {hostname}."
            logger.warning(msg)
            return
        
        sh_result = show_command_results.get(show_command)
        
        if sh_result is None:
            msg = f"Unable to determine show command result."
            logger.error(msg)
            return
        
        self.populate_log_results(sh_result)
        
                    
                    