import json
import os

def load_results(path=None):
    if path is None:
        path = os.path.join(os.path.dirname(__file__), "..", "data", "result.json")
    
    try:
        with open(path, "r") as f:
            data = json.load(f)
        return data.get("results", [])
    except Exception as e:
        return []