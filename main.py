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
    duration_raw = data.get("duration")
    
    # Handle duration - could be None, string "None", number, time string (HH:MM:SS), or missing
    if duration_raw is None or duration_raw == "None" or duration_raw == "":
        duration = None
    else:
        try:
            # First try to parse as a number (seconds)
            duration = float(duration_raw)
            # Only consider valid if it's a positive number
            if duration < 0:
                duration = None
        except (ValueError, TypeError):
            # If not a number, try to parse as time string (HH:MM:SS or MM:SS)
            try:
                if isinstance(duration_raw, str) and ':' in duration_raw:
                    # Parse time format like "00:00:10" or "00:10"
                    time_parts = duration_raw.strip().split(':')
                    if len(time_parts) == 3:  # HH:MM:SS
                        hours, minutes, seconds = map(float, time_parts)
                        duration = hours * 3600 + minutes * 60 + seconds
                    elif len(time_parts) == 2:  # MM:SS
                        minutes, seconds = map(float, time_parts)
                        duration = minutes * 60 + seconds
                    else:
                        duration = None
                else:
                    duration = None
            except (ValueError, TypeError):
                duration = None
    
    # Check if target is empty/blank (which indicates "No Value" calls)
    target_is_empty = (target_name == "" or target_name is None or target_name.strip() == "")
    
    # Check if duration is 10 seconds or under (must be a valid positive number)
    # Don't treat missing/None duration as 0 - only catch if duration is explicitly provided
    duration_short = duration is not None and isinstance(duration, (int, float)) and 0 < duration <= 10
    
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
    duration_raw = data.get("duration")
    
    # Handle duration - could be None, string "None", number, time string (HH:MM:SS), or missing
    if duration_raw is None or duration_raw == "None" or duration_raw == "":
        duration = None
    else:
        try:
            # First try to parse as a number (seconds)
            duration = float(duration_raw)
            # Only consider valid if it's a positive number
            if duration < 0:
                duration = None
        except (ValueError, TypeError):
            # If not a number, try to parse as time string (HH:MM:SS or MM:SS)
            try:
                if isinstance(duration_raw, str) and ':' in duration_raw:
                    # Parse time format like "00:00:10" or "00:10"
                    time_parts = duration_raw.strip().split(':')
                    if len(time_parts) == 3:  # HH:MM:SS
                        hours, minutes, seconds = map(float, time_parts)
                        duration = hours * 3600 + minutes * 60 + seconds
                    elif len(time_parts) == 2:  # MM:SS
                        minutes, seconds = map(float, time_parts)
                        duration = minutes * 60 + seconds
                    else:
                        duration = None
                else:
                    duration = None
            except (ValueError, TypeError):
                duration = None
    
    # Log the target value and duration for debugging
    duration_display = f"{duration}s" if duration is not None else "None/invalid"
    logging.info(f"Filter check - Target: '{target_name}' (empty = No Value call), Duration (raw): {duration_raw}, Duration (parsed): {duration_display}")
    
    # Check if target is empty/blank (which indicates "No Value" calls)
    target_is_empty = (target_name == "" or target_name is None or target_name.strip() == "")
    
    # Check if duration is 10 seconds or under (must be a valid positive number)
    # Don't treat missing/None duration as 0 - only catch if duration is explicitly provided
    duration_short = duration is not None and isinstance(duration, (int, float)) and 0 < duration <= 10
    
    logging.info(f"Target is empty: {target_is_empty}, Duration <= 10s: {duration_short} (duration must be > 0 and <= 10)")
    
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
