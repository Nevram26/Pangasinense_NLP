import json
import re

# ---------- Load Lexicon ----------
input_file = "midterms/midterm_dictionary.json"
output_file = "midterms/midterm_dictionary_enriched.json"

print(f"📖 Loading dictionary from {input_file}...")
with open(input_file, "r", encoding="utf-8") as f:
    lexicon = json.load(f)
print(f"✓ Loaded {len(lexicon)} entries")

# ---------- POS Tagging Function ----------
def guess_pos(meaning: str, word: str) -> str:
    """
    Guess Part of Speech from English meaning and word structure (heuristics).
    """
    meaning = meaning.lower()
    word = word.lower()

    # Verb detection
    if meaning.startswith("to "):
        return "VERB"
    if any(x in meaning for x in ["(man-", "(maN-", "(on-", "(-en)", "(-an)", "(i-)", "(pa-)", "(-in)"]):
        return "VERB"
    if any(verb in meaning for verb in [
        "do ", "make ", "go ", "come ", "eat ", "drink ", "say ", "tell ", 
        "give ", "take ", "see ", "know ", "think ", "put ", "become ",
        "find ", "use ", "work ", "call ", "try ", "ask ", "need ", "feel ",
        "leave ", "move ", "live ", "believe ", "bring ", "happen ", "write ",
        "sit ", "stand ", "lose ", "pay ", "meet ", "run ", "sell ", "begin ",
        "grow ", "open ", "walk ", "win ", "talk ", "turn ", "start ", "show"
    ]):
        return "VERB"

    # Pronoun detection
    if word in ["siak", "sika", "sikato", "sikami", "sikatayo", "sikayo", "sikara", 
                "ak", "ka", "to", "mi", "tayo", "yo", "da", "ko", "mo"]:
        return "PRONOUN"

    # Particle detection  
    if word in ["ed", "na", "so", "ray", "et", "ya", "ta", "no", "diad", "para", "ni"]:
        return "PARTICLE"

    # Demonstrative
    if word in ["itan", "iyan", "yaran", "yan", "tan"]:
        return "DEMONSTRATIVE"

    # Noun detection
    if any(x in meaning for x in [
        "thing", "place", "person", "animal", "jar", "tree", "food", "house", "home",
        "water", "fire", "land", "way", "time", "year", "day", "work", "child",
        "life", "hand", "part", "city", "room", "fact", "word", "family", "head",
        "mother", "father", "body", "name", "school", "town", "table", "book"
    ]):
        return "NOUN"

    # Adjective detection
    if any(x in meaning for x in [
        "ugly", "red", "white", "blue", "tired", "big", "small", "good", "new",
        "old", "great", "high", "different", "young", "important", "few", "public",
        "bad", "same", "able", "beautiful", "hot", "cold", "happy", "sad", "sick"
    ]):
        return "ADJECTIVE"

    # Adverb detection
    if any(x in meaning for x in [
        "already", "together", "again", "while", "during", "very", "well", "just",
        "also", "still", "even", "only", "never", "really", "most", "often",
        "always", "however", "almost", "perhaps", "quite", "rather", "too"
    ]):
        return "ADVERB"

    # Number detection
    if any(num in word for num in ["usa", "dua", "talo", "apat", "lima", "anem", "pito", "walo", "siam", "sakey"]):
        return "NUMBER"

    # Default
    return "NOUN"  # Default to NOUN rather than UNKNOWN

# ---------- Morphology Detection ----------
def detect_morphology(word: str, meaning: str, entry: dict) -> dict | None:
    """
    Detect common Pangasinan affixes in dictionary entries.
    """
    morph = {
        "root": entry.get("root", word),
        "processes": []
    }

    # Verb affixes from meaning
    if "(maN-)" in meaning or "maN-" in meaning:
        morph["processes"].append({"type": "prefix", "affix": "maN-", "meaning": "actor focus"})
    if "(man-)" in meaning or "man-" in meaning:
        morph["processes"].append({"type": "prefix", "affix": "man-", "meaning": "actor focus (non-completed)"})
    if "(on-)" in meaning or "on-" in meaning:
        morph["processes"].append({"type": "prefix", "affix": "on-", "meaning": "object focus"})
    if "(-en)" in meaning:
        morph["processes"].append({"type": "suffix", "affix": "-en", "meaning": "patient focus"})
    if "(-an)" in meaning:
        morph["processes"].append({"type": "suffix", "affix": "-an", "meaning": "locative focus"})
    if "(i-)" in meaning:
        morph["processes"].append({"type": "prefix", "affix": "i-", "meaning": "benefactive focus"})
    if "(pa-)" in meaning or "pa-" in meaning:
        morph["processes"].append({"type": "prefix", "affix": "pa-", "meaning": "causative"})
    if "(-in)" in meaning or "(in-)" in meaning:
        morph["processes"].append({"type": "infix", "affix": "-in-", "meaning": "completed aspect"})

    # Enclitic detection from process_meaning field
    process_meaning = entry.get("process meaning", "").lower()
    if "enclitic" in process_meaning:
        if "1sg" in process_meaning or "my" in meaning.lower():
            morph["processes"].append({"type": "enclitic", "affix": "-ko", "meaning": "1sg genitive (my)"})
        elif "2sg" in process_meaning or "your" in meaning.lower():
            morph["processes"].append({"type": "enclitic", "affix": "-mo", "meaning": "2sg genitive (your)"})
        elif "3sg" in process_meaning:
            morph["processes"].append({"type": "enclitic", "affix": "-to", "meaning": "3sg genitive (his/her)"})

    return morph if morph["processes"] else None

# ---------- Enrichment ----------
print("\n🔧 Enriching entries with POS tags and morphology...")
pos_counts = {}

for i, entry in enumerate(lexicon):
    if i % 500 == 0:
        print(f"  Processing entry {i+1}/{len(lexicon)}...")
    
    # Add POS tag
    pos = guess_pos(entry.get("meaning", ""), entry.get("word", ""))
    entry["POS"] = pos
    pos_counts[pos] = pos_counts.get(pos, 0) + 1
    
    # Add morphology
    morph = detect_morphology(
        entry.get("word", ""), 
        entry.get("meaning", ""),
        entry
    )
    if morph:
        entry["morphology"] = morph

print("\n📊 POS Tag Distribution:")
for pos, count in sorted(pos_counts.items(), key=lambda x: x[1], reverse=True):
    print(f"  {pos}: {count}")

# ---------- Save Enriched Lexicon ----------
print(f"\n💾 Saving enriched dictionary to {output_file}...")
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(lexicon, f, ensure_ascii=False, indent=2)

print(f"✅ Enriched lexicon saved to {output_file}")
print(f"✅ Total entries: {len(lexicon)}")
print(f"✅ Entries with morphology: {sum(1 for e in lexicon if e.get('morphology'))}")
