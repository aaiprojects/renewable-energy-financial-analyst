import json, glob

files = sorted(glob.glob("executive_summary_*.json"))
if not files:
    print("No JSON files found.")
    exit()

print(f"Found {len(files)} summary files:\n")
for fp in files:
    with open(fp) as f:
        data = json.load(f)
    ticker = fp.split("_")[2].split(".")[0]
    conf = data.get("confidence", {}).get("overall", 0)
    outlook = data.get("market_outlook", "N/A")
    print(f"{ticker:<6}  confidence={conf:.2f}  outlook={outlook}")

