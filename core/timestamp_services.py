import pytz
from datetime import datetime
from typing import Final


class TimestampService:
    LOCATION: Final = "Asia/Manila"
    TIMESTAMP_FORMAT: Final = "%Y%m%d_%H%M%S"
    
    def __init__(self):
        self.__timezone = pytz.timezone(self.LOCATION)
        self._timestamp = datetime.now(self.__timezone)
        
    def refresh(self) -> None:
        """Refresh the stored timestamp to current time."""
        self._timestamp = datetime.now(self.__timezone)
        
    def generate_timestamp(self) -> str:
        """Generate timestamp string in 'YYYYMMDD_HHMMSS' format."""
        return self._timestamp.strftime(self.TIMESTAMP_FORMAT)
    
    def generate_by_hm(self) -> str:
        """Generate timestamp string with hour and minute only 'HHMM'."""
        return self._timestamp.strftime("%H%M")
    
    def generate_by_date(self) -> str:
        """Generate timestamp string with date only 'YYYYMMDD'."""
        return self._timestamp.strftime("%Y%m%d")
    
    def generate_readable_format(self) -> str:
        """Generate human-readable timestamp e.g. 'Jul 28, 2025 03:45 PM'."""
        return self._timestamp.strftime("%b %d, %Y %I:%M %p")
        

shared_timestamp_service = TimestampService()
