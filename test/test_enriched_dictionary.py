import json
import os
from collections import Counter

# -------- LOAD ENRICHED DATA --------
with open("../pangasinan_with_morphology.json", "r", encoding="utf-8") as f:
    enriched = json.load(f)

# -------- CREATE OUTPUTS DIR --------
os.makedirs("outputs", exist_ok=True)


# -------- COVERAGE --------
def coverage_stats(enriched):
    n = len(enriched)

    pos_filled = sum(1 for e in enriched if e.get("POS") and e["POS"] != "UNKNOWN")
    morph_filled = sum(1 for e in enriched if e.get("morphology"))
    root_filled = sum(1 for e in enriched if e.get("morphology", {}).get("root"))

    return {
        "total_entries": n,
        "pos_known_%": pos_filled / n * 100,
        "morphology_present_%": morph_filled / n * 100,
        "root_present_%": root_filled / n * 100,
    }


# -------- INTERNAL CONSISTENCY --------
def consistency_checks(enriched):
    issues = {
        "unknown_with_morphology": 0,
        "empty_process_lists": 0,
    }

    for e in enriched:
        pos = e.get("POS")
        morph = e.get("morphology", {})
        processes = morph.get("processes", [])

        # Case 1: POS unknown but morphology exists
        if pos == "UNKNOWN" and morph:
            issues["unknown_with_morphology"] += 1

        # Case 2: morphology exists but processes are empty
        if morph and isinstance(processes, list) and len(processes) == 0:
            issues["empty_process_lists"] += 1

    return issues


# -------- ROOT STATS --------
def root_analysis(enriched):
    roots = [e.get("morphology", {}).get("root") for e in enriched if e.get("morphology", {}).get("root")]
    root_counter = Counter(roots)

    return {
        "unique_roots": len(root_counter),
        "avg_words_per_root": sum(root_counter.values()) / len(root_counter) if root_counter else 0,
        "top_roots": root_counter.most_common(10),
    }


# -------- COLLECT ALL METRICS --------
metrics = {
    "coverage": coverage_stats(enriched),
    "consistency_checks": consistency_checks(enriched),
    "root_analysis": root_analysis(enriched),
}

# -------- SAVE METRICS --------
metrics_path = os.path.join("outputs", "metrics.json")
with open(metrics_path, "w", encoding="utf-8") as f:
    json.dump(metrics, f, ensure_ascii=False, indent=2)

print(f"Saved metrics to {metrics_path}")