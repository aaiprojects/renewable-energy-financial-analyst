from typing import Tuple
class Evaluator:
    def score(self, report: dict) -> Tuple[float, str]:
        score = 0.6
        critique = "Add citations, expand evidence coverage, and quantify confidence."
        return score, critique
