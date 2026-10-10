import os
from typing import List

API_ID = int(os.environ.get("API_ID", ""))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
MONGO_URI = os.environ.get("MONGO_URI", "")
DATABASE_CHANNEL_ID = int(os.environ.get("DATABASE_CHANNEL_ID", ""))
ADMIN_ID = int(os.environ.get("ADMIN_ID", "1255023013"))
PICS = os.environ.get("PICS", "https://i.ibb.co/MDssddJp/pic.jpg https://i.ibb.co/n8fQ2xcx/pic.jpg").split()
LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", ""))
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "TechifyBots")  # Without @
IS_FSUB = os.environ.get("IS_FSUB", "False").lower() == "true"  # Set "True" to enable force subscribe
AUTH_CHANNELS = list(map(int, os.environ.get("AUTH_CHANNELS", "").split()))  # Add multiple channel IDs
AUTH_REQ_CHANNELS = list(map(int, os.environ.get("AUTH_REQ_CHANNELS", "").split()))  # Add multiple channel IDs
FSUB_EXPIRE = int(os.environ.get("FSUB_EXPIRE", "2"))  # Minutes, 0 = no expiry
DATABASE_CHANNEL_LOG = int(os.environ.get("DATABASE_CHANNEL_LOG", ""))
FREE_VIDEO_DURATION = int(os.environ.get("FREE_VIDEO_DURATION", "240"))
PING_URL = os.environ.get("PING_URL", "")  # Service URL for keep-alive
VERSION = os.environ.get("VERSION", "3.0")
