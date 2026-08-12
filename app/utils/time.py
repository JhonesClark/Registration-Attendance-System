from datetime import datetime
from zoneinfo import ZoneInfo

# Centralized Philippines timezone helper
PH_TZ = ZoneInfo("Asia/Manila")


def now_ph():
    """Return the current timezone-aware datetime in Asia/Manila."""
    return datetime.now(PH_TZ)
