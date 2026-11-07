import threading
from atlas.app.config import MEMORY_FILE
import json
import time

_working: dict[str, list[dict]] = {}
def working_write(task_id, agent, note):
    if task_id not in _working:
        _working[task_id] = []
    _working[task_id].append({"agent":agent, "note":note})
    
def working_read(task_id):
    return _working.get(task_id, [])

def working_context(task_id, max_notes=6):
    notes = working_read(task_id)[-max_notes:]
    return "\n".join(f"[{n['agent']}] {n['note']}" for n in notes)

_lock = threading.Lock()

def episodic_store(goal,outcome,summary):
    with _lock:
        if not MEMORY_FILE.exists():
            loaded = []
        else:
            loaded = json.loads(MEMORY_FILE.read_text(encoding="utf-8")) 
        loaded.append({"ts":time.time(), "goal":goal,"outcome":outcome,"summary":summary})
        loaded = loaded[-100:]
        with open(MEMORY_FILE,"w", encoding = "utf-8") as f:
                f.write(json.dumps(loaded,indent=2))
def episodic_recall(limit=5):
    if not MEMORY_FILE.exists():
        return []
    loaded = json.loads(MEMORY_FILE.read_text(encoding="utf-8"))
    return loaded[-limit:]