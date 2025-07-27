from tkinter import messagebox
from core.syslogger import logger
from core.constants import Const

def show_message(msg_type: str, **kwargs):
    match msg_type:
        case Const.LOG_COLL_GOOD:
            msg = "Log collection is complted."
            messagebox.showinfo("Log collection", msg)
            logger.info(msg)
            
        case Const.LOG_COLL_BAD:
            msg = "Log collection is failed."
            messagebox.showerror("Log collection", msg)
            logger.error(msg)
            
        case Const.LOG_COLL_SKIP:
            msg = "No reachable network device."
            messagebox.showerror("Log collection", msg)
            logger.error(msg)
            
        case Const.COMP_LOG_GOOD:
            msg = "Log comparison is completed."
            messagebox.showinfo("Log comparison", msg)
            logger.info(msg)
            
        case Const.COMP_LOG_BAD:
            msg = "Log comparison is failed."
            messagebox.showerror("Log comparison", msg)
            logger.error(msg)
            
        case Const.COMP_LOG_SKIP:
            msg = "Invalid log comparison."
            messagebox.showerror("Log comparison", msg)
            logger.error(msg)
            
        case Const.COMP_PRE_LOG_EMP:
            msg = "No pre-log data found for comparison."
            messagebox.showerror("Log comparison", msg)
            logger.error(msg)
            
        case Const.COMP_POST_LOG_EMP:
            msg = "No post-log data found for comparison."
            messagebox.showerror("Log comparison", msg)
            logger.error(msg)
            
        case Const.NO_SH_CMD_CONF_POST:
            msg = "All hostnames have no configured show commands."
            messagebox.showerror("Select Post-log folder", msg)
            logger.error(msg)
            
        case Const.NO_SH_CMD_CONF_PRE:
            msg = "All hostnames have no configured show commands."
            messagebox.showerror("Select Pre-log folder", msg)
            logger.error(msg)
            
        case Const.NO_VALID_LOG_HOST_POST:
            msg = "No valid hostnames were detected in the logs you uploaded."
            messagebox.showerror("Select Post-log folder", msg)
            logger.error(msg)
            
        case Const.NO_VALID_LOG_HOST_PRE:
            msg = "No valid hostnames were detected in the logs you uploaded."
            messagebox.showerror("Select Pre-log folder", msg)
            logger.error(msg)
            
        case Const.EXP_GOOD:
            msg = "Logs exported successfully."
            messagebox.showinfo("Export logs", msg)
            logger.info(msg)
            
        case Const.EXP_BAD:
            msg = "Logs export faield."
            messagebox.showerror("Export logs", msg)
            logger.error(msg)
            
        case Const.EXP_NO_DATA:
            msg = "There are no logs available for export."
            messagebox.showerror("Export logs", msg)
            logger.error(msg)
            
        case Const.PRE_PATH_INVALID_FILENAME_ERR:
            msg = "No valid network logs were found in the selected pre-log-folder."
            messagebox.showerror("Select Pre-log folder", msg)
            logger.error(msg)
            
        case Const.POST_PATH_INVALID_FILENAME_ERR:
            msg = "No valid network logs were found in the selected post-log-folder."
            messagebox.showerror("Select Post-log folder", msg)
            logger.error(msg)
            
        case Const.WINDOW_ERROR:
            msg = (
                f"Your screen resolution is {kwargs["screen_width"]}x{kwargs["screen_height"]}, "
                f"which is below the minimum required resolution of {Const.WINDOW_WIDTH}x{Const.WINDOW_HEIGHT}.\n\n"
                "Please adjust your display settings to continue."
            )
            messagebox.showerror("Resolution error", msg)
            logger.error(msg)
            
        case Const.INIT_ERROR:
            messagebox.showerror("Initialization error", kwargs["msg"])
            logger.error(kwargs["msg"])
            
        case Const.INIT_NO_HOST_DTC:
            msg = "No network devices detected for analysis."
            messagebox.showerror("Initialization error", msg)
            logger.error(msg)
            
            