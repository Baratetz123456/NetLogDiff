def set_window_center(window):
    window.update_idletasks()
    width = window.winfo_width()
    
    form_width = window.winfo_rootx() - window.winfo_x()
    window_width = width + 2 * form_width
    
    height = window.winfo_height()
    titlebar_height = window.winfo_rooty() - window.winfo_y()
    window_height = height + titlebar_height + form_width
    
    x = window.winfo_screenwidth() // 2 - window_width // 2
    y = window.winfo_screenheight() // 2 - window_height // 2
    
    window.geometry(f"{width}x{height}+{x}+{y}")
    window.deiconify()
    