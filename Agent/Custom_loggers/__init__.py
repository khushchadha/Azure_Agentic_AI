import logging
import os
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler

# Create logs directory
os.makedirs("logs", exist_ok=True)

# Log format
log_format = (
    "%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - "
    "%(lineno)d - %(message)s"
)

# File handler (daily rotation)
current_date = datetime.now().strftime("%Y-%m-%d")
file_handler = TimedRotatingFileHandler(
    f"logs/app_{current_date}.log", when="midnight", interval=1
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
 