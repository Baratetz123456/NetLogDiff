import tkinter as tk
from tkinter import ttk, font, messagebox, filedialog
from typing import List, Dict, Union
from functools import partial

from viewmodel.viewmodel import ViewModel
from core.syslogger import logger
from core.constants import Const
from core.messages import show_message
from core.utility import resource_path
from .log_panel_view import LogPanelView


class MainView(tk.Tk):
    def __init__(self, viewmodel: ViewModel):
        super().__init__()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        if screen_width < Const.WINDOW_WIDTH or screen_height < Const.WINDOW_HEIGHT:
            show_message(Const.WINDOW_ERROR, screen_width=screen_width, screen_height=screen_height)
            self.destroy()
            return
        
        self.viewmodel = viewmodel()