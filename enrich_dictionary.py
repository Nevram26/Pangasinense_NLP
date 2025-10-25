import json
import re

# ---------- Load Lexicon ----------
with open("sorted_dictionary.json", "r", encoding="utf-8") as f:
    lexicon = json.load(f)

# ---------- POS Tagging Function ----------
def guess_pos(meaning: str) -> str:
    """
    Guess Part of Speech from English meaning (heuristics).
    """
    meaning = meaning.lower()

    # Verb detection
    if meaning.startswith("to "):
        return "VERB"
    if any(x in meaning for x in ["(man-", "(maN-", "(on-", "(-en)", "(-an)"]):
        return "VERB"

    # Noun detection
    if any(x in meaning for x in ["thing", "place", "person", "animal", "jar", "tree", "food"]):
        return "NOUN"

    # Adjective detection
    if any(x in meaning for x in ["ugly", "red", "white", "blue", "tired", "big", "small"]):
        return "ADJECTIVE"

    # Adverb detection
    if any(x in meaning for x in ["already", "together", "again", "while", "during"]):
        return "ADVERB"

    # Default
    return "UNKNOWN"

# ---------- Morphology Detection ----------
def detect_morphology(word: str, meaning: str) -> dict | None:
    """
    Detect common Pangasinan affixes in dictionary entries.
    """
    morph = {}

    # Verb affixes
    if "(maN-)" in meaning or "maN-" in meaning:
        morph["affix"] = "maN-"
        morph["category"] = "verb"
    if "(man-)" in meaning or "man-" in meaning:
        morph["affix"] = "man-"
        morph["category"] = "verb"
    if "(on-)" in meaning or "on-" in meaning:
        morph["affix"] = "on-"
        morph["category"] = "verb"
    if "(-en)" in meaning:
        morph["suffix"] = "-en"
        morph["category"] = "verb"
    if "(-an)" in meaning:
        morph["suffix"] = "-an"
        morph["category"] = "verb"

    return morph if morph else None

# ---------- Enrichment ----------
for entry in lexicon:
    entry["POS"] = guess_pos(entry["meaning"])
    entry["morphology"] = detect_morphology(entry["word"], entry["meaning"])

# ---------- Save Enriched Lexicon ----------
with open("pangasinan_enriched.json", "w", encoding="utf-8") as f:
    json.dump(lexicon, f, ensure_ascii=False, indent=2)

print("✅ Enriched lexicon saved to pangasinan_enriched.json")
