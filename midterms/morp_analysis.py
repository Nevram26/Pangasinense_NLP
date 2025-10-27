#!/usr/bin/env python3
"""
Morphological analysis script converted from the notebook.
Loads a JSON lexicon, applies rule-based morphological analysis,
and writes an enriched lexicon plus prints simple statistics.

Usage:
  python3 morp_analysis.py --input pangasinan_dictionary_combined.json --output pangasinan_with_morphology.json
"""
import argparse
import json
import os
import sys
from collections import Counter, defaultdict
from copy import deepcopy

# === Rules (kept compact / same as notebook) ===
RULES = [
    {"type": "nasal_prefix", "form": "ma", "label": "maN-", "meaning": "actor focus (nasal-assimilating, non-completed)"},
    {"type": "nasal_prefix", "form": "a", "label": "aN-", "meaning": "actor focus (nasal-assimilating, completed)"},
    {"type": "nasal_prefix", "form": "pa", "label": "paN-", "meaning": "causative/instrumental nasal-assimilating"},
    {"type": "nasal_prefix", "form": "o", "label": "oN-", "meaning": "actor focus (nasal-assimilating variant)"},
    {"type": "prefix", "form": "man", "label": "man-", "meaning": "actor focus (non-completed)"},
    {"type": "prefix", "form": "nan", "label": "nan-", "meaning": "actor focus (completed)"},
    {"type": "prefix", "form": "ma", "label": "ma-", "meaning": "causative / stative"},
    {"type": "prefix", "form": "pa", "label": "pa-", "meaning": "causative/allowative"},
    {"type": "prefix", "form": "paka", "label": "paka-", "meaning": "causative/allowative (intensive)"},
    {"type": "prefix", "form": "maka", "label": "maka-", "meaning": "ability/potential"},
    {"type": "prefix", "form": "mi", "label": "mi-", "meaning": "reciprocal/distributive"},
    {"type": "prefix", "form": "aki", "label": "aki-", "meaning": "reciprocal/distributive"},
    {"type": "prefix", "form": "ipan", "label": "(i)pan-", "meaning": "instrumental focus (non-completed)"},
    {"type": "prefix", "form": "inpan", "label": "inpan-", "meaning": "instrumental focus (completed)"},
    {"type": "prefix", "form": "ipañgi", "label": "(i)pañgi-", "meaning": "instrumental/apparatus focus (non-completed)"},
    {"type": "prefix", "form": "inpañgi", "label": "inpañgi-", "meaning": "instrumental/apparatus focus (completed)"},
    {"type": "prefix", "form": "i", "label": "i-", "meaning": "theme/goal or benefactive focus (non-completed)"},
    {"type": "prefix", "form": "in", "label": "in-", "meaning": "theme/goal or benefactive focus (completed)"},
    {"type": "suffix", "form": "an", "label": "-an", "meaning": "locative/referent focus (non-completed)"},
    {"type": "suffix", "form": "en", "label": "-en", "meaning": "patient focus (non-completed)"},
    {"type": "suffix", "form": "in", "label": "-in", "meaning": "patient/theme focus (completed)"},
    {"type": "suffix", "form": "tayo", "label": "-tayo", "meaning": "1pl inclusive genitive enclitic"},
    {"type": "suffix", "form": "mi", "label": "-mi", "meaning": "1pl exclusive genitive enclitic"},
    {"type": "suffix", "form": "mo", "label": "-mo", "meaning": "2sg genitive enclitic"},
    {"type": "suffix", "form": "yo", "label": "-yo", "meaning": "2pl genitive enclitic"},
    {"type": "suffix", "form": "ko", "label": "-ko", "meaning": "1sg genitive enclitic"},
    {"type": "suffix", "form": "ta", "label": "-ta", "meaning": "1du inclusive genitive enclitic"},
    {"type": "suffix", "form": "to", "label": "-to", "meaning": "3sg genitive enclitic"},
    {"type": "suffix", "form": "da", "label": "-da", "meaning": "3pl genitive enclitic"},
    {"type": "circumfix", "form": {"prefix": "i", "suffix": "an"}, "label": "i-…-an", "meaning": "benefactive focus (non-completed)"},
    {"type": "circumfix", "form": {"prefix": "in", "suffix": "an"}, "label": "in-…-an", "meaning": "benefactive/referent focus (completed)"},
    {"type": "infix", "form": "in", "label": "-in-", "meaning": "completed aspect marker"},
    {"type": "reduplication", "form": "CV", "label": "CV-", "meaning": "partial reduplication (plural nouns)"},
    {"type": "reduplication", "form": "CVC", "label": "CVC-", "meaning": "partial reduplication (plural nouns)"},
    {"type": "reduplication", "form": "C1V", "label": "C1V-", "meaning": "partial reduplication (plural nouns)"},
    {"type": "reduplication", "form": "CVCV", "label": "CVCV-", "meaning": "partial reduplication (plural nouns)"},
    {"type": "reduplication", "form": "full", "label": "full", "meaning": "full reduplication (intensifier/frequentative)"}
]

