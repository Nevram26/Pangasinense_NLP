#!/usr/bin/env python3
"""
Test script for the Pangasinan Translation API
"""

import requests
import time
import json

BASE_URL = "http://localhost:8000"


def print_section(title):
    """Print a section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def test_health():
    """Test health endpoint"""
    print_section("Health Check")
    response = requests.get(f"{BASE_URL}/health")
    print(json.dumps(response.json(), indent=2))
    return response.status_code == 200


def test_single_translation():
    """Test single translation"""
    print_section("Single Translation")
    
    test_words = [
        "agew",
        "aso",
        "maong",
        "kaaro",
        "bahay"
    ]
    
    for word in test_words:
        try:
            response = requests.post(
                f"{BASE_URL}/translate",
                json={"text": word}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"  {word:15} → {data['translation']}")
            else:
                print(f"  {word:15} → Error: {response.status_code}")
        except Exception as e:
            print(f"  {word:15} → Error: {e}")


def test_batch_translation():
    """Test batch translation"""
    print_section("Batch Translation")
    
    texts = ["agew", "aso", "maong", "kaaro"]
    
    try:
        response = requests.post(
            f"{BASE_URL}/batch-translate",
            json={"texts": texts}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"Total translations: {data['total']}\n")
            
            for item in data['translations']:
                print(f"  {item['original']:15} → {item['translation']}")
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Error: {e}")


def test_models():
    """Test model listing"""
    print_section("Available Models")
    
    try:
        response = requests.get(f"{BASE_URL}/models")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Total models: {data['count']}\n")
            
            for model in data['models']:
                print(f"  Name: {model['name']}")
                print(f"    Size: {model['size_mb']:.2f} MB")
                print(f"    Modified: {model['modified']}\n")
        else:
            print(f"Error: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")


def test_vocab_stats():
    """Test vocabulary statistics"""
    print_section("Vocabulary Statistics")
    
    try:
        response = requests.get(f"{BASE_URL}/vocab-stats")
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"Source Vocabulary Size: {data['source_vocab']['size']}")
            print("\nTop 10 Source Words:")
            for word, count in data['source_vocab']['top_words'][:10]:
                print(f"  {word:20} - {count} occurrences")
            
            print(f"\nTarget Vocabulary Size: {data['target_vocab']['size']}")
            print("\nTop 10 Target Words:")
            for word, count in data['target_vocab']['top_words'][:10]:
                print(f"  {word:20} - {count} occurrences")
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Error: {e}")


def test_evaluation():
    """Test model evaluation"""
    print_section("Model Evaluation")
    
    try:
        response = requests.get(f"{BASE_URL}/evaluate")
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"Accuracy: {data['accuracy']:.1f}%")
            print(f"Correct: {data['correct']}/{data['total_tests']}\n")
            
            print("Results:")
            for result in data['results']:
                status = "✓" if result['correct'] else "✗"
                print(f"  {status} {result['input']:15} → {result['predicted']:20} (expected: {result['expected']})")
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Error: {e}")


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("  Pangasinan Translation API - Test Suite")
    print("="*70)
    print(f"  Testing: {BASE_URL}")
    print("="*70)
    
    # Check if server is running
    try:
        requests.get(BASE_URL, timeout=2)
    except requests.exceptions.RequestException:
        print("\n❌ Error: API server is not running!")
        print("\nPlease start the server first:")
        print("  uvicorn api:app --reload --host 0.0.0.0 --port 8000")
        print("\nOr:")
        print("  python api.py")
        return
    
    # Run tests
    tests = [
        ("Health Check", test_health),
        ("Single Translation", test_single_translation),
        ("Batch Translation", test_batch_translation),
        ("Model Listing", test_models),
        ("Vocabulary Stats", test_vocab_stats),
        ("Evaluation", test_evaluation),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"\n❌ Test failed: {test_name}")
            print(f"   Error: {e}")
            failed += 1
        
        time.sleep(0.5)  # Small delay between tests
    
    # Summary
    print("\n" + "="*70)
    print("  Test Summary")
    print("="*70)
    print(f"  Passed: {passed}")
    print(f"  Failed: {failed}")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
