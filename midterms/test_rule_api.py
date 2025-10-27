"""
Test script for Rule-Based Translation API
Quick verification that everything works
"""

import requests
import json

BASE_URL = "http://localhost:8000"


def test_health():
    """Test health endpoint"""
    print("🔍 Testing /health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed!")
            print(f"   Status: {data['status']}")
            print(f"   Type: {data['type']}")
            print(f"   Model loaded: {data['model_loaded']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Is it running?")
        print("   Run: ./start_rule_api.sh")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_translate(text, show_rules=False):
    """Test translation"""
    print(f"\n🔍 Translating: '{text}'")
    try:
        response = requests.post(
            f"{BASE_URL}/translate",
            json={"text": text, "show_rules": show_rules},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Translation successful!")
            print(f"   Original: {data['original']}")
            print(f"   Translation: {data['translation']}")
            if data.get('word_by_word'):
                print(f"   Word-by-word: {data['word_by_word']}")
            if data.get('rules_applied'):
                print(f"   Rules applied: {', '.join(data['rules_applied'])}")
            return True
        else:
            print(f"❌ Translation failed: {response.status_code}")
            print(f"   {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_rules():
    """Test rules endpoint"""
    print("\n🔍 Testing /rules endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/rules", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Rules retrieved!")
            print(f"   Affixes: {data['affixes']['count']}")
            print(f"   Particles: {data['particles']['count']}")
            print(f"   Pronouns: {data['pronouns']['count']}")
            print(f"   Dictionary entries: {data['total_dictionary_entries']}")
            return True
        else:
            print(f"❌ Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_analyze(word):
    """Test word analysis"""
    print(f"\n🔍 Analyzing word: '{word}'")
    try:
        response = requests.post(f"{BASE_URL}/analyze?word={word}", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Analysis complete!")
            print(f"   Word: {data['word']}")
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
    print("\n🔍 Testing /stats endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/stats", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Stats retrieved!")
            print(f"   Type: {data['type']}")
            print(f"   Approach: {data['approach']}")
            return True
        else:
            print(f"❌ Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    print("=" * 60)
    print("  Pangasinan Rule-Based Translation API - Test Suite")
    print("=" * 60)
    
    # Test health
    if not test_health():
        print("\n❌ API is not running or not accessible")
        print("   Start the API with: ./start_rule_api.sh")
        return
    
    # Test basic translation
    test_translate("mangan")
    test_translate("abung ko", show_rules=True)
    test_translate("mangan ed abung", show_rules=True)
    
    # Test rules
    test_rules()
    
    # Test word analysis
    test_analyze("mangan")
    test_analyze("tuboan")
    
    # Test stats
    test_stats()
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)
    print("\n💡 Next steps:")
    print("   1. Open translator.html in your browser")
    print("   2. Check 'Use Rule-Based API' checkbox")
    print("   3. Try translating Pangasinan text")
    print("   4. Enable 'Show Rules' to see linguistic rules applied")


if __name__ == "__main__":
    main()
