"""
Rule-Based Pangasinan ↔ English Translator API
FastAPI implementation with linguistic rules
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
import json
import re
from datetime import datetime

app = FastAPI(
    title="Pangasinan Rule-Based Translation API",
    description="Rule-based translation using linguistic patterns and dictionary lookup",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global dictionary
DICTIONARY = {}


class TranslationRequest(BaseModel):
    text: str = Field(..., description="Text to translate")
    source_lang: str = Field("pang", description="Source language: 'pang' or 'eng'")
    target_lang: str = Field("eng", description="Target language: 'pang' or 'eng'")
    show_rules: bool = Field(False, description="Show applied rules")


class TranslationResponse(BaseModel):
    original: str
    translation: str
    word_by_word: Optional[str] = None
    rules_applied: Optional[List[str]] = None
    timestamp: str


class RuleBasedTranslator:
    """Rule-based translator using linguistic patterns"""
    
    def __init__(self, dictionary_path: str):
        self.dictionary = self.load_dictionary(dictionary_path)
        
        # Pangasinan linguistic rules
        self.affixes = {
            # Actor focus prefixes
            'man': {'type': 'prefix', 'focus': 'actor', 'aspect': 'non-completed', 'removes': 'man'},
            'nan': {'type': 'prefix', 'focus': 'actor', 'aspect': 'completed', 'removes': 'nan'},
            'ma': {'type': 'prefix', 'focus': 'stative', 'removes': 'ma'},
            'mi': {'type': 'prefix', 'focus': 'reciprocal', 'removes': 'mi'},
            'maN': {'type': 'nasal_prefix', 'focus': 'actor', 'aspect': 'non-completed'},
            'aN': {'type': 'nasal_prefix', 'focus': 'actor', 'aspect': 'completed'},
            'pa': {'type': 'prefix', 'focus': 'causative', 'removes': 'pa'},
            'paN': {'type': 'nasal_prefix', 'focus': 'causative'},
            'i': {'type': 'prefix', 'focus': 'benefactive', 'removes': 'i'},
            'in': {'type': 'prefix', 'focus': 'completed', 'removes': 'in'},
            'ika': {'type': 'prefix', 'focus': 'ordinal', 'removes': 'ika'},
            'ka': {'type': 'prefix', 'focus': 'abstract', 'removes': 'ka'},
            'maka': {'type': 'prefix', 'focus': 'ability', 'removes': 'maka'},
            'paka': {'type': 'prefix', 'focus': 'intensive', 'removes': 'paka'},
            
            # Suffixes
            'an': {'type': 'suffix', 'focus': 'locative', 'removes': 'an'},
            'en': {'type': 'suffix', 'focus': 'patient', 'removes': 'en'},
            'in': {'type': 'suffix', 'focus': 'completed', 'removes': 'in'},
            
            # Genitive enclitics
            'ko': {'type': 'enclitic', 'meaning': 'my', 'removes': 'ko'},
            'mo': {'type': 'enclitic', 'meaning': 'your (sg)', 'removes': 'mo'},
            'to': {'type': 'enclitic', 'meaning': 'his/her', 'removes': 'to'},
            'mi': {'type': 'enclitic', 'meaning': 'our (excl)', 'removes': 'mi'},
            'tayo': {'type': 'enclitic', 'meaning': 'our (incl)', 'removes': 'tayo'},
            'yo': {'type': 'enclitic', 'meaning': 'your (pl)', 'removes': 'yo'},
            'da': {'type': 'enclitic', 'meaning': 'their', 'removes': 'da'},
        }
        
        # Common particles
        self.particles = {
            'ed': 'at/to/in',
            'na': 'already',
            'so': 'the',
            'ray': 'the (pl)',
            'et': 'and',
            'ya': 'that',
            'ta': 'because',
            'no': 'if',
            'diad': 'from',
            'para': 'for',
            'ni': 'of',
        }
        
        # Pronouns
        self.pronouns = {
            'siak': 'I',
            'sika': 'you (sg)',
            'sikato': 'he/she',
            'sikatayo': 'we (incl)',
            'sikami': 'we (excl)',
            'sikayo': 'you (pl)',
            'sikara': 'they',
            'ak': 'I',
            'ka': 'you',
        }
        
        # Demonstratives
        self.demonstratives = {
            'itan': 'this',
            'iyan': 'that',
            'yaran': 'that (far)',
            'yan': 'that',
            'tan': 'this',
        }
    
    def load_dictionary(self, path: str) -> Dict:
        """Load dictionary and create lookup index for both directions"""
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        pang_to_eng = {}
        eng_to_pang = {}
        
        for entry in data:
            pang_word = entry.get('word', '').lower().strip()
            # Use normalized form if available, otherwise normalize the word
            normalized_word = entry.get('normalized form', self.normalize(pang_word))
            eng_meaning = entry.get('meaning', '').lower().strip()
            
            if pang_word and eng_meaning:
                entry_data = {
                    'meaning': eng_meaning,
                    'translation': entry.get('translation', eng_meaning),
                    'root': entry.get('root', ''),
                    'pos': entry.get('POS', ''),  # Use enriched POS tags (capital POS)
                    'morphology': entry.get('morphology', {}),  # Use enriched morphology
                    'type': entry.get('type', ''),
                    'process_meaning': entry.get('process meaning', ''),
                }
                
                # Pangasinan -> English
                # Store by both original and normalized forms
                pang_to_eng[pang_word] = entry_data
                pang_to_eng[normalized_word] = entry_data
                
                # English -> Pangasinan (reverse lookup)
                # Handle multiple English translations separated by commas, semicolons, or "or"
                eng_variants = re.split(r'[;,]|\s+or\s+', eng_meaning)
                for eng_var in eng_variants:
                    eng_var = eng_var.strip()
                    if eng_var and len(eng_var) > 1:  # Skip single letters
                        if eng_var not in eng_to_pang:
                            eng_to_pang[eng_var] = pang_word
        
        return {'pang_to_eng': pang_to_eng, 'eng_to_pang': eng_to_pang}
    
    def normalize(self, text: str) -> str:
        """Normalize text for lookup"""
        # Remove diacritics and lowercase
        text = text.lower()
        replacements = {'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u', 'ñ': 'ny'}
        for old, new in replacements.items():
            text = text.replace(old, new)
        return text
    
    def tokenize(self, text: str) -> List[str]:
        """Tokenize text into words"""
        return re.findall(r'\w+|[^\w\s]', text.lower())
    
    def validate_affix(self, affix: str, affix_info: Dict, root_pos: str) -> bool:
        """Validate if an affix can attach to a root with given POS tag"""
        if not root_pos:
            return True  # If no POS tag, allow the affix (permissive mode)
        
        # Define valid POS combinations for different affix types
        affix_type = affix_info.get('type', '')
        affix_focus = affix_info.get('focus', '')
        
        # Verb affixes (actor, patient, locative focus)
        verb_affixes = ['actor', 'patient', 'locative', 'benefactive', 'completed', 'ability']
        if affix_focus in verb_affixes:
            return root_pos in ['VERB', 'ADJECTIVE']  # Adjectives can sometimes be verbalized
        
        # Causative affixes can attach to verbs, adjectives, and some nouns
        if affix_focus == 'causative':
            return root_pos in ['VERB', 'ADJECTIVE', 'NOUN']
        
        # Stative affixes typically attach to adjectives
        if affix_focus == 'stative':
            return root_pos in ['ADJECTIVE', 'VERB']
        
        # Abstract noun formation (ka-) can attach to adjectives
        if affix_focus == 'abstract':
            return root_pos in ['ADJECTIVE', 'VERB']
        
        # Ordinal (ika-) attaches to numbers/nouns
        if affix_focus == 'ordinal':
            return root_pos in ['NOUN', 'NUMBER']
        
        # Reciprocal typically on verbs
        if affix_focus == 'reciprocal':
            return root_pos in ['VERB']
        
        # Enclitics (possessive markers) can attach to nouns
        if affix_type == 'enclitic':
            return root_pos in ['NOUN', 'VERB', 'ADJECTIVE']  # Possessives are flexible
        
        return True  # Default to permissive if no specific rule
    
    def analyze_word(self, word: str, direction: str = 'pang_to_eng') -> Dict:
        """Analyze word morphology and find root"""
        normalized = self.normalize(word)
        rules_applied = []
        
        # Direct lookup first
        dict_to_use = self.dictionary.get(direction, {})
        if normalized in dict_to_use:
            translation = dict_to_use[normalized]
            pos = None
            morphology = {}
            if isinstance(translation, dict):
                pos = translation.get('pos', '')
                morphology = translation.get('morphology', {})
                translation = translation.get('translation') or translation.get('meaning')
            return {
                'word': word,
                'root': normalized,
                'translation': translation,
                'pos': pos,
                'morphology': morphology,
                'rules': ['direct_lookup'],
                'found': True
            }
        
        # Check pronouns
        if normalized in self.pronouns:
            return {
                'word': word,
                'root': normalized,
                'translation': self.pronouns[normalized],
                'rules': ['pronoun'],
                'found': True
            }
        
        # Check particles
        if normalized in self.particles:
            return {
                'word': word,
                'root': normalized,
                'translation': self.particles[normalized],
                'rules': ['particle'],
                'found': True
            }
        
        # Check demonstratives
        if normalized in self.demonstratives:
            return {
                'word': word,
                'root': normalized,
                'translation': self.demonstratives[normalized],
                'rules': ['demonstrative'],
                'found': True
            }
        
        # Try removing affixes (only for Pangasinan -> English)
        potential_root = normalized
        
        if direction == 'pang_to_eng':
            # Try prefixes
            for prefix, info in self.affixes.items():
                if info['type'] in ['prefix', 'nasal_prefix'] and potential_root.startswith(prefix.lower()):
                    candidate_root = potential_root[len(prefix):]
                    if candidate_root in self.dictionary['pang_to_eng']:
                        root_entry = self.dictionary['pang_to_eng'][candidate_root]
                        root_pos = root_entry.get('pos', '')
                        translation = root_entry.get('translation') or root_entry.get('meaning')
                        
                        # POS-aware rule validation
                        valid_affix = self.validate_affix(prefix, info, root_pos)
                        if not valid_affix:
                            continue  # Skip invalid affix-POS combinations
                        
                        # Apply rule meaning
                        if info['focus'] == 'actor':
                            translation = f"to {translation}" if info.get('aspect') == 'non-completed' else f"{translation} (completed)"
                        elif info['focus'] == 'causative':
                            translation = f"cause to {translation}"
                        elif info['focus'] == 'ability':
                            translation = f"able to {translation}"
                        elif info['focus'] == 'stative':
                            translation = f"become {translation}"
                        
                        rules_applied.append(f"prefix_{prefix}")
                        return {
                            'word': word,
                            'root': candidate_root,
                            'translation': translation,
                            'pos': root_pos,
                            'rules': rules_applied,
                            'found': True
                        }
        
            # Try suffixes
            for suffix, info in self.affixes.items():
                if info['type'] in ['suffix', 'enclitic'] and potential_root.endswith(suffix.lower()):
                    candidate_root = potential_root[:-len(suffix)]
                    if candidate_root in self.dictionary['pang_to_eng']:
                        root_entry = self.dictionary['pang_to_eng'][candidate_root]
                        root_pos = root_entry.get('pos', '')
                        translation = root_entry.get('translation') or root_entry.get('meaning')
                        
                        # POS-aware rule validation
                        valid_affix = self.validate_affix(suffix, info, root_pos)
                        if not valid_affix:
                            continue  # Skip invalid affix-POS combinations
                        
                        # Apply rule meaning
                        if info['type'] == 'enclitic' and 'meaning' in info:
                            translation = f"{translation} {info['meaning']}"
                        elif info['focus'] == 'locative':
                            translation = f"place of {translation}"
                        elif info['focus'] == 'patient':
                            translation = f"{translation} (object focus)"
                        
                        rules_applied.append(f"suffix_{suffix}")
                        return {
                            'word': word,
                            'root': candidate_root,
                            'translation': translation,
                            'pos': root_pos,
                            'rules': rules_applied,
                            'found': True
                        }
            
            # Try reduplication (first two letters repeated)
            if len(normalized) > 4:
                first_two = normalized[:2]
                if normalized[2:4] == first_two:
                    candidate_root = normalized[2:]
                    if candidate_root in self.dictionary['pang_to_eng']:
                        translation = self.dictionary['pang_to_eng'][candidate_root]['translation'] or self.dictionary['pang_to_eng'][candidate_root]['meaning']
                        rules_applied.append('reduplication')
                        return {
                            'word': word,
                            'root': candidate_root,
                            'translation': f"{translation} (plural/intensive)",
                            'rules': rules_applied,
                            'found': True
                        }
        
        # Not found
        return {
            'word': word,
            'root': word,
            'translation': word,
            'rules': ['not_found'],
            'found': False
        }
    
    def translate(self, text: str, source_lang: str = 'pang', target_lang: str = 'eng', show_rules: bool = False) -> Dict:
        """Translate between Pangasinan and English using rules"""
        tokens = self.tokenize(text)
        translations = []
        all_rules = []
        word_by_word = []
        
        # Determine direction
        direction = 'pang_to_eng' if source_lang == 'pang' else 'eng_to_pang'
        
        for token in tokens:
            if re.match(r'\w+', token):
                analysis = self.analyze_word(token, direction)
                translations.append(analysis['translation'])
                word_by_word.append(f"{token}→{analysis['translation']}")
                if show_rules and analysis['rules']:
                    all_rules.extend(analysis['rules'])
            else:
                translations.append(token)
        
        return {
            'translation': ' '.join(translations),
            'word_by_word': ' | '.join(word_by_word),
            'rules_applied': list(set(all_rules)) if show_rules else None
        }


# Initialize translator
translator = None


@app.on_event("startup")
async def startup_event():
    """Load dictionary on startup"""
    global translator
    try:
        # Use absolute path or check if file exists in midterms directory
        dict_path = 'midterm_dictionary_enriched.json'
        import os
        if not os.path.exists(dict_path):
            dict_path = os.path.join(os.path.dirname(__file__), 'midterm_dictionary_enriched.json')
        if not os.path.exists(dict_path):
            # Try parent directory
            dict_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'midterm_dictionary_enriched.json')
        
        translator = RuleBasedTranslator(dict_path)
        print("✓ Enriched dictionary loaded successfully")
    except Exception as e:
        print(f"✗ Failed to load dictionary: {e}")


@app.get("/")
async def root():
    """API root"""
    return {
        "name": "Pangasinan Rule-Based Translation API",
        "version": "1.0.0",
        "description": "Translation using linguistic rules and morphological analysis",
        "endpoints": {
            "translate": "/translate",
            "health": "/health",
            "rules": "/rules",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "model_loaded": translator is not None,
        "type": "rule_based",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/translate", response_model=TranslationResponse)
async def translate(request: TranslationRequest):
    """
    Translate between Pangasinan and English using rule-based approach
    
    - **text**: Text to translate
    - **source_lang**: Source language ('pang' or 'eng')
    - **target_lang**: Target language ('pang' or 'eng')
    - **show_rules**: Show which linguistic rules were applied
    """
    if translator is None:
        raise HTTPException(status_code=503, detail="Translator not initialized")
    
    try:
        result = translator.translate(
            request.text, 
            request.source_lang, 
            request.target_lang, 
            request.show_rules
        )
        
        return TranslationResponse(
            original=request.text,
            translation=result['translation'],
            word_by_word=result['word_by_word'],
            rules_applied=result['rules_applied'],
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation error: {str(e)}")


@app.get("/rules")
async def get_rules():
    """Get linguistic rules used by the translator"""
    if translator is None:
        raise HTTPException(status_code=503, detail="Translator not initialized")
    
    return {
        "affixes": {
            "description": "Prefixes and suffixes with their grammatical functions",
            "count": len(translator.affixes),
            "examples": {
                "man-": "actor focus (non-completed)",
                "-an": "locative focus",
                "-en": "patient focus",
                "ma-": "stative/causative"
            }
        },
        "particles": {
            "description": "Common grammatical particles",
            "count": len(translator.particles),
            "examples": dict(list(translator.particles.items())[:5])
        },
        "pronouns": {
            "description": "Personal pronouns",
            "count": len(translator.pronouns),
            "examples": dict(list(translator.pronouns.items())[:5])
        },
        "total_dictionary_entries": {
            "pang_to_eng": len(translator.dictionary.get('pang_to_eng', {})),
            "eng_to_pang": len(translator.dictionary.get('eng_to_pang', {}))
        }
    }


@app.post("/analyze")
async def analyze_word(word: str):
    """Analyze morphological structure of a word"""
    if translator is None:
        raise HTTPException(status_code=503, detail="Translator not initialized")
    
    analysis = translator.analyze_word(word)
    return analysis


@app.get("/stats")
async def get_stats():
    """Get translator statistics"""
    if translator is None:
        raise HTTPException(status_code=503, detail="Translator not initialized")
    
    return {
        "dictionary_size": {
            "pang_to_eng": len(translator.dictionary.get('pang_to_eng', {})),
            "eng_to_pang": len(translator.dictionary.get('eng_to_pang', {}))
        },
        "affixes_count": len(translator.affixes),
        "particles_count": len(translator.particles),
        "pronouns_count": len(translator.pronouns),
        "demonstratives_count": len(translator.demonstratives),
        "type": "rule_based",
        "approach": "Morphological analysis + Dictionary lookup + Linguistic rules",
        "supports_bidirectional": True
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
