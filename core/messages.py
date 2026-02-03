from tkinter import messagebox
from core.syslogger import logger
from core.constants import Const

MESSAGE_MAP = {
    # Log collection
    Const.LOG_COLL_GOOD:      ("info", "Log collection", "Log collection is completed."),
    Const.LOG_COLL_BAD:       ("error", "Log collection", "Log collection failed."),
    Const.LOG_COLL_SKIP:      ("error", "Log collection", "No reachable network device."),
    Const.LOG_COLL_STOPPED:   ("warning", "Log collection", "Log collection stopped."),

    # Log comparison
    Const.COMP_LOG_GOOD:      ("info", "Log comparison", "Log comparison is completed."),
    Const.COMP_LOG_BAD:       ("error", "Log comparison", "Log comparison failed."),
    Const.COMP_LOG_SKIP:      ("error", "Log comparison", "Invalid log comparison."),
    Const.COMP_PRE_LOG_EMP:   ("error", "Log comparison", "No pre-log data found for comparison."),
    Const.COMP_POST_LOG_EMP:  ("error", "Log comparison", "No post-log data found for comparison."),

    # Pre/Post log loading
    Const.NO_SH_CMD_CONF_PRE:        ("error", "Select Pre-log folder", "All hostnames have no configured show commands."),
    Const.NO_SH_CMD_CONF_POST:       ("error", "Select Post-log folder", "All hostnames have no configured show commands."),
    Const.NO_VALID_LOG_HOST_PRE:     ("error", "Select Pre-log folder", "No valid hostnames were detected in the logs you uploaded."),
    Const.NO_VALID_LOG_HOST_POST:    ("error", "Select Post-log folder", "No valid hostnames were detected in the logs you uploaded."),
    Const.PRE_PATH_INVALID_FILENAME_ERR:  ("error", "Select Pre-log folder", "No valid network logs were found in the selected pre-log folder."),
    Const.POST_PATH_INVALID_FILENAME_ERR: ("error", "Select Post-log folder", "No valid network logs were found in the selected post-log folder."),

    # Export
    Const.EXP_GOOD:         ("info", "Export logs", "Logs exported successfully."),
    Const.EXP_BAD:          ("error", "Export logs", "Logs export failed."),
    Const.EXP_NO_DATA:      ("error", "Export logs", "There are no logs available for export."),
    
    # Initialization
    Const.INIT_NO_HOST_DTC: ("error", "Initialization error", "No network devices detected for analysis."),
}


def show_message(msg_type: str, **kwargs):
    if msg_type == Const.WINDOW_ERROR:
        width = kwargs.get("screen_width", "?")
        height = kwargs.get("screen_height", "?")

        msg = (
            f"Your screen resolution is {width}x{height}, "
            f"which is below the minimum required resolution of {Const.WINDOW_WIDTH}x{Const.WINDOW_HEIGHT}.\n\n"
            "Please adjust your display settings to continue."
        )
        messagebox.showerror("Resolution error", msg)
        logger.error(msg)
        return

    if msg_type == Const.INIT_ERROR:
        msg = kwargs.get("msg", "Unknown initialization error.")
        messagebox.showerror("Initialization error", msg)
        logger.error(msg)
        return

    if msg_type == Const.EXP_CMP_ERR:
        msg = kwargs.get("error", "Unknown error.")
        messagebox.showerror("Export Error", msg)
        logger.error(msg)
        return
    
    if msg_type in MESSAGE_MAP:
        level, title, msg = MESSAGE_MAP[msg_type]
        if level == "info":
            messagebox.showinfo(title, msg)
            logger.info(msg)
        elif level == "error":
            messagebox.showerror(title, msg)
            logger.error(msg)
        elif level == "warning":
            messagebox.showwarning(title, msg)
            logger.warning(msg)
    else:
        logger.warning(f"Unknown message type: {msg_type}")
