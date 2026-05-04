import json
from datetime import datetime, timezone
from pathlib import Path


def run_session(paper_dir: Path, user_answer: str) -> Path:
    sessions_dir = paper_dir / "sessions"
    sessions_dir.mkdir(exist_ok=True)
    out = sessions_dir / f"session_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}.json"
    out.write_text(json.dumps({"answer": user_answer, "timestamp": datetime.now(timezone.utc).isoformat()}, ensure_ascii=False, indent=2), encoding="utf-8")
    return out
