"""
Test Bidirectional Translation and Rule Application
Tests both Pangasinan->English and English->Pangasinan
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("=" * 60)
    print("HEALTH CHECK")
    print("=" * 60)
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {data['status']}")
            print(f"✅ Type: {data['type']}")
            print(f"✅ Model loaded: {data['model_loaded']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Start it with:")
        print("   cd midterms && python3 rule_based_api.py")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_translation(text, source_lang="pang", target_lang="eng", show_rules=True):
    """Test translation with rules"""
    direction = f"{source_lang} → {target_lang}"
    print(f"\n{'=' * 60}")
    print(f"TEST: {direction}")
    print(f"{'=' * 60}")
    print(f"Input: '{text}'")
    
    try:
        response = requests.post(
            f"{BASE_URL}/translate",
            json={
                "text": text,
                "source_lang": source_lang,
                "target_lang": target_lang,
                "show_rules": show_rules
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Translation: {data['translation']}")
            
            if data.get('word_by_word'):
                print(f"\n📝 Word-by-word:")
                words = data['word_by_word'].split(' | ')
                for w in words:
                    print(f"   {w}")
            
            if data.get('rules_applied'):
                print(f"\n🔧 Rules applied: {', '.join(data['rules_applied'])}")
            else:
                print(f"\n⚠️  No rules were applied!")
            
            return True
        else:
            print(f"❌ Translation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_analyze(word):
    """Test word analysis"""
    print(f"\n{'=' * 60}")
    print(f"ANALYZE WORD: '{word}'")
    print(f"{'=' * 60}")
    
    try:
        response = requests.post(f"{BASE_URL}/analyze?word={word}", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Word: {data['word']}")
            print(f"   Root: {data['root']}")
            print(f"   Translation: {data['translation']}")
            print(f"   Rules: {', '.join(data['rules'])}")
            print(f"   Found: {data['found']}")
            return True
        else:
            print(f"❌ Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_stats():
    """Test stats endpoint"""
    print(f"\n{'=' * 60}")
    print("SYSTEM STATISTICS")
    print(f"{'=' * 60}")
    
    try:
        response = requests.get(f"{BASE_URL}/stats", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"Dictionary size:")
            if isinstance(data['dictionary_size'], dict):
                print(f"  Pang→Eng: {data['dictionary_size']['pang_to_eng']} entries")
                print(f"  Eng→Pang: {data['dictionary_size']['eng_to_pang']} entries")
            else:
                print(f"  {data['dictionary_size']} entries")
            print(f"Affixes: {data['affixes_count']}")
            print(f"Particles: {data['particles_count']}")
            print(f"Pronouns: {data['pronouns_count']}")
            print(f"Type: {data['type']}")
            print(f"Bidirectional: {data.get('supports_bidirectional', False)}")
            return True
        else:
            print(f"❌ Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    print("\n" + "🎯" * 30)
    print(" COMPREHENSIVE BIDIRECTIONAL TRANSLATION TEST")
    print("🎯" * 30 + "\n")
    
    # Health check
    if not test_health():
        return
    
    # Test stats first
    test_stats()
    
    print("\n" + "━" * 60)
    print("PANGASINAN → ENGLISH TESTS")
    print("━" * 60)
    
    # Test 1: Simple word
    test_translation("abung", "pang", "eng", True)
    
    # Test 2: Word with prefix
    test_translation("mangan", "pang", "eng", True)
    
    # Test 3: Word with enclitic
    test_translation("ko", "pang", "eng", True)
    
    # Test 4: Phrase with multiple words
    test_translation("mangan ko", "pang", "eng", True)
    
    # Test 5: Longer phrase
    test_translation("mangan ed abung", "pang", "eng", True)
    
    # Test 6: Complex phrase
    test_translation("mangan ak ed abung ko", "pang", "eng", True)
    
    print("\n" + "━" * 60)
    print("ENGLISH → PANGASINAN TESTS")
    print("━" * 60)
    
    # Test 7: English to Pangasinan
    test_translation("house", "eng", "pang", True)
    
    # Test 8: English phrase
    test_translation("eat", "eng", "pang", True)
    
    # Test 9: Multiple words
    test_translation("my house", "eng", "pang", True)
    
    # Test 10: Complex English phrase
    test_translation("I eat at my house", "eng", "pang", True)
    
    print("\n" + "━" * 60)
    print("WORD ANALYSIS TESTS")
    print("━" * 60)
    
    # Test morphological analysis
    test_analyze("mangan")
    test_analyze("abung")
    test_analyze("tuboan")
    
    print("\n" + "🎯" * 30)
    print(" TEST SUMMARY")
    print("🎯" * 30)
    print("\n✅ All tests completed!")
    print("\n💡 Next steps:")
    print("   1. Open translator.html in browser")
    print("   2. Check 'Use Rule-Based API'")
    print("   3. Try translating both directions")
    print("   4. Enable 'Show Rules' to see linguistic rules")


if __name__ == "__main__":
    main()
