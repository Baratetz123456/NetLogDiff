import tkinter as tk
from tkinter import ttk
import tkinter.font as tkfont
from core.constants import Const


class LogPanelView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        # Shared font for text and line numbers
        self.text_font = tkfont.Font(family="Courier New", size=12)

        # Configure scrollbars
        self.vert_scrollbar = tk.Scrollbar(
            self, orient=tk.VERTICAL, command=self.on_vertical_scroll
        )
        self.horiz_scrollbar = tk.Scrollbar(
            self, orient=tk.HORIZONTAL, command=self.on_horizontal_scroll
        )

        self.vert_scrollbar.pack(fill=tk.Y, side=tk.RIGHT)
        self.horiz_scrollbar.pack(fill=tk.X, side=tk.BOTTOM)

        prelog_frame = tk.Frame(self, width=400)
        prelog_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        prelog_frame.pack_propagate(False)
        
        postlog_frame = tk.Frame(self, width=400)
        postlog_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        postlog_frame.pack_propagate(False)

        # Line numbers widget
        self.prelog_line_num = self.create_line_numbers(prelog_frame)
        self.postlog_line_num = self.create_line_numbers(postlog_frame)

        # Main text widget
        self.prelog_panel = self.create_panel(prelog_frame)
        self.postlog_panel = self.create_panel(postlog_frame)

        # Attach scrollbars to both text widgets
        self.prelog_panel.config(
            yscrollcommand=self.on_pre_panel_vertical,
            xscrollcommand=self.on_pre_panel_horizontal,
        )
        self.postlog_panel.config(
            yscrollcommand=self.on_post_panel_vertical,
            xscrollcommand=self.on_post_panel_horizontal,
        )

        self.prelog_line_num.config(yscrollcommand=self.on_line_number_scroll)
        self.postlog_line_num.config(yscrollcommand=self.on_line_number_scroll)

        self.config_highlights(self.prelog_panel)
        self.config_highlights(self.postlog_panel)
        
        self.prelog_line_num.pack(side=tk.LEFT, fill=tk.Y)
        self.prelog_panel.pack(side=tk.LEFT, fill=tk.BOTH)
        
        self.postlog_line_num.pack(side=tk.LEFT, fill=tk.Y)
        self.postlog_panel.pack(side=tk.LEFT, fill=tk.BOTH)

    def create_panel(self, parent):
        return tk.Text(
            parent, wrap=tk.NONE, state=tk.DISABLED, font=self.text_font, width=200
        )

    def create_line_numbers(self, parent):
        return tk.Text(
            parent,
            width=4,
            padx=4,
            takefocus=0,
            border=0,
            background="lightgray",
            state=tk.DISABLED,
            wrap=tk.NONE,
            font=self.text_font,
            cursor="arrow",
        )

    def config_highlights(self, panel):
        panel.tag_configure("highlight", background="lightyellow")
        panel.tag_configure("add", background=Const.ADDED_COLOR)
        panel.tag_configure("remove", background=Const.REMOVED_COLOR)
        panel.tag_configure("replace", background=Const.CHANGED_COLOR)
        panel.tag_configure("equal", background="")
        panel.tag_configure("add_blank", background=Const.BLANK_COLOR)
        panel.tag_configure("remove_blank", background=Const.BLANK_COLOR)
    
    def clear_line_numbers(self):
        self.prelog_line_num.config(state=tk.NORMAL)
        self.postlog_line_num.config(state=tk.NORMAL)
        
        self.prelog_line_num.delete(1.0, tk.END)
        self.postlog_line_num.delete(1.0, tk.END)
    
    def _sync_scroll(self):
        pre_first, pre_last = self.prelog_panel.yview()
        post_first, post_last = self.postlog_panel.yview()
        
        self.prelog_line_num.yview_moveto(pre_first)
        self.postlog_line_num.yview_moveto(post_first)
        
        self.vert_scrollbar.set(pre_first, pre_last)
        
    def update_panel_line_numbers(self):
        self.sync_line_numbers(self.prelog_line_num, self.prelog_panel)
        self.sync_line_numbers(self.postlog_line_num, self.postlog_panel)
        
    def sync_line_numbers(self, line_numbers, panel):
        line_numbers.config(state=tk.NORMAL)
        line_numbers.delete(1.0, tk.END)
        
        line_count = int(panel.index("end").split(".")[0])
        lines = "\n".join(str(i) for i in range(1, line_count + 1))
        width = max(4, len(str(line_count)))
        
        line_numbers.insert(1.0, lines)
        line_numbers.config(state=tk.DISABLED, width=width)
        line_numbers.tag_add("right", 1.0, "end")
        
        self._sync_scroll()
        
    def on_line_number_scroll(self, *args):
        self.vert_scrollbar.set(*args)
        self.prelog_panel.yview_moveto(args[0])
        self.postlog_panel.yview_moveto(args[0])
        
    def on_vertical_scroll(self, *args):
        # Scroll both text widget vertically
        self.prelog_panel.yview(*args)
        self.postlog_panel.yview(*args)
        
    def on_horizontal_scroll(self, *args):
        # Scroll both text widget horizontally
        self.prelog_panel.xview(*args)
        self.postlog_panel.xview(*args)
        
    def on_pre_panel_vertical(self, *args):
        self.vert_scrollbar.set(*args)
        self.postlog_panel.yview_moveto(args[0])
        self.postlog_line_num.yview_moveto(args[0])
        
    def on_post_panel_vertical(self, *args):
        self.vert_scrollbar.set(*args)
        self.prelog_panel.yview_moveto(args[0])
        self.prelog_line_num.yview_moveto(args[0])
    
    def on_pre_panel_horizontal(self, *args):
        self.horiz_scrollbar.set(*args)
        self.postlog_panel.xview_moveto(args[0])
        
    def on_post_panel_horizontal(self, *args):
        self.horiz_scrollbar.set(*args)
        self.prelog_panel.xview_moveto(args[0])
        
    def set_normal_state(self):
        self.prelog_panel.config(state=tk.NORMAL)
        self.postlog_panel.config(state=tk.NORMAL)
        
    def set_disabled_state(self):
        self.prelog_panel.config(state=tk.DISABLED)
        self.postlog_panel.config(state=tk.DISABLED)