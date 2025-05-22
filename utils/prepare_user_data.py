import json
from datetime import datetime

def prepare_user_data_for_saving(user_data):
    # Ensure no non-serializable data (like datetime)
    safe_data = {}
    for key, value in user_data.items():
        if isinstance(value, datetime):
            safe_data[key] = value.isoformat()
        elif isinstance(value, list):
            safe_data[key] = json.dumps(value)  # Save lists as JSON strings
        else:
            safe_data[key] = value
    return safe_data


