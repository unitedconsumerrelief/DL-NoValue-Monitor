from flask import Flask, request, jsonify
from datetime import datetime
import logging
from config import RINGBA_FILTERS, GOOGLE_SHEET_ID, FLASK_DEBUG, HOST, PORT
from google_sheets import append_row_to_sheet
from slack_notify import send_slack_alert

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ringba_webhook.log'),
        logging.StreamHandler()
    ]
)

app = Flask(__name__)

def get_call_type(data):
    """Determine the call type based on filter criteria"""
    target_name = data.get("targetName", "")
    duration = data.get("duration", 0)
    
    # Check if target is empty/blank (which indicates "No Value" calls)
    target_is_empty = (target_name == "" or target_name is None or target_name.strip() == "")
    
    # Check if duration is 10 seconds or under
    duration_short = duration is not None and duration <= 10
    
    # Determine call type:
    # - If no target name → "No Value" (regardless of duration)
    # - If has target name AND duration ≤ 10s → "Short Duration"
    if target_is_empty:
        return "No Value"
    elif duration_short:
        return "Short Duration"
    else:
        return None

def passes_filter(data):
    """Check if the webhook data matches our filter criteria"""
    target_name = data.get("targetName", "")
    duration = data.get("duration", 0)
    
    # Log the target value and duration for debugging
    logging.info(f"Filter check - Target: '{target_name}' (empty = No Value call), Duration: {duration}s")
    
    # Check if target is empty/blank (which indicates "No Value" calls)
    target_is_empty = (target_name == "" or target_name is None or target_name.strip() == "")
    
    # Check if duration is 10 seconds or under
    duration_short = duration is not None and duration <= 10
    
    logging.info(f"Target is empty: {target_is_empty}, Duration <= 10s: {duration_short}")
    
    # Return true if:
    # - Target is empty (No Value call) OR
    # - Target exists AND duration <= 10 seconds (Short Duration call)
    return target_is_empty or (not target_is_empty and duration_short)

@app.route("/", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Ringba Webhook Handler",
        "filters": RINGBA_FILTERS,
        "server": "local"
    }), 200

@app.route("/ringba-webhook", methods=["POST"])
def ringba_webhook():
    """Handle incoming Ringba webhook data"""
    try:
        data = request.json
        if not data:
            logging.warning("No JSON data received in webhook")
            return jsonify({"error": "No JSON received"}), 400

        # Log incoming webhook for debugging
        logging.info(f"Received webhook: campaignName={data.get('campaignName')}, targetName={data.get('targetName')}, duration={data.get('duration')}s")

        if not passes_filter(data):
            logging.info("Webhook filtered out - doesn't match criteria")
            return jsonify({"status": "ignored", "reason": "filtered"}), 200

        # Determine call type
        call_type = get_call_type(data)
        logging.info(f"Call type determined: {call_type}")
        # Extract call data
        caller_id = data.get("callerId", "Unknown")
        # Use EST timezone instead of UTC
        from datetime import timezone, timedelta
        est_tz = timezone(timedelta(hours=-5))  # EST is UTC-5
        time_of_call = datetime.now(est_tz).strftime("%Y-%m-%d %H:%M:%S EST")

        # Append to Google Sheet
        sheet_success = append_row_to_sheet(time_of_call, caller_id, call_type)
        if not sheet_success:
            logging.error("Failed to append to Google Sheet")
            return jsonify({"error": "Failed to update Google Sheet"}), 500

        # Send Slack notification
        sheet_link = f"https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID}"
        slack_success = send_slack_alert(caller_id, time_of_call, sheet_link, call_type)
        
        if not slack_success:
            logging.warning("Failed to send Slack notification")

        logging.info(f"Successfully processed call from {caller_id}")
        return jsonify({
            "status": "success",
            "caller_id": caller_id,
            "time": time_of_call
        }), 200

    except Exception as e:
        logging.error(f"Error processing webhook: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    logging.info(f"Starting Ringba Webhook Handler on {HOST}:{PORT}")
    app.run(
        host=HOST,
        port=PORT,
        debug=FLASK_DEBUG
    )
