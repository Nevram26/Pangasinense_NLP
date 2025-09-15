import json
import os
import glob

def load_all_dictionaries(json_dir):
    """Load all JSON files from directory without sorting."""
    json_files = glob.glob(os.path.join(json_dir, "*.json"))
    json_files.sort()  # Sort file names for consistent order
    
    all_entries = []
    
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                entries = json.load(f)
            
            filename = os.path.basename(json_file)
            
            # Add source info to each entry
            for entry in entries:
                entry['source'] = filename.replace('.json', '').replace('_', ' ').title()
            
            all_entries.extend(entries)
            
        except Exception as e:
            continue
    
    return all_entries

def remove_duplicates(entries):
    """Remove duplicate words, keep first occurrence."""
    seen = {}
    unique_entries = []
    
    for entry in entries:
        word_key = entry["word"].lower()
        
        if word_key not in seen:
            seen[word_key] = entry
            unique_entries.append(entry)
        else:
            # Combine sources if duplicate found
            existing_entry = seen[word_key]
            if 'source' in entry and 'source' in existing_entry:
                sources = set()
                if ',' in existing_entry['source']:
                    sources.update(s.strip() for s in existing_entry['source'].split(','))
                else:
                    sources.add(existing_entry['source'])
                
                sources.add(entry['source'])
                existing_entry['source'] = ', '.join(sorted(sources))
    
    return unique_entries

def combine_dictionaries(json_dir="json_files", output_file="pangasinan_dictionary_combined.json"):
    """Load and combine all dictionary files without sorting."""
    # Load files
    all_entries = load_all_dictionaries(json_dir)
    
    if not all_entries:
        return
    
    # Remove duplicates (but keep original order)
    unique_entries = remove_duplicates(all_entries)
    
    # Save combined file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(unique_entries, f, ensure_ascii=False, indent=2)

def main():
    """Combine dictionary files without sorting."""
    json_directory = "json_files"
    combined_output = "pangasinan_dictionary_combined.json"
    
    if not os.path.exists(json_directory):
        return
    
    combine_dictionaries(json_directory, combined_output)

if __name__ == "__main__":
    main()