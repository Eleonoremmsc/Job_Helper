import datetime
from datetime import datetime
from create_account import get_worksheet
import uuid
import json

SPREADSHEET_NAME = "Job_Assistant_Users"
SHEET_NAME = "Users"

def save_user_to_sheet(user_data):
    sheet = get_worksheet(SPREADSHEET_NAME, SHEET_NAME)
    email = user_data.get("email", "").strip()
    all_rows = sheet.get_all_records()
    
    for i, row in enumerate(all_rows, start=2):
        if row["Email"] == email:
            sheet.update(f"B{i}:N{i}", [[
                row.get("First_Name", ""),
                row.get("Last_Name", ""),
                row.get("Email", ""),
                row.get("Hashed_Password"),
                row.get("phone", ""),
                row.get("age", ""),
                row.get("location", ""),
                row.get("description", ""),
                row.get("education", ""),
                row.get("skills", ""),
                row.get("experience", ""),
                json.dumps(user_data.get("accepted_suggestions", [])),
                row.get("last_updated", datetime.now().isoformat()),
            ]])

def load_user_from_sheet(email):
    sheet = get_worksheet(SPREADSHEET_NAME, SHEET_NAME)
    rows = sheet.get_all_records()
    for row in rows:
        if row["Email"] == email:
            # Parse accepted_suggestions back from JSON
            if isinstance(row.get("accepted_suggestions"), str):
                try:
                    row["accepted_suggestions"] = json.loads(row["accepted_suggestions"])
                except:
                    row["accepted_suggestions"] = []
            return row
    return {}

def sync_to_sheet(user_data):
    sheet = get_worksheet(SPREADSHEET_NAME, SHEET_NAME)
    emails = [row[3] for row in sheet.get_all_values()[1:]]  # 4th col = Email

    # Avoid duplicates
    if user_data.get("email") in emails:
        return  # Already exists

    sheet.append_row([
        user_data.get("id", str(uuid.uuid4())),
        user_data.get("first_name", ""),
        user_data.get("last_name", ""),
        user_data.get("email", ""),
        user_data.get("hashed_password", ""),
        user_data.get("phone", ""),
        user_data.get("age", ""),
        user_data.get("location", ""),
        user_data.get("description", ""),
        user_data.get("education", ""),
        user_data.get("skills", ""),
        user_data.get("experience", ""),
        json.dumps(user_data.get("accepted_suggestions", [])),
        user_data.get("last_updated", datetime.now().isoformat()),
        user_data.get("created_at", datetime.now().isoformat())
    ])
    