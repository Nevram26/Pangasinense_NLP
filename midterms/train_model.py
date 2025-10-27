#!/usr/bin/env python3
"""
Standalone training script for Pangasinan translator
Run this to train the model before starting the API
"""

import argparse
from ml_translator import PangasinanTranslator


def main():
    parser = argparse.ArgumentParser(
        description='Train Pangasinan-English translation model'
    )
    parser.add_argument(
        '--dataset',
        default='midterm_dictionary.json',
        help='Path to dictionary JSON file'
    )
    parser.add_argument(
        '--epochs',
        type=int,
        default=30,
        help='Number of training epochs (default: 30)'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=32,
        help='Batch size (default: 32)'
    )
    parser.add_argument(
        '--learning-rate',
        type=float,
        default=0.001,
        help='Learning rate (default: 0.001)'
    )
    parser.add_argument(
        '--model-dir',
        default='models',
        help='Directory to save models (default: models)'
    )
    
    args = parser.parse_args()
    
    print("="*70)
    print("Pangasinan-English Translation Model Training")
    print("="*70)
    print(f"Dataset: {args.dataset}")
    print(f"Epochs: {args.epochs}")
    print(f"Batch Size: {args.batch_size}")
    print(f"Learning Rate: {args.learning_rate}")
    print(f"Model Directory: {args.model_dir}")
    print("="*70)
    print()
    
    # Initialize translator
    translator = PangasinanTranslator(model_dir=args.model_dir)
    
    # Train model
    print("Starting training...")
    val_loss = translator.train(
        json_path=args.dataset,
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.learning_rate
    )
    
    print("\n" + "="*70)
    print(f"Training Complete!")
    print(f"Best Validation Loss: {val_loss:.4f}")
    print("="*70)
    
    # Test the model
    print("\nTesting translations:")
    print("-" * 70)
    
    test_words = [
        "agew",
        "aso",
        "bahay",
        "maong",
        "kaaro",
        "danum",
        "pusa",
        "siak",
        "sika"
    ]
    
    for word in test_words:
        try:
            translation = translator.translate(word)
            print(f"  {word:15} → {translation}")
        except Exception as e:
            print(f"  {word:15} → Error: {e}")
    
    print("-" * 70)
    print("\nModel saved! You can now start the API server:")
    print("  python api.py")
    print("\nOr use uvicorn:")
    print("  uvicorn api:app --reload --host 0.0.0.0 --port 8000")
    print()


if __name__ == '__main__':
    main()
