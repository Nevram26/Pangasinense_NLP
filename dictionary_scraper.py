import re
import json
import os
import glob
from PyPDF2 import PdfReader

def extract_entries_from_pdf(pdf_file):
    """Extract word-meaning pairs from one PDF file with complete multi-line handling."""
    reader = PdfReader(pdf_file)
    full_text = ""
    
    # Extract all text
    for page in reader.pages:
        full_text += page.extract_text() + "\n"
    
    # Remove metadata sections
    text = full_text
    metadata_patterns = [
        r'Chapter Title:.*?(?=\n[a-záéíóúñ])',
        r'Book Title:.*?(?=\n[a-záéíóúñ])',
        r'Book Author\(s\):.*?(?=\n[a-záéíóúñ])',
        r'Published by:.*?(?=\n[a-záéíóúñ])',
        r'Stable URL:.*?(?=\n[a-záéíóúñ])',
        r'JSTOR is a not-for-profit.*?(?=\n[a-záéíóúñ])',
        r'Your use of the JSTOR.*?(?=\n[a-záéíóúñ])',
        r'This content is licensed.*?(?=\n[a-záéíóúñ])',
        r'University of Hawai\'i Press.*?(?=\n[a-záéíóúñ])',
        r'This content downloaded.*?(?=\n[a-záéíóúñ])',
        r'All use subject to.*?(?=\n[a-záéíóúñ])',
        r'PANGASINAN–ENGLISH\s*DICTIONARY.*?(?=\n[a-záéíóúñ])',
    ]
    
    for pattern in metadata_patterns:
        text = re.sub(pattern, '', text, flags=re.DOTALL | re.IGNORECASE)
    
    # Split into lines and process
    lines = text.split('\n')
    entries = []
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip empty lines and obvious non-entries
        if (not line or line.isdigit() or 
            'jstor' in line.lower() or 'http' in line.lower() or
            'utc' in line.lower() or 'content downloaded' in line.lower() or
            'license' in line.lower() or 'university' in line.lower() or
            line in ['B', 'C', 'D', 'E', 'I', 'K', 'L', 'M', 'P'] or  # Allow 'A' but skip other section headers
            line.lower().startswith(('range of', 'facilitate', 'digital archive'))):
            i += 1
            continue
        
        # Look for dictionary entry patterns
        entry_match = None
        word = None
        definition = None
        
        # Special handling for numbered entries like "1ainterjection", "2alinking"
        special_match = re.match(r'^([0-9][a-záéíóúñ])([a-záéíóúñ]+)\s+(.+)', line, re.IGNORECASE)
        if special_match:
            word = special_match.group(1)  # "1a", "2a"
            type_word = special_match.group(2)  # "interjection", "linking"
            rest = special_match.group(3)  # "marking hesitation,..."
            definition = type_word + " " + rest  # "interjection marking hesitation,..."
            entry_match = True
        else:
            # Regular pattern for other entries including single letters and -n
            regular_match = re.match(r'^([a-záéíóúñ](?:[a-záéíóúñ\-]*[a-záéíóúñ])?|\-[a-záéíóúñ]+|[a-záéíóúñ])\s+(.+)', line, re.IGNORECASE)
            if regular_match:
                word = regular_match.group(1).strip()
                definition = regular_match.group(2).strip()
                entry_match = True
        
        if entry_match:
            # Skip common English words that are likely definition fragments
            english_fragments = [
                'holding', 'between', 'applied', 'plants', 'animals', 'material', 'them', 'noise',
                'word', 'following', 'not', 'when', 'used', 'meaning', 'particle', 'pronoun',
                'where', 'have', 'addressing', 'respectively', 'couple', 'specific', 'purpose',
                'generation', 'sufficient', 'mature', 'containing', 'scissors', 'tube', 'rise',
                'stored', 'equivalent', 'storing', 'maturing', 'harvestable', 'centavo',
                'cooked', 'mainly', 'putting', 'dry', 'flesh', 'range', 'international', 
                'descriptive', 'relative', 'finalizing', 'groom', 'collectively',
                'person', 'object', 'neighbor', 'close', 'cloth', 'supplies'
            ]
            
            if word.lower() in english_fragments:
                i += 1
                continue
            
            # Collect ALL continuation lines until we find the next real entry
            j = i + 1
            while j < len(lines):
                next_line = lines[j].strip()
                
                # Skip empty lines
                if not next_line:
                    j += 1
                    continue
                
                # Check if this line starts a new dictionary entry
                # Test both special numbered pattern and regular pattern
                is_new_entry = False
                
                # Check for numbered entry
                next_special_match = re.match(r'^([0-9][a-záéíóúñ])([a-záéíóúñ]+)\s+(.+)', next_line, re.IGNORECASE)
                if next_special_match:
                    is_new_entry = True
                else:
                    # Check for regular entry
                    next_regular_match = re.match(r'^([a-záéíóúñ](?:[a-záéíóúñ\-]*[a-záéíóúñ])?|\-[a-záéíóúñ]+|[a-záéíóúñ])\s+(.+)', next_line, re.IGNORECASE)
                    if next_regular_match:
                        potential_word = next_regular_match.group(1).strip().lower()
                        potential_def = next_regular_match.group(2).strip().lower()
                        
                        # Check if this looks like a genuine dictionary entry
                        is_new_entry = (
                            potential_word not in english_fragments and 
                            len(potential_def) > 2 and
                            not potential_def.startswith(('or object', 'close by', 'and those', 'between the', 'holding between'))
                        )
                
                if is_new_entry:
                    break
                
                # Otherwise, add this line to the current definition
                if next_line and len(next_line) > 0:
                    definition += " " + next_line
                
                j += 1
            
            # Clean up definition
            definition = re.sub(r'\s+', ' ', definition)  # Normalize spaces
            definition = re.sub(r'[\x00-\x1f]', '', definition)  # Remove control chars
            definition = definition.strip()
            
            # Validate entry
            is_valid_entry = (
                len(word) >= 1 and len(definition) >= 3 and
                not word.lower() in ['to', 'the', 'and', 'or', 'in', 'on', 'at', 'by', 'for', 'with', 'from', 'of'] and
                not word.isdigit() and
                not definition.lower().startswith(('http', 'www', 'license', 'university')) and
                not word.lower() in english_fragments
            )
            
            if is_valid_entry:
                entries.append({
                    "word": word,
                    "meaning": definition
                })
            
            i = j  # Skip to next unprocessed line
        else:
            i += 1
    
    return entries


