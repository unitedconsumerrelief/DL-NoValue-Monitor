import os
from dotenv import load_dotenv

load_dotenv()

# Ringba webhook filters
RINGBA_FILTERS = {
    "campaign_name": os.getenv("RINGBA_CAMPAIGN_NAME", "SPANISH DEBT | 1.0 STANDARD"),
    "target_name": os.getenv("RINGBA_TARGET_NAME", "-no value-")
}

# Google Sheets configuration
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID", "19F4ZpVE9pzOToxxi0IiNR9K5LgQJmU6ylS-RF4aA__I")
GOOGLE_SHEET_TAB = os.getenv("GOOGLE_SHEET_TAB", "Sheet1")
GOOGLE_CREDS_FILE = os.getenv("GOOGLE_CREDS_FILE", "ringba-no-values-469904-c7faf20383e2.json")

# Slack configuration
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "https://hooks.slack.com/services/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")

# Flask configuration for local server
FLASK_ENV = os.getenv("FLASK_ENV", "production")  # Changed to production for server
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "False").lower() == "true"  # Changed to False for server
HOST = os.getenv("HOST", "0.0.0.0")  # Allow external connections
PORT = int(os.getenv("PORT", 5000))