# === Analyzer constants & helpers ===
NASAL_ALLOMORPHS = ["m", "n", "ng", "ny"]
VOWELS = set("aeiouáéíóúâêîôû")
PARTIAL_REDUPE_LENGTHS = {"CV": 2, "CVC": 3, "C1V": 2, "CVCV": 4}
APPLY_FUNCS = {}  # filled after function definitions
PROCESS_ORDER = ["circumfix", "nasal_prefix", "prefix", "suffix", "infix"]

def _display_form(rule):
    if "label" in rule:
        return rule["label"]
    form = rule["form"]
    if isinstance(form, dict):
        return f"{form.get('prefix','')}…{form.get('suffix','')}"
    return str(form)

def _make_record(rule, extra=None):
    record = {
        "type": rule["type"],
        "meaning": rule.get("meaning", ""),
        "form": _display_form(rule),
        "normalized_form": deepcopy(rule.get("form"))
    }
    if extra:
        record.update(extra)
    return record

def _apply_circumfix(stem, rule):
    form = rule["form"]
    prefix = form.get("prefix", "")
    suffix = form.get("suffix", "")
    lower = stem.lower()
    if lower.startswith(prefix) and (suffix == "" or lower.endswith(suffix)) and len(stem) > len(prefix) + len(suffix):
        if suffix:
            new_stem = stem[len(prefix):-len(suffix)]
        else:
            new_stem = stem[len(prefix):]
        return new_stem, _make_record(rule)
    return stem, None

def _apply_nasal_prefix(stem, rule):
    base = rule["form"]
    lower = stem.lower()
    if not lower.startswith(base):
        return stem, None
    remainder = stem[len(base):]
    if not remainder:
        return stem, None
    rem_lower = remainder.lower()
    for allo in NASAL_ALLOMORPHS:
        if rem_lower.startswith(allo):
            new_stem = remainder[len(allo):]
            return new_stem, _make_record(rule, {"applied_allomorph": allo})
    if rem_lower[0] in VOWELS:
        return remainder, _make_record(rule, {"applied_allomorph": ""})
    return stem, None

def _apply_prefix(stem, rule):
    prefix = rule["form"]
    if stem.lower().startswith(prefix) and len(stem) > len(prefix):
        return stem[len(prefix):], _make_record(rule)
    return stem, None

def _apply_suffix(stem, rule):
    suffix = rule["form"]
    if stem.lower().endswith(suffix) and len(stem) > len(suffix):
        return stem[:-len(suffix)], _make_record(rule)
    return stem, None

def _apply_infix(stem, rule):
    infix = rule["form"]
    lower = stem.lower()
    start = lower.find(infix, 1)  # avoid word-initial match
    if start != -1 and len(stem) > len(infix):
        new_stem = stem[:start] + stem[start + len(infix):]
        return new_stem, _make_record(rule, {"position": start})
    return stem, None

def _apply_reduplication(stem, rule):
    pattern = rule["form"]
    lower = stem.lower()
    if pattern == "full":
        if len(stem) % 2 == 0:
            half = len(stem) // 2
            if lower[:half] == lower[half:]:
                return stem[:half], _make_record(rule)
        return stem, None
    chunk_len = PARTIAL_REDUPE_LENGTHS.get(pattern)
    if not chunk_len or len(stem) < chunk_len * 2:
        return stem, None
    chunk = stem[:chunk_len]
    if lower[:chunk_len] == lower[chunk_len:chunk_len * 2]:
        return stem[chunk_len:], _make_record(rule, {"partial_chunk": chunk})
    return stem, None

