import os 
from pathlib import Path 

def _load_env():
    env_path = Path(__file__).parent.parent / ".env"
    if not env_path.exists():
        return 
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(),value.strip())

_load_env()

DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
AUDIT_LOG = DATA_DIR / "audit.jsonl"
MEMORY_FILE = DATA_DIR / "memory.json"

FORCE_DEMO = os.environ.get("FORCE_DEMO","0") == "1"
APPROVAL_THRESHOLD = int(os.environ.get("APPROVAL_THRESHOLD", "80"))
MAX_STEP_RETRIES = int(os.environ.get("MAX_STEP_RETRIES","3"))
CODE_TIMEOUT_SECONDS = int(os.environ.get("CODE_TIMEOUT_SECONDS","10"))

