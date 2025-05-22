import datetime
from datetime import datetime
from create_account import get_worksheet
from utils.prepare_user_data import prepare_user_data_for_saving
import uuid
import json

SPREADSHEET_NAME = "Job_Assistant_Users"
SHEET_NAME = "Users"


def save_user_to_sheet(user_data):
    sheet=get_worksheet(SPREADSHEET_NAME, SHEET_NAME)
    records = get_all_user_records()
    headers= sheet.row_values(1)
    for idx, row in enumerate(records):
        if row.get("Email", "").strip().lower()==user_data.email.strip().lower():
            values = prepare_user_data_for_sheet(user_data, headers)
            sheet.update(f"A{idx+2}", [values])
            return
    safe_user_data = prepare_user_data_for_saving(user_data, headers)
    sheet.append_row(values)
    #            row.get("First_Name", ""),
    #            row.get("Last_Name", ""),
    #            row.get("Email", ""),
    #            row.get("Hashed_Password"),
    #            row.get("phone", ""),
    #            row.get("age", ""),
    #            row.get("location", ""),
    #            row.get("description", ""),
    #            row.get("education", ""),
    #            row.get("skills", ""),
    #            row.get("experience", ""),
    #            row.get("hobbies", ""),
    #            row.get("languages", ""),
    #            json.dumps(user_data.get("accepted_suggestions", [])),
    #            row.get("last_updated", datetime.now().isoformat()),
    #        ]])

def load_user_from_sheet(email):
    if not email:
        return {}
    sheet = get_worksheet(SPREADSHEET_NAME, SHEET_NAME)
    rows = get_all_user_records()
    for row in rows:
        if row.get("Email", "").strip().lower()==email.strip().lower():
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
    all_rows = get_all_user_records()
    headers= sheet.row_values(1)
    
    user_data["accepted_suggestions"] = json.dumps(user_data.get("accepted_suggestions", []))
    #row_data = []
    #for header in headers:
    #    val = user_data.get(header, "")
    #    if isinstance(val, list):
    #        val = json.dumps(val, ensure_ascii=False)
    #        row_data.append(val)
            
    for i, row in enumerate(all_rows):
        if row.get("Email", "").strip().lower() == user_data.get("email","").strip().lower():
            values = prepare_user_data_for_sheet(user_data, headers)
            sheet.update(f"A{i+2}", [values])  # Update in-place
            return
    values = prepare_user_data_for_sheet(user_data, headers)
    sheet.append_row(values)
    # Step 2: If not found, append a new row
#    sheet.append_row(list(user_data.values()))
    #sheet.append_row([
    #    user_data.get("id", str(uuid.uuid4())),
    #    user_data.get("first_name", ""),
    #    user_data.get("last_name", ""),
    #    user_data.get("email", ""),
    #    user_data.get("hashed_password", ""),
    #    user_data.get("phone", ""),
    #    user_data.get("age", ""),
    #    user_data.get("location", ""),
    #    user_data.get("description", ""),
    #    user_data.get("education", ""),
    #    user_data.get("skills", ""),
    #    user_data.get("experience", ""),
    #    user_data.get("hobbies", ""),
    #    user_data.get("languages", ""),
    #    json.dumps(user_data.get("accepted_suggestions", [])),
    #    user_data.get("last_updated", datetime.now().isoformat()),
    #    user_data.get("created_at", datetime.now().isoformat())
    #])

def get_all_user_records():
    sheet = get_worksheet(SPREADSHEET_NAME, SHEET_NAME)
    raw = sheet.get_all_values()
    headers = raw[0]
    records = []
    
    for row in raw[1:]:
        row += [""] * (len(headers) - len(row))
        record = dict(zip(headers, row))
        records.append(record)
        
    return records

import json
from datetime import datetime

def prepare_user_data_for_sheet(user_data, headers):
    safe_data = []
    for header in headers:
        value = user_data.get(header, "")
        if isinstance(value, datetime):
            value = value.isoformat()
        elif isinstance(value, list):
            value = json.dumps(value)
        safe_data.append(value)
    return safe_data
