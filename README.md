# Pangasinense Dictionary Scraper

A Python tool for extracting and processing Pangasinan-English dictionary entries from PDF files. This project scrapes dictionary content, cleans it from metadata contamination, and organizes it into structured JSON files with intelligent sorting and deduplication.

## Overview

The Pangasinan Dictionary Scraper processes multiple PDF dictionary files and extracts clean word-meaning pairs while handling complex dictionary formatting challenges like:

- **Multi-line definitions** that span across several lines
- **JSTOR metadata contamination** mixed within dictionary content
- **Special entry types** like numbered entries (1a, 2a) and prefixed entries (-n)
- **Unicode character normalization** for proper alphabetical sorting
- **Duplicate entry management** across multiple dictionary sources

## Features

- **PDF Text Extraction**: Uses PyPDF2 to extract text from multiple dictionary PDF files
- **Intelligent Filtering**: Removes JSTOR metadata, licensing text, and other non-dictionary content
- **Multi-line Definition Handling**: Combines fragmented definitions that span multiple lines
- **Special Entry Support**: Properly handles numbered (1a, 2a) and prefixed (-n) dictionary entries
- **Individual File Creation**: Creates separate JSON files for each dictionary source
- **Smart Sorting**: Alphabetical sorting with proper handling of accented characters (á, é, í, ó, ú, ñ)
- **Deduplication**: Removes duplicate entries while preserving source information
- **Combined Output**: Merges all dictionaries into a single sorted file

## Project Structure

```
Pangasinense_Dictionary_Scraper/
├── Dictionary/                 # Source PDF files
│   ├── Dictionary A.pdf
│   ├── Dictionary B.pdf
│   ├── Dictionary CH.pdf
│   ├── Dictionary D.pdf
│   ├── Dictionary E.pdf
│   ├── Dictionary I.pdf
│   ├── Dictionary K.pdf
│   ├── Dictionary L.pdf
│   ├── Dictionary M.pdf
│   └── Dictionary P.pdf
├── json_files/                 # Generated JSON files
│   ├── dictionary_a.json
│   ├── dictionary_b.json
│   ├── dictionary_ch.json
│   ├── dictionary_d.json
│   ├── dictionary_e.json
│   ├── dictionary_i.json
│   ├── dictionary_k.json
│   ├── dictionary_l.json
│   ├── dictionary_m.json
│   └── dictionary_p.json
├── dictionary_scraper.py       # Main extraction script
├── sort_and_combine.py         # Sorting and combining script
└── README.md
```

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Nevram26/Pangasinense_Dictionary_Scraper.git
   cd Pangasinense_Dictionary_Scraper
   ```

2. **Install required dependencies:**
   ```bash
   pip install PyPDF2
   ```

## Usage

### Step 1: Extract Dictionary Entries

Run the main scraper to extract entries from all PDF files:

```bash
python dictionary_scraper.py
```

This will:
- Process all PDF files in the `Dictionary/` folder
- Extract clean dictionary entries with multi-line definition handling
- Create individual JSON files in the `json_files/` directory
- Show extraction progress and statistics

**Sample Output:**
```
Found 10 PDF files:
  - Dictionary/Dictionary A.pdf
  - Dictionary/Dictionary B.pdf
  ...

Extracting from Dictionary/Dictionary A.pdf...
   Found 285 entries
   Saved 285 entries to json_files/dictionary_a.json

Individual JSON files created: 10
  - json_files/dictionary_a.json
  - json_files/dictionary_b.json
  ...

Total entries across all dictionaries: 2724
SUCCESS: Each dictionary has been saved as a separate JSON file in 'json_files/' directory

TIP: Use the 'sort_and_combine.py' script to sort and combine all dictionaries into one file.
```

### Step 2: Sort and Combine Dictionaries

Run the sorting script to create a combined, alphabetically sorted dictionary:

```bash
python sort_and_combine.py
```

This will:
- Load all individual JSON files
- Remove duplicate entries (keeping source information)
- Sort alphabetically with proper Unicode handling
- Create a combined sorted dictionary file
- Generate sorted versions of individual dictionaries

**Sample Output:**
```
Found 10 dictionary files:
  - json_files/dictionary_a.json (285 entries)
  - json_files/dictionary_b.json (267 entries)
  ...

Removing duplicates...
  Removed 39 duplicates

Saving combined dictionary to 'pangasinan_dictionary_combined_sorted.json'...
SUCCESS: Combined dictionary created with 2685 entries!

Dictionary Statistics:
  - Total entries: 2685
  - Original entries before deduplication: 2724
  - Duplicates removed: 39

First 15 entries in alphabetical order:
 1. -n → (particle suffix) (attached to verbs to form...)
 2. 1a → interjection marking hesitation, equivalent to 'uh'...
 3. 2a → linking particle connecting clauses or phrases...
 ...

All tasks completed!
Files created:
  - pangasinan_dictionary_combined_sorted.json (combined and sorted)
  - Individual sorted files in 'json_files/' directory
```

## JSON Output Format

Each dictionary entry is stored in the following JSON format:

```json
{
  "word": "abalayan",
  "meaning": "to help someone carry a load or burden; to assist in carrying something heavy",
  "source": "Dictionary A"
}
```

Combined entries from multiple dictionaries include source information:

```json
{
  "word": "agawa",
  "meaning": "to make, to do, to create something",
  "source": "Dictionary A, Dictionary B"
}
```

## Technical Details

### Text Processing Features

1. **Metadata Removal**: Filters out JSTOR licensing text, URLs, and academic metadata
2. **Multi-line Continuation**: Intelligently combines definition fragments across multiple lines
3. **Special Pattern Recognition**: Handles entries like "1ainterjection" → "1a" + "interjection ..."
4. **Unicode Normalization**: Proper sorting of accented characters (á→a, ñ→n for sorting purposes)
5. **English Fragment Filtering**: Removes common English words that appear as extraction artifacts

### Sorting Algorithm

The sorting system uses a sophisticated normalization function:

- **Numbered entries** (1a, 2a) are sorted first with special prefixing
- **Prefixed entries** (-n) are sorted at the beginning
- **Accented characters** are normalized for consistent alphabetical order
- **Case-insensitive** sorting maintains proper dictionary order

### Duplicate Handling

The deduplication system:
- Uses lowercase word matching to identify duplicates
- Keeps the first occurrence encountered
- Combines source information from multiple dictionaries
- Preserves all unique word-meaning combinations

## File Dependencies

- **PyPDF2**: PDF text extraction library
- **Standard Python libraries**: `re`, `json`, `os`, `glob`, `unicodedata`

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## License

This project is open source. Please respect the original dictionary sources and any associated copyrights.

## Troubleshooting

### Common Issues

1. **PyPDF2 Import Error**:
   ```bash
   pip install PyPDF2
   ```

2. **No PDF files found**:
   - Ensure PDF files are in the `Dictionary/` folder
   - Check file naming matches expected patterns

3. **Empty extraction results**:
   - Verify PDF files contain readable text (not just images)
   - Check if PDFs are password-protected

4. **Unicode/accent issues**:
   - Ensure your terminal supports UTF-8 encoding
   - Files are saved with UTF-8 encoding by default

### Performance Notes

- Processing time depends on PDF file size and complexity
- Large dictionaries may take several minutes to process
- Memory usage scales with the total number of entries extracted

## Acknowledgments

- Built for processing Pangasinan-English dictionary resources
- Uses PyPDF2 for reliable PDF text extraction
- Designed to handle academic PDF formatting challenges