"""Central path helpers so the app works no matter where it is launched from."""
import os

# .../Streaming agent/backend
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# .../Streaming agent
PROJECT_DIR = os.path.dirname(BACKEND_DIR)

PROMPTS_DIR = os.path.join(BACKEND_DIR, "prompts")
LOGS_DIR = os.path.join(BACKEND_DIR, "logs")
FRONTEND_DIR = os.path.join(PROJECT_DIR, "frontend")
