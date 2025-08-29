import datetime
import gspread
import json
import os
from google.oauth2.service_account import Credentials
from config import GOOGLE_SHEET_ID, GOOGLE_SHEET_TAB, GOOGLE_CREDS_FILE
import logging

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

def append_row_to_sheet(time_of_call, caller_id):
    try:
        # Try to get credentials from environment variable first (for deployment)
        creds_json = os.getenv('GOOGLE_CREDS_JSON')
        if creds_json:
            creds = Credentials.from_service_account_info(json.loads(creds_json), scopes=SCOPES)
        else:
            # Fall back to file-based credentials (for local development)
            creds = Credentials.from_service_account_file(GOOGLE_CREDS_FILE, scopes=SCOPES)
        
        client = gspread.authorize(creds)
        sheet = client.open_by_key(GOOGLE_SHEET_ID).worksheet(GOOGLE_SHEET_TAB)
        
        # Define correct headers
        correct_headers = ["Time of call", "CallerID", "Agent Name", "Status", "Notes"]
        
        # Check if headers exist and are correct
        try:
            existing_headers = sheet.row_values(1)
            if not existing_headers or existing_headers != correct_headers:
                # Clear the sheet and add correct headers
                sheet.clear()
                sheet.append_row(correct_headers)
                logging.info("Created correct headers in Google Sheet")
        except Exception as e:
            # If there's an error reading headers, clear and create new ones
            sheet.clear()
            sheet.append_row(correct_headers)
            logging.info("Created correct headers in Google Sheet (after error)")
        
        new_row = [time_of_call, caller_id, "", "", ""]  # Manual fields left empty
        sheet.append_row(new_row, value_input_option="USER_ENTERED")
        
        logging.info(f"Successfully appended row for caller {caller_id}")
        return True
        
    except Exception as e:
        logging.error(f"Error appending to Google Sheet: {str(e)}")
        return False