# 🔹 Create output directory for JSON files
output_dir = "json_files"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    print(f"📁 Created directory: {output_dir}")

# 🔹 Automatically find all PDF files in the Dictionary directory
pdf_files = glob.glob("Dictionary/*.pdf")
pdf_files.sort()  # Sort them alphabetically

print(f"📂 Found {len(pdf_files)} PDF files:")
for pdf in pdf_files:
    print(f"  - {pdf}")
print()

all_entries = []
individual_files = []

for pdf in pdf_files:
    print(f"📖 Extracting from {pdf}...")
    entries = extract_entries_from_pdf(pdf)
    print(f"   Found {len(entries)} entries")
    
    # Create individual JSON file for this dictionary
    pdf_name = os.path.basename(pdf).replace('.pdf', '')
    json_filename = f"{pdf_name.lower().replace(' ', '_')}.json"
    json_filepath = os.path.join(output_dir, json_filename)
    
    # Remove duplicates from this individual dictionary
    seen_in_this_dict = set()
    unique_entries_this_dict = []
    for entry in entries:
        word_key = entry["word"].lower()
        if word_key not in seen_in_this_dict:
            seen_in_this_dict.add(word_key)
            unique_entries_this_dict.append(entry)
    
    # Save individual JSON file
    with open(json_filepath, "w", encoding="utf-8") as f:
        json.dump(unique_entries_this_dict, f, ensure_ascii=False, indent=2)
    
    print(f"   Saved {len(unique_entries_this_dict)} entries to {json_filepath}")
    individual_files.append(json_filepath)
    all_entries.extend(unique_entries_this_dict)

print(f"\nIndividual JSON files created: {len(individual_files)}")
for file in individual_files:
    print(f"  - {file}")

print(f"\n� Total entries across all dictionaries: {len(all_entries)}")
print(f"✅ Done! Each dictionary has been saved as a separate JSON file in '{output_dir}/' directory")
print(f"\n💡 Use the 'sort_and_combine.py' script to sort and combine all dictionaries into one file.")
