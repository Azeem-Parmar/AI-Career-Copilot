import json
from pathlib import Path

DATA_DIR = Path("career_copilot_data")
HISTORY_FILE = DATA_DIR / "history.json"
COMPARISONS_FILE = DATA_DIR / "comparisons.json"

DATA_DIR.mkdir(exist_ok=True)

def load_history():
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    return []

def save_to_history(analysis_data):
    history = load_history()
    history.append(analysis_data)

    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)

def load_comparisons():
    if COMPARISONS_FILE.exists():
        with open(COMPARISONS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_comparison(comparison_name, comparison_data):
    comparisons = load_comparisons()
    comparisons[comparison_name] = comparison_data

    with open(COMPARISONS_FILE, 'w') as f:
        json.dump(comparisons, f, indent=2)

def clear_all_data():
    if HISTORY_FILE.exists():
        HISTORY_FILE.unlink()

    if COMPARISONS_FILE.exists():
        COMPARISONS_FILE.unlink()