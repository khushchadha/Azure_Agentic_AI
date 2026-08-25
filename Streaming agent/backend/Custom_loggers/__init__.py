import logging
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.paths import LOGS_DIR
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler

# Create logs directory (always inside backend/, not the cwd)
os.makedirs(LOGS_DIR, exist_ok=True)

# Log format
log_format = (
    "%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - "
    "%(lineno)d - %(message)s"
)

# File handler (daily rotation)
current_date = datetime.now().strftime("%Y-%m-%d")
file_handler = TimedRotatingFileHandler(
    os.path.join(LOGS_DIR, f"app_{current_date}.log"), when="midnight", interval=1
)
file_handler.suffix = "%Y-%m-%d"
file_handler.setFormatter(logging.Formatter(log_format))

# Stream handler
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(logging.Formatter(log_format))

# Configure root logger
logging.basicConfig(level=logging.INFO, handlers=[file_handler, stream_handler])
logger = logging.getLogger()

# Silence noisy loggers (optional)
noisy_loggers = [
    "azure",
    "azure.core.pipeline",
    "azure.openai",
]
for name in noisy_loggers:
    logging.getLogger(name).setLevel(logging.WARNING)

# Disable all logging globally (optional, for production)
# logging.disable(logging.CRITICAL)
 