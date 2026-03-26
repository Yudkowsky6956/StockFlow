from pathlib import Path

# PATHS
ANALYZE_FOLDER = Path("analytics")
HISTORY_FOLDER = ANALYZE_FOLDER / "history"
OUTPUT_FOLDER = ANALYZE_FOLDER / "output"
OUTPUT_FILE = OUTPUT_FOLDER / "errors_amount.json"
OUTPUT_BY_DAY_FILE = OUTPUT_FOLDER / "errors_by_day.json"