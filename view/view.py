import tkinter as tk
from tkinter import ttk, font, messagebox, filedialog
from typing import List, Dict, Union
from functools import partial

from viewmodel.viewmodel import ViewModel
from core.syslogger import logger
from core.constants import Const
from core.messages import show_message

from .utility_view import set_window_center
from .log_comparison_result_view import LogComparisonResultView
from .device_status_table_view import DeviceStatusTableView


class MainView(tk.Tk):
    def __init__(self):
        super().__init__()
        self.vm = self.create_viewmodel()

        if not self.vm:
            self.destroy()
            return

        self.vm.set_view(self)

        if not self.set_window_dimensions():
            return

        self.vm.init_tk_variables()

        if not self.set_window_title():
            return

        if not self.set_icon():
            return

        set_window_center(self)
        self.config_style()

        self.paned = tk.PanedWindow(
            self,
            orient=tk.HORIZONTAL,
            sashwidth=5,
            sashrelief=tk.RAISED,
            opaqueresize=False,
        )
        self.paned.pack(fill=tk.BOTH, expand=True)

        self.left_frame = ttk.Frame(self.paned)
        self.right_frame = ttk.Frame(self.paned)

        self.paned.add(self.left_frame, minsize=180)
        self.paned.add(self.right_frame, minsize=200)

        log_cmp_res = LogComparisonResultView(self.right_frame, self.vm)
        self.device_status_tbl = DeviceStatusTableView(
            self.left_frame, self.vm, log_cmp_res
        )

        self.setup_traces()

        self.bind("<Configure>", self.on_resize)
        # Bind to sash movement (mouse drag with button 1)
        self.paned.bind("<B1-Motion>", self.on_resize)
        # Place sash in the middle of winow
        self.paned.bind("<Configure>", self.place_sash_middle)

    def on_resize(self, event):
        # If window width is less than 1380px -> collapse into burger menu
        # If left frame width is less than 577 -> collapse into burger menu
        if self.left_frame.winfo_width() < 577:
            self.device_status_tbl.show_menu_button()
        else:
            self.device_status_tbl.hide_menu_button()

    def toggle_menu(self):
        if self.device_status_tbl.burger_btn.winfo_ismapped():
            # Hide menu button
            self.device_status_tbl.burger_btn.pack_forget()
        else:
            # Show menu button
            self.device_status_tbl.burger_btn.pack(side=tk.RIGHT, fill="y")

    def place_sash_middle(self, event=None):
        if self.paned.cget("orient") == tk.HORIZONTAL:
            # Place sash horizontally in the middle
            self.paned.sash_place(0, self.paned.winfo_width() // 2, 0)

    def create_viewmodel(self):
        try:
            return ViewModel()

        except Exception as e:
            show_message(Const.INIT_ERROR, msg=e)
            return

    def config_style(self):
        style = ttk.Style()
        style.configure("TButton", padding=10)
        style.configure(
            "Big.TMenubutton",
            padding=(10, 10),
            font=("Arial", 14),
            borderwith=5,
            relief="solid",
            foreground="black",
            background="white",
        )

    def set_window_dimensions(self):
        width, height = self.vm.get_window_dimensions_helper()

        if width is None or height is None:
            logger.error("Window dimensions could not be determined.")
            self.destroy()
            return False

        screen_width = int(self.winfo_screenwidth() * width)
        screen_height = int(self.winfo_screenheight() * height)

        self.geometry(f"{screen_width}x{screen_height}")
        self.minsize(width=400, height=400)
        return True

    def set_window_title(self):
        title = self.vm.get_window_title_helper()

        if title is None:
            logger.error("Unable to determine window title configuration.")
            self.destroy()
            return False

        self.title(title)
        return True

    def set_icon(self):
        icon_path = self.vm.get_window_icon_path_helper()

        if icon_path is None:
            logger.error("Window icon path is None or invalid.")
            self.destroy()
            return False

        self.iconbitmap(icon_path)
        return True

    def setup_traces(self):
        for var in [
            self.vm.collect_status,
            self.vm.compare_status,
            self.vm.config_status,
            self.vm.export_status,
            self.vm.post_log_status,
            self.vm.pre_log_status,
        ]:
            var.trace_add("write", partial(self.show_status_message, var))

    def show_status_message(self, var, *args):
        status = var.get()
        show_message(status)

        if self.is_progress_window_alive():
            self.close_progress_bar_helper()
    
    def is_progress_window_alive(self):
        progress_bar = getattr(self.device_status_tbl, "log_collection_progress_bar", None)
        if not progress_bar or not hasattr(progress_bar, "top") or progress_bar.top is None:
            return False
        
        return bool(progress_bar.top.winfo_exists())

    def update_progress_bar_helper(self, value):
        return self.device_status_tbl.log_collection_progress_bar.update_progress(value)
    
    def close_progress_bar_helper(self):
        self.device_status_tbl.log_collection_progress_bar.close()
