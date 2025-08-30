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

def passes_filter(data):
    """Check if the webhook data matches our filter criteria"""
    campaign_id = data.get("campaignId", "")  # Ringba sends campaignId
    expected_campaign_id = RINGBA_FILTERS["campaign_id"]
    target_name = data.get("targetName", "")
    
    # Log the actual values for debugging
    logging.info(f"Filter check - Campaign ID: '{campaign_id}' vs '{expected_campaign_id}'")
    logging.info(f"Filter check - Target: '{target_name}' (empty = No Value call)")
    
    # Check if campaign ID matches exactly
    campaign_matches = campaign_id == expected_campaign_id
    
    # Check if target is empty/blank (which indicates "No Value" calls)
    # We want calls where target is empty, not where it has a value
    target_is_empty = (target_name == "" or target_name is None or target_name.strip() == "")
    
    logging.info(f"Campaign ID match: {campaign_matches}, Target is empty: {target_is_empty}")
    
    # Return true if: campaign ID matches AND target is empty (No Value call)
    return campaign_matches and target_is_empty

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
        logging.info(f"Received webhook: campaignName={data.get('campaignName')}, targetName={data.get('targetName')}")

        if not passes_filter(data):
            logging.info("Webhook filtered out - doesn't match criteria")
            return jsonify({"status": "ignored", "reason": "filtered"}), 200

        # Extract call data
        caller_id = data.get("callerId", "Unknown")
        time_of_call = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

        # Append to Google Sheet
        sheet_success = append_row_to_sheet(time_of_call, caller_id)
        if not sheet_success:
            logging.error("Failed to append to Google Sheet")
            return jsonify({"error": "Failed to update Google Sheet"}), 500

        # Send Slack notification
        sheet_link = f"https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID}"
        slack_success = send_slack_alert(caller_id, time_of_call, sheet_link)
        
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
