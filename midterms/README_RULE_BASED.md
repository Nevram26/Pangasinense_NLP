# Pangasinan Rule-Based Translation System

## Overview

This is a **rule-based translation system** for Pangasinan ↔ English that uses linguistic rules and morphological analysis to provide accurate, explainable translations.

### Why Rule-Based?

Unlike black-box ML models, rule-based translation is:
- **✅ Transparent**: Every translation decision is based on explicit linguistic rules
- **✅ Explainable**: Can show exactly which rules were applied
- **✅ Linguistically Sound**: Based on actual Pangasinan grammar and morphology
- **✅ Maintainable**: Easy to add new rules and refine existing ones
- **✅ No Training Required**: Works immediately with dictionary data
- **✅ Presentation-Friendly**: Easy to justify and demonstrate

## System Architecture

```
┌─────────────────────────────────────────────────┐
│         Pangasinan Text Input                   │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│           Tokenization                          │
│  • Unicode normalization                        │
│  • Word boundary detection                      │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│      Morphological Analysis                     │
│  • Prefix detection (man-, ma-, pa-, etc.)      │
│  • Suffix detection (-an, -en, etc.)            │
│  • Enclitic detection (-ko, -mo, -to, etc.)     │
│  • Reduplication detection                      │
│  • Root extraction                              │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│         Dictionary Lookup                       │
│  • 30,980 entries                               │
│  • Root word matching                           │
│  • Type-based translation                       │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│         Rule Application                        │
│  • Focus system rules (Actor, Patient, etc.)    │
│  • Aspect rules (Completed, Non-completed)      │
│  • Causative, Ability, Intensive patterns       │
│  • Pronoun substitution                         │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│           English Output                        │
│  • Word-by-word mapping                         │
│  • Applied rules list                           │
│  • Grammatical annotations                      │
└─────────────────────────────────────────────────┘
```

## Linguistic Rules Implemented

### 1. **Affixes (Prefixes & Suffixes)**

#### Actor Focus Prefixes
- `man-`: Non-completed actor focus → "to [verb]"
  - Example: `mangan` → `man` + `angan` → "to eat"
- `nan-`: Completed actor focus → "[verb] (completed)"
  - Example: `nangan` → `nan` + `angan` → "ate"

#### Other Prefixes
- `ma-`: Stative/causative → "become [adj]"
- `pa-`: Causative → "cause to [verb]"
- `maka-`: Ability → "able to [verb]"
- `i-`: Benefactive focus
- `ika-`: Ordinal numbers

#### Suffixes
- `-an`: Locative focus → "place of [noun]"
  - Example: `tuboan` → `tubo` + `an` → "place of growth"
- `-en`: Patient focus → "[verb] (object focus)"
  - Example: `animen` → `anim` + `en` → "six (object)"

#### Enclitics (Possessive)
- `-ko`: "my"
- `-mo`: "your (singular)"
- `-to`: "his/her"
- `-mi`: "our (exclusive)"
- `-tayo`: "our (inclusive)"
- `-yo`: "your (plural)"
- `-da`: "their"

### 2. **Particles**
- `ed`: at/to/in
- `so`/`ray`: the (singular/plural)
- `et`: and
- `ya`: that
- `ta`: because
- `no`: if
- `diad`: from
- `para`: for

### 3. **Pronouns**
- `siak`: I
- `sika`: you (sg)
- `sikato`: he/she
- `sikatayo`: we (inclusive)
- `sikami`: we (exclusive)
- `sikayo`: you (plural)
- `sikara`: they

### 4. **Morphological Patterns**
- **Reduplication**: First syllable/letters repeated → plural/intensive
  - Example: `lalaki` → `la` + `laki` → "men (plural)"

## API Endpoints

### `POST /translate`
Translate Pangasinan to English

**Request:**
```json
{
  "text": "mangan ed abung",
  "show_rules": true
}
```

**Response:**
```json
{
  "original": "mangan ed abung",
  "translation": "to eat at house",
  "word_by_word": "mangan→to eat | ed→at/to/in | abung→house",
  "rules_applied": ["prefix_man", "particle", "direct_lookup"],
  "timestamp": "2025-10-27T..."
}
```

### `GET /health`
Check API status

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "type": "rule_based",
  "timestamp": "2025-10-27T..."
}
```

### `GET /rules`
Get all linguistic rules

**Response:**
```json
{
  "affixes": {
    "description": "Prefixes and suffixes with their grammatical functions",
    "count": 30,
    "examples": {
      "man-": "actor focus (non-completed)",
      "-an": "locative focus",
      ...
    }
  },
  "particles": {...},
  "pronouns": {...}
}
```

### `POST /analyze`
Analyze a single word's morphology

**Request:**
```
POST /analyze?word=mangan
```

**Response:**
```json
{
  "word": "mangan",
  "root": "angan",
  "translation": "to eat",
  "rules": ["prefix_man"],
  "found": true
}
```

### `GET /stats`
Get translator statistics

## Quick Start

### 1. Install Dependencies

```bash
cd midterms
pip install fastapi uvicorn pydantic
```

### 2. Start the API

**Option A: Using the script**
```bash
chmod +x start_rule_api.sh
./start_rule_api.sh
```

**Option B: Direct command**
```bash
python3 rule_based_api.py
```

**Option C: With uvicorn**
```bash
uvicorn rule_based_api:app --reload --port 8000
```

### 3. Test the API

```bash
# Health check
curl http://localhost:8000/health

