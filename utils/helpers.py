import json
import os
import datetime
from utils.gspread_client import get_gspread_client

DATA_FILE = "user_data.json"

def load_user_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_user_data(all_data):
    with open(DATA_FILE, "w") as f:
        json.dump(all_data, f, indent=2)
        
def sync_to_sheet(user_data):
    client = get_gspread_client()
    sheet = client.open("Job_Assistant_Users").worksheet("Users")
    
    existing_ids = sheet.col_values(1)
    
    if user_data["id"] in existing_ids:
        return 

    sheet.append_row([
        user_data.get("first_name", ""),
        user_data.get("last_name", ""),
        user_data.get("email", ""),
        user_data.get("phone", ""),
        user_data.get("age", ""),
        user_data.get("location", ""),
        datetime.now().isoformat()
    ])

