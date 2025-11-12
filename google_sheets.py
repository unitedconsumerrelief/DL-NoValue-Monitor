import datetime
import gspread
import json
import os
from google.oauth2.service_account import Credentials
from config import GOOGLE_SHEET_ID, GOOGLE_SHEET_TAB, GOOGLE_CREDS_FILE
import logging

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

def append_row_to_sheet(time_of_call, caller_id, call_type):
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
        
        # Define correct headers with Call Type column after "Time of call"
        correct_headers = ["Time of call", "Call Type", "CallerID", "Agent Name", "Status", "Notes"]
        
        # Check if headers exist and are correct (without clearing protected cells)
        try:
            existing_headers = sheet.row_values(1)
            if not existing_headers:
                # No headers exist, try to add them (only if row 1 is empty)
                try:
                    sheet.insert_row(correct_headers, 1)
                    logging.info("Created headers in Google Sheet")
                except Exception as header_error:
                    # If we can't insert headers (protected), try to append and log warning
                    logging.warning(f"Could not insert headers (may be protected): {str(header_error)}")
                    # Continue - we'll try to append data anyway
            elif existing_headers != correct_headers:
                # Headers exist but don't match - log warning but don't try to modify protected cells
                logging.warning(f"Headers don't match expected format. Expected: {correct_headers}, Found: {existing_headers}")
                logging.warning("Skipping header update to avoid protected cell errors. Please manually update headers if needed.")
        except Exception as e:
            # If there's an error reading headers, log but continue
            logging.warning(f"Could not read headers (may be protected): {str(e)}")
            # Continue - we'll try to append data anyway
        
        # Find the next empty row (after headers)
        try:
            # Get all values to find the last row
            all_values = sheet.get_all_values()
            next_row = len(all_values) + 1
            
            # If row 1 is empty or doesn't have our headers, use row 2
            if next_row == 1:
                next_row = 2
        except:
            # Fallback: just append (will find next row automatically)
            next_row = None
        
        # Prepare the row data in correct order: [Time of call, Call Type, CallerID, Agent Name, Status, Notes]
        new_row = [time_of_call, call_type, caller_id, "", "", ""]  # Manual fields left empty (Agent Name, Status, Notes)
        
        if next_row:
            # Explicitly update specific cells to ensure correct column alignment
            # Update cells A, B, C (Time, Call Type, CallerID)
            sheet.update(f'A{next_row}:C{next_row}', [[time_of_call, call_type, caller_id]], value_input_option="USER_ENTERED")
            logging.info(f"Successfully added row {next_row} for caller {caller_id} with call type {call_type}")
        else:
            # Fallback to append_row
            sheet.append_row(new_row, value_input_option="USER_ENTERED")
            logging.info(f"Successfully appended row for caller {caller_id} with call type {call_type}")
        return True
        
    except Exception as e:
        logging.error(f"Error appending to Google Sheet: {str(e)}")
        return False
