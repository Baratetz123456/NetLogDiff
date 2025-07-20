import tkinter as tk
from tkinter import ttk, font, messagebox, filedialog
from typing import List, Dict, Union
from functools import partial

from viewmodel.viewmodel import ViewModel
from core.syslogger import logger
from core.constants import Const
from core.messages import show_message
from core.utility import resource_path

# from .log_panel_view import LogPanelView
from .utility_view import set_window_center
from .log_comparison_result_view import LogComparisonResultView
from .device_status_table_view import DeviceStatusTableView


class MainView(tk.Tk):
    def __init__(self, viewmodel: ViewModel):
        super().__init__()
        self.vm = viewmodel

        if not self.validate_screen_resolution():
            return

        if not self.set_window_dimensions():
            return

        viewmodel.init_tk_variables()

        if not self.set_window_title():
            return

        if not self.set_icon():
            return

        if not self.validate_config_init():
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

        left_frame = ttk.Frame(self.paned)
        right_frame = ttk.Frame(self.paned)

        self.paned.add(left_frame, minsize=50)
        self.paned.add(right_frame, minsize=50)

        log_cmp_res = LogComparisonResultView(right_frame, self)
        device_status_tbl = DeviceStatusTableView(left_frame, self, log_cmp_res)

        self.setup_traces()

        self.after(100, lambda: self.paned.sash_place(0, 850, 0))

    def config_style(self):
        btn_font = font.Font(family="Arial", size=10, weight="bold")
        lbl_font = font.Font(family="Arial", size=10, weight="bold")

        style = ttk.Style()
        style.configure("TButton", font=btn_font, padding=10)
        style.configure("TLabel", font=lbl_font)

    def set_window_dimensions(self):
        width, height = self.vm.get_window_dimensions_helper()

        if width is None or height is None:
            logger.error("Window dimensions could not be determined.")
            self.destroy()
            return False

        self.geometry(f"{width}x{height}")
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
        return

    def validate_screen_resolution(self) -> bool:
        width, height = self.vm.get_window_dimensions_helper()

        if width is None or height is None:
            logger.error(
                "Window dimensions could not be determined for screen resolution check."
            )
            self.destroy()
            return False

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        if screen_width < width or screen_height < height:
            show_message(
                Const.WINDOW_ERROR,
                screen_width=screen_width,
                screen_height=screen_height,
            )
            self.destroy()
            return False

        return True

    def validate_config_init(self) -> bool:
        # When an import error occurs
        if bool(self.vm.config_status.get()):
            show_message(Const.INIT_ERROR, msg=self.vm.config_status.get())
            self.destroy()
            return False

        # When there were no network devices detected
        elif self.vm.config_content_status.get():
            show_message(self.vm.config_content_status.get())
            self.destroy()
            return False

        else:
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
