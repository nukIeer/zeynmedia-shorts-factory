"""Appends one run's history entry (written by produce.py) to the history file; no-op if already there.

Used by the workflow after re-syncing with origin, so concurrent runs never conflict on history.json.
Usage: python v2/factory/append_history.py output/history-entry.json data/history.json
"""
import json
import sys
from pathlib import Path

entry = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
path = Path(sys.argv[2])
history = json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
if not any(h.get("date") == entry["date"] and h.get("topic") == entry["topic"] for h in history):
    history.append(entry)
    path.write_text(json.dumps(history, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
