
import tkinter as tk
from .log_panel_view import LogPanelView

class LogComparisonResultView:
    def __init__(self, parent):
        self.parent = parent
        
        self.create_labels()
        self.create_comparison_log_panels()
        
    def create_labels(self):
        pass
    
    def create_comparison_log_panels(self):
        self.log_panel = LogPanelView(self)
        self.log_panel.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    
    def display_comparison_result(self, hostname: str, show_command: str):
        pass
    
    def get_blank_lines(self, ref_str):
        return " " * len(ref_str)
    
    def clear_panels(self):
        self.log_panel.set_normal_state()
        self.log_panel.prelog_panel.delete(1.0, tk.END)
        self.log_panel.postlog_panel.delete(1.0, tk.END)
        self.log_panel.clear_line_numbers()
        self.log_panel.set_disabled_state()