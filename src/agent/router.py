from typing import List, Dict
class Router:
    def route(self, news_items: List[Dict]) -> List[Dict]:
        routed = []
        for item in news_items or []:
            lower = (item.get("title","") + " " + item.get("description","")).lower()
            if any(k in lower for k in ["earnings", "guidance", "q1", "q2", "q3", "q4"]):
                routed.append({"type": "earnings", "item": item})
            elif any(k in lower for k in ["policy", "tariff", "subsid", "ira", "regulat"]):
                routed.append({"type": "news", "item": item})
            else:
                routed.append({"type": "market", "item": item})
        return routed
