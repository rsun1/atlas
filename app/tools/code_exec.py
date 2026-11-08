from atlas.app import config
import re 

_DENY_RE = re.compile(r"os\.system|subprocess|rm\s+-rf|__import__|eval\(|exec\(")

#_DENY_RE.search("import os; os.system('rm -rf /')")