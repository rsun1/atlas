import json 
from atlas.app.config import AUDIT_LOG

def record(event):
    with open(AUDIT_LOG,"a", encoding = "utf-8") as f:
        f.write(event.model_dump_json() + "\n")

def tail(limit=200):
    if not AUDIT_LOG.exists():
        return []
    lines = AUDIT_LOG.read_text(encoding="utf-8").splitlines()
    results= []
    for line in lines[-limit:]:
        try:
            results.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return results