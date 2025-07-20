import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime
import pytz

__timezone = pytz.timezone("Asia/Manila")
data_time = datetime.now(__timezone)

# Create logs directory
log_folder = "system_logs"
log_file = f"app_{data_time.strftime('%Y%m%d_%H%M%S')}.log"
log_path = os.path.join(log_folder, log_file)
os.makedirs(log_folder, exist_ok=True)

# Create logger
logger = logging.getLogger("NetLogger")
logger.setLevel(logging.DEBUG)

# Log format
formatter = logging.Formatter(
    "%(asctime)s [%(name)s][%(levelname)s][%(funcName)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# Rotating file handler
file_handler = RotatingFileHandler(log_path, maxBytes=5 * 1024 * 1024, backupCount=3)

logger.addHandler(console_handler)
logger.addHandler(file_handler)
