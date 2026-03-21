import json

def load_results(path="../backend/output/result.json"):
    try:
        with open(path, "r") as f:
            data = json.load(f)
        return data.get("results", [])
    except Exception as e:
        return []