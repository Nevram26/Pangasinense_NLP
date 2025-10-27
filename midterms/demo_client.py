"""
Example client demonstrating how to use the Pangasinan Translation API
This can be used in your presentation or as a reference
"""

import requests
import json


class PangasinanTranslatorClient:
    """Client for interacting with the Pangasinan Translation API"""
    
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def translate(self, text, max_length=50):
        """Translate a single text"""
        response = requests.post(
            f"{self.base_url}/translate",
            json={"text": text, "max_length": max_length}
        )
        response.raise_for_status()
        return response.json()
    
    def batch_translate(self, texts, max_length=50):
        """Translate multiple texts at once"""
        response = requests.post(
            f"{self.base_url}/batch-translate",
            json={"texts": texts, "max_length": max_length}
        )
        response.raise_for_status()
        return response.json()
    
    def get_health(self):
        """Check API health"""
        response = requests.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def get_models(self):
        """List available models"""
        response = requests.get(f"{self.base_url}/models")
        response.raise_for_status()
        return response.json()
    
    def evaluate(self):
        """Evaluate model performance"""
        response = requests.get(f"{self.base_url}/evaluate")
        response.raise_for_status()
        return response.json()
    
    def get_vocab_stats(self):
        """Get vocabulary statistics"""
        response = requests.get(f"{self.base_url}/vocab-stats")
        response.raise_for_status()
        return response.json()


def demo_basic_translation():
    """Demo: Basic translation"""
    print("\n" + "="*70)
    print("DEMO 1: Basic Translation")
    print("="*70)
    
    client = PangasinanTranslatorClient()
    
    # Single word translations
    words = ["agew", "aso", "maong", "kaaro", "bahay"]
    
    print("\nTranslating individual words:")
    print("-" * 70)
    
    for word in words:
        try:
            result = client.translate(word)
            print(f"  {word:15} → {result['translation']}")
        except Exception as e:
            print(f"  {word:15} → Error: {e}")


def demo_batch_translation():
    """Demo: Batch translation"""
    print("\n" + "="*70)
    print("DEMO 2: Batch Translation")
    print("="*70)
    
    client = PangasinanTranslatorClient()
    
    # Multiple words at once
    words = ["agew", "aso", "maong", "kaaro", "bahay", "danum", "pusa"]
    
    print(f"\nTranslating {len(words)} words in one request:")
    print("-" * 70)
    
    try:
        result = client.batch_translate(words)
        
        for item in result['translations']:
            print(f"  {item['original']:15} → {item['translation']}")
        
        print(f"\nTotal: {result['total']} translations")
        print(f"Timestamp: {result['timestamp']}")
        
    except Exception as e:
        print(f"Error: {e}")


def demo_model_evaluation():
    """Demo: Model evaluation"""
    print("\n" + "="*70)
    print("DEMO 3: Model Evaluation")
    print("="*70)
    
    client = PangasinanTranslatorClient()
    
    try:
        result = client.evaluate()
        
        print(f"\nModel Accuracy: {result['accuracy']:.1f}%")
        print(f"Correct: {result['correct']}/{result['total_tests']}")
        print("\nTest Results:")
        print("-" * 70)
        
        for test in result['results']:
            status = "✓" if test['correct'] else "✗"
            print(f"  {status} {test['input']:15} → {test['predicted']:20} (expected: {test['expected']})")
    
    except Exception as e:
        print(f"Error: {e}")


def demo_vocab_statistics():
    """Demo: Vocabulary statistics"""
    print("\n" + "="*70)
    print("DEMO 4: Vocabulary Statistics")
    print("="*70)
    
    client = PangasinanTranslatorClient()
    
    try:
        result = client.get_vocab_stats()
        
        print(f"\nSource Vocabulary (Pangasinan):")
        print(f"  Total words: {result['source_vocab']['size']}")
        print("\n  Top 10 words:")
        for word, count in result['source_vocab']['top_words'][:10]:
            print(f"    {word:20} - {count:4} occurrences")
        
        print(f"\nTarget Vocabulary (English):")
        print(f"  Total words: {result['target_vocab']['size']}")
        print("\n  Top 10 words:")
        for word, count in result['target_vocab']['top_words'][:10]:
            print(f"    {word:20} - {count:4} occurrences")
    
    except Exception as e:
        print(f"Error: {e}")


def demo_health_check():
    """Demo: Health check"""
    print("\n" + "="*70)
    print("DEMO 5: Health Check")
    print("="*70)
    
    client = PangasinanTranslatorClient()
    
    try:
        result = client.get_health()
        
        print(f"\nAPI Status: {result['status']}")
        print(f"Model Loaded: {'Yes' if result['model_loaded'] else 'No'}")
        print(f"Timestamp: {result['timestamp']}")
    
    except Exception as e:
        print(f"Error: {e}")


def demo_presentation_flow():
    """Demo: Complete presentation flow"""
    print("\n" + "="*70)
    print("PRESENTATION DEMO: Complete Translation Flow")
    print("="*70)
    
    client = PangasinanTranslatorClient()
    
    print("\n1. Check API is running...")
    try:
        health = client.get_health()
        print(f"   ✓ API Status: {health['status']}")
        print(f"   ✓ Model Loaded: {health['model_loaded']}")
    except:
        print("   ✗ API not running. Start with: uvicorn api:app --reload")
        return
    
    print("\n2. Translate common Pangasinan words...")
    demo_words = [
        ("agew", "day"),
        ("aso", "dog"),
        ("maong", "good"),
    ]
    
    for pang, expected in demo_words:
        try:
            result = client.translate(pang)
            match = "✓" if expected.lower() in result['translation'].lower() else "~"
            print(f"   {match} {pang:10} → {result['translation']:20} (expected: {expected})")
        except Exception as e:
            print(f"   ✗ {pang:10} → Error: {e}")
    
    print("\n3. Show model performance...")
    try:
        eval_result = client.evaluate()
        print(f"   Accuracy: {eval_result['accuracy']:.1f}%")
        print(f"   Correct: {eval_result['correct']}/{eval_result['total_tests']}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n4. Batch translation example...")
    try:
        batch_result = client.batch_translate(["agew", "aso", "maong"])
        print(f"   Translated {batch_result['total']} words in one request")
        for item in batch_result['translations'][:3]:
            print(f"     • {item['original']} → {item['translation']}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "="*70)
    print("Demo complete! Ready for presentation.")
    print("="*70)


if __name__ == "__main__":
    """
    Run different demos based on your needs
    """
    
    print("\n" + "="*70)
    print("  Pangasinan Translation API - Client Examples")
    print("="*70)
    print("\nMake sure the API server is running:")
    print("  uvicorn api:app --reload --host 0.0.0.0 --port 8000")
    print("="*70)
    
    # Run all demos
    try:
        demo_health_check()
        demo_basic_translation()
        demo_batch_translation()
        demo_model_evaluation()
        demo_vocab_statistics()
        
        print("\n\n")
        print("="*70)
        print("  PRESENTATION-READY DEMO")
        print("="*70)
        demo_presentation_flow()
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Cannot connect to API server")
        print("\nPlease start the server first:")
        print("  uvicorn api:app --reload --host 0.0.0.0 --port 8000")
        print("\nOr use:")
        print("  ./start_api.sh  (macOS/Linux)")
        print("  start_api.bat   (Windows)")
    except Exception as e:
        print(f"\n❌ Error: {e}")