# populate APPLY_FUNCS
APPLY_FUNCS.update({
    "circumfix": _apply_circumfix,
    "nasal_prefix": _apply_nasal_prefix,
    "prefix": _apply_prefix,
    "suffix": _apply_suffix,
    "infix": _apply_infix,
    "reduplication": _apply_reduplication,
})

def analyze(word, rules):
    """Return morphology analysis: root and list of processes applied."""
    stem = word
    processes = []
    grouped = defaultdict(list)
    for rule in rules:
        grouped[rule["type"]].append(rule)

    for rule_type in PROCESS_ORDER:
        applied = True
        while applied:
            applied = False
            for rule in grouped.get(rule_type, []):
                new_stem, record = APPLY_FUNCS[rule_type](stem, rule)
                if record is not None:
                    processes.append(record)
                    stem = new_stem
                    applied = True
                    break

    # attempt reduplication once at end
    for rule in grouped.get("reduplication", []):
        new_stem, record = APPLY_FUNCS["reduplication"](stem, rule)
        if record is not None:
            processes.append(record)
            stem = new_stem
            break

    return {"root": stem if stem else word, "processes": processes}

def enrich_lexicon(in_path, out_path, rules):
    if not os.path.exists(in_path):
        print(f"Input file not found: {in_path}", file=sys.stderr)
        sys.exit(2)
    with open(in_path, "r", encoding="utf-8") as f:
        lexicon = json.load(f)
    if not isinstance(lexicon, list):
        print("Expected lexicon to be a list of entries.", file=sys.stderr)
        sys.exit(2)

    for entry in lexicon:
        word = entry.get("word") if isinstance(entry, dict) else None
        if not word or not isinstance(word, str):
            # skip entries without a usable word
            continue
        entry["morphology"] = analyze(word, rules)

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(lexicon, f, ensure_ascii=False, indent=2)

    print(f"Saved enriched lexicon ({len(lexicon)} entries) to {out_path}")
    return out_path

def print_statistics(enriched_path):
    with open(enriched_path, "r", encoding="utf-8") as f:
        enriched = json.load(f)

    AFFIX_TYPES = {"prefix", "suffix", "infix", "nasal_prefix", "circumfix"}
    affix_counter = Counter()
    nasal_allomorph_counter = Counter()
    redup_counter = Counter()
    total = len(enriched)

    for entry in enriched:
        morph = entry.get("morphology", {})
        for proc in morph.get("processes", []):
            ptype = proc.get("type")
            label = proc.get("form")
            if ptype == "reduplication":
                redup_counter[label] += 1
            elif ptype in AFFIX_TYPES:
                affix_counter[label] += 1
                if ptype == "nasal_prefix":
                    nasal_allomorph_counter[(label, proc.get("applied_allomorph", "∅"))] += 1

    print(f"Total entries enriched: {total}\n")
    if affix_counter:
        print("Affix statistics:")
        for affix, count in affix_counter.most_common():
            print(f"  {affix}: {count}")
    if nasal_allomorph_counter:
        print("\nNasal assimilation allomorphs:")
        for (affix, allo), count in nasal_allomorph_counter.most_common():
            print(f"  {affix} +{allo or '∅'}: {count}")
    if redup_counter:
        print("\nReduplication statistics:")
        for form, count in redup_counter.most_common():
            print(f"  {form}: {count}")

def main():
    p = argparse.ArgumentParser(description="Apply rule-based morphological analysis to Pangasinan lexicon.")
    # default input now points to the combined file; fallback to enriched if combined missing
    p.add_argument("--input", "-i", default="pangasinan_dictionary_combined.json", help="Input JSON lexicon (default: pangasinan_dictionary_combined.json)")
    p.add_argument("--output", "-o", default="pangasinan_with_morphology.json", help="Output enriched JSON file")
    p.add_argument("--stats", action="store_true", help="Print enrichment statistics after processing")
    args = p.parse_args()

    # if default combined file not present, try previous enriched default
    input_path = args.input
    if args.input == "pangasinan_dictionary_combined.json" and not os.path.exists(input_path):
        alt = "pangasinan_with_morphology.json"
        if os.path.exists(alt):
            input_path = alt
            print(f"Note: combined file not found, falling back to {alt}")

    out_path = enrich_lexicon(input_path, args.output, RULES)
    if args.stats:
        print_statistics(out_path)

if __name__ == "__main__":
    main()