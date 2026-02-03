from typing import Final

class Const:
    WINDOW_ERROR: Final = "window_error"
    
    TITLE: Final = "NetLogDiff"
    COMPARISON_LBL: Final = "Log Comparison Result"
    PRE_LOG_LBL: Final = "Pre-log"
    POST_LOG_LBL: Final = "Post-log"
    
    ADDED_COLOR: Final = "#d4fcd4"
    REMOVED_COLOR: Final = "#fcd4d4"
    CHANGED_COLOR: Final = "#fcfcd4"
    ABNORMAL_COLOR: Final = "#ffcdd2"
    BLANK_COLOR: Final = "#a6a6a6"
    
    COLLECT_LOG_BTN: Final = "Collect logs"
    PRE_LOG_FOLDER_BTN: Final = "Select Pre-log Folder"
    POST_LOG_FOLDER_BTN: Final = "Select Post-log Folder"
    COMPARE_BTN: Final = "Compare Start"
    EXPORT_BTN: Final = "Export Result"
    
    PRE_IMPORT_TITLE: Final = "Pre-log path selection"
    POST_IMPORT_TITLE: Final = "Post-log path selection"
    
    PRE_IMP_ERR: Final = "pre_log_import_error"
    POST_IMP_ERR: Final = "post_log_import_error"
    EXP_CMP_ERR: Final = "export_comparison_log_error"
    
    PRE_PATH_EMPTY_ERR: Final = "pre_log_path_empty_error"
    POST_PATH_EMPTY_ERR: Final = "post_log_path_empty_error"
    
    PRE_PATH_NOT_FOUND_ERR: Final = "pre_log_path_not_found_error"
    POST_PATH_NOT_FOUND_ERR: Final = "post_log_path_not_found_error"
    
    PRE_EMPTY_LOG_ERR: Final = "pre_log_empty_error"
    POST_EMPTY_LOG_ERR: Final = "post_log_empty_error"
    
    PRE_PATH_INVALID_FILENAME_ERR: Final = "pre_log_path_invalid_filename_error"
    POST_PATH_INVALID_FILENAME_ERR: Final = "post_log_path_invalid_filename_error"
    
    INVALID_FILENAME_FORMAT_ERR: Final = "invalid_filename_format_error"
    
    EXP_GOOD: Final = "export_success"
    EXP_BAD: Final = "export_failed"
    EXP_NO_DATA: Final = "export_no_data"
    EXP_INVALID_PATH: Final = "export_invalid_path"
    
    LOG_COLL_GOOD: Final = "log_collection_successful"
    LOG_COLL_BAD: Final = "log_collection_failed"
    LOG_COLL_FILE_SAVE_GOOD: Final = "log_collection_file_save_successful"
    LOG_COLL_FILE_SAVE_BAD: Final = "log_collection_file_save_failed"
    LOG_COLL_SKIP: Final = "log_collection_skipped"
    LOG_COLL_STOPPED: Final = "log_collection_stopped"
    
    SSH_CONN: Final = "ssh"
    TELNET_CONN: Final = "telnet"
    
    COMP_LOG_GOOD: Final = "comparison_log_successful"
    COMP_LOG_BAD: Final = "comparison_log_failed"
    COMP_LOG_SKIP: Final = "comparison_log_skipped"
    
    COMP_PRE_LOG_EMP: Final = "comparison_pre_log_empty"
    COMP_POST_LOG_EMP: Final = "comparison_post_log_empty"
    
    COMP_LOG_FILE_SAVE_GOOD: Final = "comparison_log_file_save_successful"
    COMP_LOG_FILE_SAVE_BAD: Final = "comparison_log_file_save_failed"
    
    COMP_PRE_LOG_PARS_EMP: Final = "comparison_pre_log_parsed_empty"
    COMP_POST_LOG_PARS_EMP: Final = "comparison_post_log_parsed_empty"
    
    TAG_A: Final = "add"
    TAG_RM: Final = "remove"
    TAG_RP: Final = "replace"
    TAG_E: Final = "equal"
    TAG_AB: Final = "add_blank"
    TAG_RMB: Final = "remove_blank"
    
    NO_SH_CMD_CONF_PRE: Final = "no_show_commands_configured_prelog"
    NO_SH_CMD_CONF_POST: Final = "no_show_commands_configured_postlog"
    
    NO_VALID_LOG_HOST_PRE: Final = "no_valid_log_hostnames_prelog"
    NO_VALID_LOG_HOST_POST: Final = "no_valid_log_hostnames_postlog"
    
    INIT_ERROR: Final = "initialization_error"
    INIT_NO_HOST_DTC: Final = "initialization_no_host_detected"