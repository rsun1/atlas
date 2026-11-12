import re 
import asyncio
import tempfile
import os
from pathlib import Path
from atlas.app.config import CODE_TIMEOUT_SECONDS

_DENY_RE = re.compile(r"os\.system|subprocess|rm\s+-rf|__import__|eval\(|exec\(")


async def run_python(code):
    if _DENY_RE.search(code):
        return {"ok": False, "stdout":"", "stderr":"Blocked: code matched denylist pattern"}
    else:
        with tempfile.TemporaryDirectory() as tmp_dir:
            script_path = Path(tmp_dir) / "script.py"
            script_path.write_text(code, encoding="utf-8")
            proc = await asyncio.create_subprocess_exec(
                "python","-I", str(script_path),
                cwd=tmp_dir,
                env={"PATH": os.environ.get("PATH","")},
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            try:
                stdout_bytes, stderr_bytes = await asyncio.wait_for(proc.communicate(),timeout=CODE_TIMEOUT_SECONDS)
            except asyncio.TimeoutError:
                proc.kill()
                return {"ok":False, "stdout":"","stderr":"Execution timed out"}
            ok = proc.returncode == 0
            return {
                    "ok": ok,
                    "stdout": stdout_bytes.decode(errors="replace")[:4000],
                    "stderr": stderr_bytes.decode(errors="replace")[:4000]
            }