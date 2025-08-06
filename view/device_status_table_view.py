import tkinter as tk
from tkinter import ttk, filedialog
from typing import List, Union

from core.constants import Const
from core.syslogger import logger
from core.messages import show_message


class DeviceStatusTableView:
    def __init__(self, parent, vm, log_cmp_res):
        self.parent = parent
        self.vm = vm
        
        self.log_cmp_res = log_cmp_res
        self.table_column_map = []
        
        self.log_collected_date = tk.StringVar()
        self.log_compared_date = tk.StringVar()
        
        btn_mframe = ttk.Frame(self.parent)
        btn_mframe.pack(side=tk.TOP, fill=tk.X, padx=5)
        
        btn_lframe = ttk.Frame(btn_mframe)
        btn_lframe.pack(side=tk.LEFT, anchor="nw")
        
        btn_rframe = ttk.Frame(btn_mframe)
        btn_rframe.pack(side=tk.RIGHT, anchor="ne")
        
        self.create_main_buttons(btn_lframe, btn_rframe)
        
        lbl_mframe = ttk.Frame(self.parent)
        lbl_mframe.pack(side=tk.TOP, fill=tk.X, padx=5, pady=(10, 0))
        
        lbl_lframe = ttk.Frame(lbl_mframe)
        lbl_lframe.pack(side=tk.LEFT, anchor="nw")
        
        lbl_rframe = ttk.Frame(lbl_mframe)
        lbl_rframe.pack(side=tk.RIGHT, anchor="ne")
        
        self.create_labels(lbl_lframe, lbl_rframe)
        
        # Table frame
        tbl_frame = ttk.Frame(self.parent)
        tbl_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.create_table(tbl_frame, self.vm.get_show_commands_helper())
        
        exp_frame = ttk.Frame(self.parent)
        exp_frame.pack(side=tk.TOP, anchor="e", fill=tk.X)
        
        self.create_export_btn(exp_frame)
        
        self.display_execution_timestamp()
        self.populate_table(vm.get_table_data())
        
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
        self.log_collect_lbl = ttk.Label(left_frame, textvariable=self.log_collected_date)
        self.log_compared_lbl = ttk.Label(right_frame, textvariable=self.log_compared_date)
        
        self.log_collect_lbl.pack(side=tk.LEFT, anchor="w")
        self.log_compared_lbl.pack(side=tk.LEFT, anchor="e")
    
    def create_table(self, tbl_frame, show_commands: List[str] = None):
        stretchable = False if len(show_commands) > 5 else True
        all_columns_count: int = len(show_commands) + 4
        columns: list = list(range(all_columns_count))
        
        self.tree = ttk.Treeview(tbl_frame, columns=columns, show="headings", height=30)
        
        # Set default column map
        self.table_column_map = ["#", "Hostname", "Reachability", "Log"]
        
        # Default headings
        self.tree.heading(0, text="#")
        self.tree.heading(1, text="Hostname", anchor="center")
        self.tree.heading(2, text="Reachability")
        self.tree.heading(3, text="Log")
        
        # Default columns
        self.tree.column(0, width=25, anchor="center", stretch=stretchable)
        self.tree.column(1, width=100, anchor="center", stretch=stretchable)
        self.tree.column(2, width=90, anchor="center", stretch=stretchable)
        self.tree.column(3, width=40, anchor="center", stretch=stretchable)
        
        # Show command headings and columns
        for sh in range(4, len(show_commands) + 4):
            sh_cmd_name = show_commands[sh -4]
            self.tree.heading(sh, text=sh_cmd_name)
            self.tree.column(sh, width=120, anchor="center", stretch=stretchable)
            self.table_column_map.append(sh_cmd_name)
        
        self.tree.tag_configure("abnormal", background=Const.ABNORMAL_COLOR)
        yscrollbar = ttk.Scrollbar(tbl_frame, orient=tk.VERTICAL, command=self.tree.yview)
        xscrollbar = ttk.Scrollbar(tbl_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        
        self.tree.configure(yscrollcommand=yscrollbar.set)
        self.tree.configure(xscrollcommand=xscrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tree.bind("<Double-1>", self.on_cell_double_click)        
        
    def create_export_btn(self, exp_frame):
        self.export_btn = ttk.Button(exp_frame, text=Const.EXPORT_BTN, command=self.export_comparison_logs)
        self.export_btn.pack(side=tk.RIGHT, anchor="e", padx=(10, 0), pady=10)
        
    def populate_table(self, table_data):
        logger.info("Populating table data.")
        
        if not isinstance(table_data, dict) or not table_data:
            logger.error("Empty table data.")
            return
        
        for index, (hostname, data) in enumerate(table_data.items()):
            default_list = [index + 1, hostname]
            data_list = self.convert_bool_to_symbols(list(data.values()))
            data = tuple(default_list + data_list)
            
            if "Abnormal" in data:
                self.tree.insert("", tk.END, iid=str(index), values=data, tags=["abnormal"])
            else:
                self.tree.insert("", tk.END, iid=str(index), values=data)
        
        self.parent.update_idletasks()
    
    def get_pre_log_path(self):
        logger.info("Get pre-log path.")
        file_path = filedialog.askdirectory(title="Pre-log directory", initialdir="")
        
        if file_path:
            try:
                self.vm.load_pre_log_files(file_path)
                
            except Exception as e:
                show_message(Const.PRE_IMP_ERR, error=e)

        self.log_cmp_res.clear_panels()
        
    def get_post_log_path(self):
        logger.info("Get post-log path.")
        file_path = filedialog.askdirectory(title="Post-log directory", initialdir="")
        
        if file_path:
            try:
                self.vm.load_post_log_files(file_path)
                
            except Exception as e:
                show_message(Const.POST_IMP_ERR, error=e)

        self.log_cmp_res.clear_panels()
        
    def export_comparison_logs(self):
        file_path = filedialog.askdirectory(title="Export logs", initialdir=".")
        
        if file_path:
            try:
                self.vm.export_comparison_logs(file_path)
                
            except Exception as e:
                show_message(Const.EXP_CMP_ERR, error=e)
    
    def convert_bool_to_symbols(self, data: List[Union[bool, str]]) -> List[str]:
        new_list = []
        
        for x in data:
            if isinstance(x, bool):
                # O = True, X = False
                new_list.append("\u25ef" if x else "\u2715")
            else:
                new_list.append(str(x))
                
        return new_list
    
    def collect_logs_helper(self):
        self.vm.collect_logs_helper()
        self.reload_table_data()
        
    def compare_logs_helper(self):
        self.vm.compare_logs_helper()
        self.reload_table_data()
        
    def reload_table_data(self):
        logger.info("Reload table data.")
        # Clear existing displayed table data
        self.tree.delete(*self.tree.get_children())
        
        # Insert new results
        self.populate_table(self.vm.get_table_data())
        self.display_execution_timestamp()
        
        # Reload the UI table
        self.parent.update_idletasks()
        
    def on_cell_double_click(self, event):
        # Get reference to the Treview widget
        tree = event.widget
        
        # Identify the region, column and row under the cursor
        row_id = tree.identify_row(event.y)
        column = tree.identify_column(event.x)
        
        if not (row_id and column):
            return
        
        # Get the values in the selected row
        row_values = tree.item(row_id, "values")
        
        # Convert column to index (0-Based)
        col_index = int(column.replace("#", "")) - 1
        
        if col_index < 4:
            return
        
        show_command = self.table_column_map[col_index]
        hostname = row_values[1]
        
        self.log_cmp_res.display_comparison_result(hostname, show_command)
        
    def display_execution_timestamp(self):
        logger.info("Display execution timestamp.")
        
        log_col_tsmp = self.vm.get_log_collection_timestamp()
        log_cmp_tsmp = self.vm.get_log_comparison_timestamp()
        
        self.log_collected_date.set(f"Latest log collected: {log_col_tsmp}")
        self.log_compared_date.set(f"Latest log collected: {log_cmp_tsmp}")
        
    