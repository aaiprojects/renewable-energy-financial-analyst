from src.dashboard.generate_dashboard import load_current_and_previous_runs, compute_confidence_deltas

current, previous, prev_dir = load_current_and_previous_runs()
print(f"✅ current tickers: {list(current.keys())}")
print(f"✅ previous dir: {prev_dir}")
print(f"✅ previous tickers: {list(previous.keys())}")

deltas = compute_confidence_deltas(current, previous)
print("\n📊 Confidence Deltas:")
for t, info in deltas.items():
    print(f"{t}: {info['previous']} → {info['current']} ({info['delta']} {info['direction']})")

