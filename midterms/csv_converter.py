import json
import csv
import unicodedata
import sys

INPUT_JSON = "pangasinan_with_morphology.json"
OUTPUT_CSV = "pangasinan.csv"

# Desired CSV columns (change 'meaning2' name if you want something else)
COLUMNS = ["word","meaning","source","morphology","root","processes","type","meaning2","form","normalized_form"]

def normalize_text(s):
    if s is None:
        return ""
    s = str(s).strip().lower()
    # remove diacritics
    s = unicodedata.normalize("NFD", s)
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn")
    s = unicodedata.normalize("NFC", s)
    return s

def serialize_value(v):
    # Join lists with semicolon, objects as compact json, else string
    if v is None:
        return ""
    if isinstance(v, list):
        return ";".join(str(x) for x in v)
    if isinstance(v, dict):
        return json.dumps(v, ensure_ascii=False, separators=(",",":"))
    return str(v)

def main():
    with open(INPUT_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Expect data to be a list of entries. If it's an object with a key, adjust as needed.
    if isinstance(data, dict):
        # try common keys
        if "entries" in data:
            data = data["entries"]
        else:
            # if single object, make it a list
            data = [data]

    rows = []
    for entry in data:
        # Fetch fields, using defaults if not present
        word = serialize_value(entry.get("word") or entry.get("orthography") or entry.get("form"))
        meaning = serialize_value(entry.get("meaning") or entry.get("gloss"))
        source = serialize_value(entry.get("source"))
        morphology = None
        # If morphology present as object or list, convert appropriately
        if "morphology" in entry:
            morphology = entry["morphology"]
        elif "morph" in entry:
            morphology = entry["morph"]
        morphology = serialize_value(morphology)

        root = serialize_value(entry.get("root"))
        processes = serialize_value(entry.get("processes") or entry.get("morph_processes") or entry.get("derivation"))
        type_ = serialize_value(entry.get("type") or entry.get("pos"))
        meaning2 = serialize_value(entry.get("meaning2") or entry.get("alt_meaning") or entry.get("gloss2"))

        form = serialize_value(entry.get("form") or entry.get("orthography") or entry.get("word"))
        normalized_form = normalize_text(form)

        row = {
            "word": word,
            "meaning": meaning,
            "source": source,
            "morphology": morphology,
            "root": root,
            "processes": processes,
            "type": type_,
            "meaning2": meaning2,
            "form": form,
            "normalized_form": normalized_form
        }
        rows.append(row)

    # Write CSV
    with open(OUTPUT_CSV, "w", encoding="utf-8", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=COLUMNS)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    print(f"Wrote {len(rows)} rows to {OUTPUT_CSV}")

if __name__ == "__main__":
    main()