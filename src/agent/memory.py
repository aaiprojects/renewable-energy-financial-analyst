import json, os, datetime
from typing import Any, Dict, List
MEM_PATH = "mem/learnings.jsonl"
class Memory:
    def update_from_run(self, ctx: Dict[str, Any]):
        os.makedirs("mem", exist_ok=True)
        note = {
            "ts": datetime.datetime.utcnow().isoformat(),
            "ticker": ctx.get("ticker"),
            "score": ctx.get("score"),
            "critique": ctx.get("critique"),
        }
        with open(MEM_PATH, "a") as f:
            f.write(json.dumps(note) + "\n")
    def fetch_notes(self, ticker: str) -> List[Dict]:
        if not os.path.exists(MEM_PATH): return []
        return [json.loads(l) for l in open(MEM_PATH) if f'"ticker": "{ticker}"' in l]
