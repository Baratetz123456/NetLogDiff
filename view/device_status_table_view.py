import tkinter as tk
from tkinter import ttk

from core.constants import Const
from core.syslogger import logger
from core.messages import show_message


class DeviceStatusTableView:
    def __init__(self, parent, log_cmp_res):
        self.parent = parent
        self.log_cmp_res = log_cmp_res
        self.table_column_map = []
        
        self.log_collected_date = tk.StringVar()
        self.log_compared_date = tk.StringVar()
        
        btn_mframe = ttk.Frame(self)
        btn_mframe.pack(side=tk.TOP, fill=tk.X, padx=5)
        
        btn_lframe = ttk.Frame(btn_mframe)
        btn_lframe.pack(side=tk.LEFT, anchor="nw")
        
        btn_rframe = ttk.Frame(btn_mframe)
        btn_rframe.pack(side=tk.RIGHT, anchor="ne")
        
        self.create_main_buttons(btn_lframe, btn_rframe)
        
        lbl_mframe = ttk.Frame(lbl_mframe)
        lbl_mframe.pack(side=tk.TOP, fill=tk.X, padx=5, pady=(10, 0))
        
        lbl_lframe = ttk.Frame(lbl_mframe)
        lbl_lframe.pack(side=tk.LEFT, anchor="nw")
        
        lbl_rframe = ttk.Frame(lbl_mframe)
        lbl_rframe.pack(side=tk.RIGHT, anchor="ne")
        
        self.create_labels(lbl_lframe, lbl_rframe)
        
        exp_frame = ttk.Frame(self)
        exp_frame.pack(side=tk.TOP, anchor="e", fill=tk.X)
        
        self.create_export_btn(exp_frame)
        
        self.display_execution_timestamp()
        self.populate_table(self.parent.vm.get_table_data)
        
    def create_main_buttons(self, left_frame, right_frame):
        self.collect_logs_btn = ttk.Button(left_frame, text=Const.COLLECT_LOG_BTN, command=self.collect_logs_helper)
        self.select_pre_log_btn = ttk.Button(right_frame, text=Const.PRE_LOG_FOLDER_BTN, command=self.get_pre_log_path)
        self.select_post_log_btn = ttk.Button(right_frame, text=Const.POST_LOG_FOLDER_BTN, command=self.get_post_log_path)
        self.compare_btn = ttk.Button(right_frame, text=Const.COMPARE_BTN, command=self.compare_logs_helper)
        
        self.collect_logs_btn.pack(side=tk.LEFT, anchor="w")
        
        self.compare_btn.pack(side=tk.RIGHT, anchor="ne", padx=(3, 0))
        self.select_post_log_btn.pack(side=tk.RIGHT, anchor="ne", padx=(5, 0))
        self.select_pre_log_btn.pack(side=tk.RIGHT, anchor="ne")

    def create_labels(self, left_frame, right_frame):
        pass
    
    def create_export_btn(self, exp_frame):
        pass
    
    def display_execution_timestamp(self):
        pass
    
    def populate_table(self, table_data):
        pass

    def collect_logs_helper(self):
        pass
    
    def get_pre_log_path(self):
        pass
    
    def get_post_log_path(self):
        pass
    
    def compare_logs_helper(self):
        pass