# Translate
curl -X POST http://localhost:8000/translate \
  -H "Content-Type: application/json" \
  -d '{"text": "mangan ko", "show_rules": true}'

# Get rules
curl http://localhost:8000/rules
```

### 4. Use with Web Interface

1. Make sure the API is running on port 8000
2. Open `translator.html` in a browser
3. Check "Use Rule-Based API" checkbox
4. Optionally check "Show Rules" to see applied rules
5. Enter Pangasinan text and click "Translate ▶"

## Web Interface Features

The integrated web interface provides:

- **Dual Mode**: Toggle between Dictionary and Rule-Based API
- **Rule Visibility**: Option to show which linguistic rules were applied
- **Word-by-Word Breakdown**: See how each word was translated
- **Live Translation**: Real-time translation as you type
- **Fallback Support**: Automatically falls back to dictionary if API is offline
- **Visual Feedback**: Shows connection status and applied rules

## Presentation Talking Points

### Why Rule-Based Translation?

1. **Linguistic Foundation**
   - Based on documented Pangasinan grammar
   - Follows established morphological patterns
   - Uses proven linguistic theory

2. **Transparency & Explainability**
   - Can show exactly why each translation was made
   - Rules are human-readable and verifiable
   - Easy to debug and improve

3. **Immediate Deployment**
   - No training required
   - Works with existing dictionary
   - Fast iteration on rules

4. **Educational Value**
   - Demonstrates understanding of Pangasinan linguistics
   - Shows systematic approach to language structure
   - Can be used as teaching tool

5. **Production Ready**
   - REST API for easy integration
   - Comprehensive error handling
   - Well-documented endpoints

### Advantages Over ML

| Rule-Based | Machine Learning |
|------------|------------------|
| ✅ Explainable | ❌ Black box |
| ✅ No training needed | ❌ Requires training data & compute |
| ✅ Deterministic | ❌ Non-deterministic |
| ✅ Easy to debug | ❌ Hard to debug |
| ✅ Linguistically sound | ❌ May learn wrong patterns |
| ✅ Works immediately | ❌ Needs hours of training |

## Example Translations

### Simple Sentences

**Input:** `mangan ak`
- Word-by-word: `mangan→to eat | ak→I`
- Rules: `[prefix_man, pronoun]`
- **Output:** `to eat I`

**Input:** `abung ko`
- Word-by-word: `abung→house | ko→my`
- Rules: `[direct_lookup, enclitic_ko]`
- **Output:** `house my`

**Input:** `ed Manila`
- Word-by-word: `ed→at/to/in | Manila→Manila`
- Rules: `[particle, direct_lookup]`
- **Output:** `at Manila`

### With Affixes

**Input:** `nalmes`
- Root: `almes`
- Prefix: `na-` (completed aspect)
- Rules: `[prefix_nan]`
- **Output:** `ate (completed)`

**Input:** `tuboan`
- Root: `tubo`
- Suffix: `-an` (locative)
- Rules: `[suffix_an]`
- **Output:** `place of growth`

## Development

### Adding New Rules

1. Open `rule_based_api.py`
2. Find the `affixes` dictionary in `RuleBasedTranslator.__init__`
3. Add your rule:

```python
'new_prefix': {
    'type': 'prefix',
    'focus': 'your_focus',
    'aspect': 'your_aspect',
    'removes': 'new_prefix'
}
```

4. Update the translation logic in `analyze_word()` if needed
5. Restart the API

### Testing New Rules

```python
# In Python REPL
from rule_based_api import RuleBasedTranslator

translator = RuleBasedTranslator('midterm_dictionary.json')
result = translator.analyze_word('yourword')
print(result)
```

## File Structure

```
midterms/
├── rule_based_api.py          # Main API implementation
├── start_rule_api.sh          # Quick-start script
├── midterm_dictionary.json    # Dictionary data (30K+ entries)
└── README_RULE_BASED.md       # This file

../
└── translator.html            # Web interface (integrated)
```

## API Documentation

Once the API is running, visit:
- **Interactive Docs**: http://localhost:8000/docs
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## Troubleshooting

### API won't start
```bash
# Check if port 8000 is available
lsof -i :8000

# Try a different port
uvicorn rule_based_api:app --port 8001
```

### Dictionary not found
```bash
# Make sure you're in the right directory
ls midterm_dictionary.json

# Or update the path in rule_based_api.py
```

### Web interface can't connect
1. Check API is running: `curl http://localhost:8000/health`
2. Check CORS is enabled (it should be by default)
3. Check browser console for errors

## Future Enhancements

- [ ] English → Pangasinan translation
- [ ] More complex sentence patterns
- [ ] Verb phrase rules
- [ ] Context-dependent translations
- [ ] Syntax tree generation
- [ ] Grammar checking

## Credits

**TEAM AMALZEN**
- Rule-based approach for transparent, explainable translation
- Based on Pangasinan linguistic research
- Dictionary: 30,980 entries

## License

Educational use - NLP Midterm Project
