import json
import os
import glob
import unicodedata
import re

def normalize_for_sorting(word):
    """Fix word for sorting (handles accents, numbers, special chars)."""
    word = word.lower()
    
    # Put numbered entries (1a, 2a) first
    if re.match(r'^[0-9][a-záéíóúñ]', word):
        number = word[0]
        letter = word[1:]
        return f"000{number}{letter}"
    
    # Put dashed entries (-n) first
    if word.startswith('-'):
        return f"000-{word[1:]}"
    
    # Remove accents (á becomes a, é becomes e)
    normalized = unicodedata.normalize('NFD', word)
    without_accents = ''.join(char for char in normalized if unicodedata.category(char) != 'Mn')
    
    return without_accents

def load_all_dictionaries(json_dir):
    """Load all JSON files from directory."""
    print(f"📂 Looking for JSON files in '{json_dir}' directory...")
    
    json_files = glob.glob(os.path.join(json_dir, "*.json"))
    json_files.sort()
    
    if not json_files:
        print(f"ERROR: No JSON files found in '{json_dir}' directory")
        return []
    
    print(f"Found {len(json_files)} dictionary files:")
    
    all_entries = []
    
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                entries = json.load(f)
            
            filename = os.path.basename(json_file)
            print(f"  - {filename}: {len(entries)} entries")
            
            # Add source info
            for entry in entries:
                entry['source'] = filename.replace('.json', '').replace('_', ' ').title()
            
            all_entries.extend(entries)
            
        except Exception as e:
            print(f"  ERROR: Error loading {json_file}: {e}")
    
    return all_entries

def remove_duplicates(entries):
    """Remove duplicate words, keep first one."""
    print("Removing duplicates...")
    
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
    
    print(f"  Removed {len(entries) - len(unique_entries)} duplicates")
    return unique_entries

def sort_and_combine_dictionaries(json_dir="json_files", output_file="pangasinan_dictionary_combined_sorted.json"):
    """Load, combine, and sort all dictionary files."""
    print("📖 Pangasinan Dictionary Combiner and Sorter")
    print("=" * 50)
    
    # Load files
    all_entries = load_all_dictionaries(json_dir)
    
    if not all_entries:
        return
    
    print(f"\n📊 Total entries loaded: {len(all_entries)}")
    
    # Remove duplicates
    unique_entries = remove_duplicates(all_entries)
    
    # Sort alphabetically
    print("🔤 Sorting entries alphabetically...")
    sorted_entries = sorted(unique_entries, key=lambda entry: normalize_for_sorting(entry['word']))
    
    # Save file
    print(f"Saving combined dictionary to '{output_file}'...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(sorted_entries, f, ensure_ascii=False, indent=2)
    
    print(f"SUCCESS: Combined dictionary created with {len(sorted_entries)} entries!")
    
    # Show stats
    print(f"\nDictionary Statistics:")
    print(f"  - Total entries: {len(sorted_entries)}")
    print(f"  - Original entries before deduplication: {len(all_entries)}")
    print(f"  - Duplicates removed: {len(all_entries) - len(sorted_entries)}")
    
    # Show sample of sorted entries
    print(f"\nFirst 15 entries in alphabetical order:")
    for i, entry in enumerate(sorted_entries[:15]):
        source_info = f" [{entry.get('source', 'Unknown')}]" if 'source' in entry else ""
        print(f"{i+1:2d}. {entry['word']} → {entry['meaning'][:50]}{'...' if len(entry['meaning']) > 50 else ''}{source_info}")
    
    # Show entries from different starting letters
    print(f"\nSample entries from different letters:")
    current_first_letter = ''
    sample_count = 0
    
    for entry in sorted_entries:
        normalized = normalize_for_sorting(entry['word'])
        if normalized and normalized[0] != current_first_letter:
            current_first_letter = normalized[0]
            source_info = f" [{entry.get('source', 'Unknown')}]" if 'source' in entry else ""
            print(f"  {entry['word']} → {entry['meaning'][:40]}{'...' if len(entry['meaning']) > 40 else ''}{source_info}")
            sample_count += 1
            if sample_count >= 10:  # Show first 10 different starting letters
                break

def create_individual_sorted_files(json_dir="json_files"):
    """Create sorted versions of individual dictionary files."""
    print("\nCreating sorted versions of individual dictionary files...")
    
    json_files = glob.glob(os.path.join(json_dir, "*.json"))
    
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                entries = json.load(f)
            
            # Sort entries
            sorted_entries = sorted(entries, key=lambda entry: normalize_for_sorting(entry['word']))
            
            # Create sorted filename
            base_name = os.path.basename(json_file).replace('.json', '')
            sorted_filename = f"{base_name}_sorted.json"
            sorted_filepath = os.path.join(json_dir, sorted_filename)
            
            # Save sorted version
            with open(sorted_filepath, 'w', encoding='utf-8') as f:
                json.dump(sorted_entries, f, ensure_ascii=False, indent=2)
            
            print(f"  SUCCESS: {sorted_filename}: {len(sorted_entries)} entries")
            
        except Exception as e:
            print(f"  ERROR: Error processing {json_file}: {e}")

def main():
    """Run dictionary sorting and combining."""
    json_directory = "json_files"
    combined_output = "pangasinan_dictionary_combined_sorted.json"
    
    try:
        # Check if json_files directory exists
        if not os.path.exists(json_directory):
            print(f"ERROR: Directory '{json_directory}' not found!")
            print("Please run the dictionary scraper first to create individual JSON files.")
            return
        
        # Combine and sort all dictionaries
        sort_and_combine_dictionaries(json_directory, combined_output)
        
        # Create sorted versions of individual files
        create_individual_sorted_files(json_directory)
        
        print(f"\nAll tasks completed!")
        print(f"Files created:")
        print(f"  - {combined_output} (combined and sorted)")
        print(f"  - Individual sorted files in '{json_directory}/' directory")
        
    except Exception as e:
        print(f"ERROR: An error occurred: {e}")

if __name__ == "__main__":
    main()
