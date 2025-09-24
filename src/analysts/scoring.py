def score(valuation: float, momentum: float, news: float, macro: float) -> tuple[str, float]:
    total = 0.25*valuation + 0.35*momentum + 0.25*news + 0.15*macro
    if total >= 0.7: return "BUY", total
    if total >= 0.5: return "WATCH", total
    return "AVOID", total
