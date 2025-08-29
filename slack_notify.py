import requests
from config import SLACK_WEBHOOK_URL
import logging

def send_slack_alert(caller_id, time_of_call, sheet_link):
    try:
        message = {
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"📞 *New No Value Call Logged*\n\n• *Caller ID:* `{caller_id}`\n• *Time:* `{time_of_call} UTC`\n• *Campaign:* `{caller_id.split('_')[0] if '_' in caller_id else 'Unknown'}`"
                    }
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "📊 View Google Sheet"
                            },
                            "url": sheet_link,
                            "style": "primary"
                        }
                    ]
                }
            ]
        }
        
        response = requests.post(SLACK_WEBHOOK_URL, json=message, timeout=10)
        response.raise_for_status()
        
        logging.info(f"Successfully sent Slack notification for caller {caller_id}")
        return True
        
    except Exception as e:
        logging.error(f"Error sending Slack notification: {str(e)}")
        return False
