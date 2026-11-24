import hashlib, json, os
from datetime import datetime, timezone
from pathlib import Path

def log_event(action, file_path=None, rows=None, status="success", log_path="reports/privacy_audit.jsonl"):
    p = Path(file_path) if file_path else None
    event = {"timestamp_utc": datetime.now(timezone.utc).isoformat(), "run_id": os.getenv("PREFECT_FLOW_RUN_ID", "local"),
        "actor": os.getenv("USER", os.getenv("USERNAME", "unknown")), "action": action,
        "file": p.name if p else None, "sha256": hashlib.sha256(p.read_bytes()).hexdigest() if p and p.exists() else None,
        "row_count": rows, "status": status}
    target = Path(log_path); target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8") as f: f.write(json.dumps(event) + "\n")
