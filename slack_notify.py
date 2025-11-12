import requests
from config import SLACK_WEBHOOK_URL
import logging

def send_slack_alert(caller_id, time_of_call, sheet_link, call_type):
    try:
        # Determine emoji and title based on call type
        if call_type == "No Value":
            emoji = "📞"
            title = "New No Value Call Logged"
        elif call_type == "Short Duration":
            emoji = "⏱️"
            title = "New Short Duration Call Logged (≤10s)"
        else:
            emoji = "📞"
            title = "New Call Logged"
        
        message = {
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"{emoji} *{title}*\n\n• *Caller ID:* `{caller_id}`\n• *Call Type:* `{call_type}`\n• *Time:* `{time_of_call} EST`\n• *Campaign:* `{caller_id.split('_')[0] if '_' in caller_id else 'Unknown'}`"
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
        
        logging.info(f"Successfully sent Slack notification for caller {caller_id} with call type {call_type}")
        return True
        
    except Exception as e:
        logging.error(f"Error sending Slack notification: {str(e)}")
        return False
