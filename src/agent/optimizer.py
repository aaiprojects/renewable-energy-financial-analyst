class Optimizer:
    def refine(self, report: dict, critique: str) -> dict:
        report["summary"] = (report.get("summary","") + f"\n\nRefined per critique: {critique}").strip()
        report["confidence"] = min(0.85, (report.get("confidence") or 0.5) + 0.15)
        return report
