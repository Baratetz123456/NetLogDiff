import sys
import os
from core.syslogger import logger

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from view.view import MainView

if __name__ == "__main__":
    logger.info("Start NetLogger")
    app = MainView()
    app.mainloop()
    