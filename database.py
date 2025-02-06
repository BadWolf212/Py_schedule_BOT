import json
import os
from typing import Dict, Any
from constants import USER_DATA_FILE

def load_user_data() -> Dict[str, Any]:
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'r') as file:
            return json.load(file)
    return {}

def save_user_data(data: Dict[str, Any]) -> None:
    with open(USER_DATA_FILE, 'w') as file:
        json.dump(data, file, indent=2)
