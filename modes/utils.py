import os, hashlib, json
from datetime import datetime

def hash_file(path):
    return hashlib.md5(open(path, "rb").read()).hexdigest() if os.path.exists(path) else None

def clear_temp(files):
    for path in files:
        if os.path.exists(path): os.remove(path)

def log_event(logfile, data):
    os.makedirs("logs", exist_ok=True)
    entry = {"timestamp": datetime.utcnow().isoformat(), **data}
    with open(f"logs/{logfile}", "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
