import tkinter as tk
from tkinter import ttk
from .utility_view import set_window_center
from core.syslogger import logger


class ProgressState:
    def __init__(self):
        self.value = 0.0
        self.closed = False
    
    def set_value(self, value: float):
        if self.closed:
            return
        
        self.value = max(0.0, min(100.0, value)) # clamp between 0-100
    
    def mark_closed(self):
        self.closed = True
    
    def is_complete(self):
        return self.value >= 100.0
    
    def reset(self):
        self.value = 0.0
        self.closed = False


class LogCollectionProgressBar:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.state = ProgressState()
        self.progress_label = tk.StringVar(value="0.00%")
        self.top = None
        self.progress = None
    
    def display(self):
        # Clean up old window if it exists
        if self.top and self.top.winfo_exists():
            self.top.destroy()
        
        self.state.reset()
        self.progress_label = tk.StringVar(value="0.00%")

        self.top = tk.Toplevel(self.root)
        self.top.title("Log Collection Progress")
        self.top.resizable(False, False)
        self.top.geometry("400x80")
        self.top.protocol("WM_DELETE_WINDOW", self.on_close)

        logger.info("The progress bar window is displayed.")
        set_window_center(self.top)

        bar_frame = ttk.Frame(self.top)
        bar_frame.pack(side=tk.TOP, fill=tk.X, anchor="center", padx=10, pady=10)

        m_frame = ttk.Frame(self.top)
        m_frame.pack(side=tk.TOP, fill=tk.X, anchor="center", padx=10, pady=10)

        l_frame = ttk.Frame(m_frame)
        l_frame.pack(side=tk.LEFT, anchor="nw")

        r_frame = ttk.Frame(m_frame)
        r_frame.pack(side=tk.LEFT, anchor="ne")

        self.progress = ttk.Progressbar(bar_frame, orient="horizontal", length=390, mode="determinate")
        self.progress.pack(side=tk.LEFT)

        progress_lbl = ttk.Label(l_frame, text="Total completion:")
        progress_lbl.pack(side=tk.LEFT, anchor="w")

        self.progress_count_lbl = ttk.Label(r_frame, textvariable=self.progress_label)
        self.progress_count_lbl.pack(side=tk.RIGHT, anchor="e")

    def update_progress(self, value: float):
        """Thread-safe update of progress bar."""
        if not self.top or not self.top.winfo_exists():
            return

        self.state.set_value(value)
        self.root.after(0, self._refresh_ui)
    
    def _refresh_ui(self):
        """Upate UI elements base on state"""
        self.progress["value"] = self.state.value
        self.progress_label.set(f"{self.state.value:.2f}%")

        if self.state.is_complete():
            logger.info("Progress completed. Closing window.")
            self.close()

    def on_close(self):
        """Handle user closing the window."""
        logger.info("Progress bar window closed by the user!")
        self.state.mark_closed()

        root = self.root.winfo_toplevel()

        if not hasattr(root.vm, "task_thread"):
            logger.error("No task_thread found.")
        elif not root.vm.task_thread.is_alive():
            logger.error("No thread alive.")
        else:
            root.vm.stop_task_thread()
        
        self.close()
    
    def close(self):
        """Safely destroy the window"""
        if self.top and self.top.winfo_exists():
            self.top.destroy()
        
        self.state.mark_closed()


