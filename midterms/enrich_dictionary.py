import json
import re

# ---------- Load Lexicon ----------
with open("midterm_dictionary.json", "r", encoding="utf-8") as f:
    lexicon = json.load(f)

# ---------- POS Tagging Function ----------
def guess_pos(translation: str) -> str:
    """
    Guess Part of Speech (POS) from the English translation field using heuristics.
    """
    if not translation:
        return "UNKNOWN"
    
    translation = translation.lower().strip()

    # Verb detection
    if translation.startswith("to "):
        return "VERB"
    if any(x in translation for x in ["(man-", "(maN-", "(on-", "(-en)", "(-an)"]):
        return "VERB"

    # Noun detection
    if any(x in translation for x in [
        "thing", "place", "person", "animal", "tree", "food", "object", "name", "part"
    ]):
        return "NOUN"

    # Adjective detection
    if any(x in translation for x in [
        "ugly", "red", "white", "blue", "big", "small", "tired", "good", "bad", "beautiful"
    ]):
        return "ADJECTIVE"

    # Adverb detection
    if any(x in translation for x in [
        "already", "together", "again", "while", "during", "now", "later", "soon"
    ]):
        return "ADVERB"

    # Pronoun detection
    if any(x in translation for x in [
        "i", "you", "he", "she", "it", "we", "they", "me", "him", "her", "them"
    ]):
        return "PRONOUN"

    # Preposition detection
    if any(x in translation for x in [
        "in", "on", "at", "with", "by", "from", "to", "for", "of"
    ]):
        return "PREPOSITION"

    # Default
    return "UNKNOWN"
    return morph if morph else None

# ---------- Enrichment ----------
for entry in lexicon:
    translation = entry.get("translation", "")
    entry["POS"] = guess_pos(translation)

# ---------- Save Enriched Lexicon ----------
with open("pangasinan_enriched_midterms.json", "w", encoding="utf-8") as f:
    json.dump(lexicon, f, ensure_ascii=False, indent=2)

print("Enriched lexicon saved to pangasinan_enriched.json (POS based on 'translation')")