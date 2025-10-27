"""
FastAPI-based Translation API for Pangasinan ↔ English
Serves the machine learning translation model via REST API
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
import uvicorn
from datetime import datetime
import os
import json
from ml_translator import PangasinanTranslator

# Initialize FastAPI app
app = FastAPI(
    title="Pangasinan Translation API",
    description="Machine Learning-based Pangasinan ↔ English Translation API",
    version="1.0.0"
)

# Enable CORS for web applications
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global translator instance
translator = None
training_status = {
    "is_training": False,
    "progress": 0,
    "message": "Not started"
}


# Request/Response Models
class TranslationRequest(BaseModel):
    text: str = Field(..., description="Text to translate", example="agew")
    max_length: int = Field(50, description="Maximum output length", ge=1, le=100)


class TranslationResponse(BaseModel):
    original: str
    translation: str
    confidence: Optional[float] = None
    timestamp: str


class TrainingRequest(BaseModel):
    dataset_path: str = Field("midterm_dictionary.json", description="Path to training dataset")
    epochs: int = Field(30, description="Number of training epochs", ge=1, le=100)
    batch_size: int = Field(32, description="Batch size for training", ge=1, le=128)
    learning_rate: float = Field(0.001, description="Learning rate", gt=0)


class TrainingResponse(BaseModel):
    message: str
    status: str


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    timestamp: str


class BatchTranslationRequest(BaseModel):
    texts: List[str] = Field(..., description="List of texts to translate")
    max_length: int = Field(50, description="Maximum output length", ge=1, le=100)


class BatchTranslationResponse(BaseModel):
    translations: List[Dict[str, str]]
    total: int
    timestamp: str


# API Endpoints

@app.on_event("startup")
async def startup_event():
    """Load model on startup if available"""
    global translator
    translator = PangasinanTranslator()
    
    # Try to load pre-trained model
    try:
        translator.load_model('best_model')
        print("✓ Pre-trained model loaded successfully")
    except FileNotFoundError:
        print("⚠ No pre-trained model found. Train a model first using /train endpoint")


@app.get("/", response_model=Dict[str, str])
async def root():
    """API root endpoint"""
    return {
        "message": "Pangasinan Translation API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "translate": "/translate",
            "batch_translate": "/batch-translate",
            "train": "/train",
            "health": "/health",
            "models": "/models"
        }
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        model_loaded=translator is not None and translator.model is not None,
        timestamp=datetime.now().isoformat()
    )


@app.post("/translate", response_model=TranslationResponse)
async def translate(request: TranslationRequest):
    """
    Translate Pangasinan text to English
    
    - **text**: The Pangasinan text to translate
    - **max_length**: Maximum length of translation output
    """
    if translator is None or translator.model is None:
        raise HTTPException(
            status_code=503,
            detail="Translation model not loaded. Train or load a model first."
        )
    
    try:
        translation = translator.translate(request.text, request.max_length)
        
        return TranslationResponse(
            original=request.text,
            translation=translation,
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation error: {str(e)}")


@app.post("/batch-translate", response_model=BatchTranslationResponse)
async def batch_translate(request: BatchTranslationRequest):
    """
    Translate multiple Pangasinan texts to English
    
    - **texts**: List of Pangasinan texts to translate
    - **max_length**: Maximum length of translation output
    """
    if translator is None or translator.model is None:
        raise HTTPException(
            status_code=503,
            detail="Translation model not loaded. Train or load a model first."
        )
    
    try:
        translations = []
        for text in request.texts:
            translation = translator.translate(text, request.max_length)
            translations.append({
                "original": text,
                "translation": translation
            })
        
        return BatchTranslationResponse(
            translations=translations,
            total=len(translations),
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch translation error: {str(e)}")


def train_model_background(dataset_path: str, epochs: int, batch_size: int, learning_rate: float):
    """Background task for model training"""
    global training_status, translator
    
    try:
        training_status["is_training"] = True
        training_status["message"] = "Training in progress..."
        
        translator = PangasinanTranslator()
        val_loss = translator.train(
            dataset_path,
            epochs=epochs,
            batch_size=batch_size,
            learning_rate=learning_rate
        )
        
        training_status["is_training"] = False
        training_status["progress"] = 100
        training_status["message"] = f"Training complete! Final validation loss: {val_loss:.4f}"
        
    except Exception as e:
        training_status["is_training"] = False
        training_status["message"] = f"Training failed: {str(e)}"


@app.post("/train", response_model=TrainingResponse)
async def train_model(request: TrainingRequest, background_tasks: BackgroundTasks):
    """
    Train the translation model
    
    - **dataset_path**: Path to the training dataset JSON file
    - **epochs**: Number of training epochs
    - **batch_size**: Batch size for training
    - **learning_rate**: Learning rate for optimizer
    
    Note: Training runs in the background. Use /training-status to check progress.
    """
    if training_status["is_training"]:
        raise HTTPException(
            status_code=409,
            detail="Training already in progress"
        )
    
    if not os.path.exists(request.dataset_path):
        raise HTTPException(
            status_code=404,
            detail=f"Dataset file not found: {request.dataset_path}"
        )
    
    # Start training in background
    background_tasks.add_task(
        train_model_background,
        request.dataset_path,
        request.epochs,
        request.batch_size,
        request.learning_rate
    )
    
    training_status["progress"] = 0
    
    return TrainingResponse(
        message="Training started in background",
        status="started"
    )


@app.get("/training-status")
async def get_training_status():
    """Get current training status"""
    return training_status


@app.get("/models")
async def list_models():
    """List available trained models"""
    model_dir = "models"
    
    if not os.path.exists(model_dir):
        return {"models": [], "count": 0}
    
    models = []
    for file in os.listdir(model_dir):
        if file.endswith('.pt'):
            file_path = os.path.join(model_dir, file)
            models.append({
                "name": file[:-3],  # Remove .pt extension
                "size_mb": os.path.getsize(file_path) / (1024 * 1024),
                "modified": datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
            })
    
    return {"models": models, "count": len(models)}


@app.post("/load-model/{model_name}")
async def load_model(model_name: str):
    """Load a specific trained model"""
    global translator
    
    try:
        translator = PangasinanTranslator()
        translator.load_model(model_name)
        
        return {
            "message": f"Model '{model_name}' loaded successfully",
            "status": "success"
        }
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Model '{model_name}' not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error loading model: {str(e)}"
        )


@app.get("/vocab-stats")
async def get_vocab_stats():
    """Get vocabulary statistics"""
    if translator is None or translator.src_vocab is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded"
        )
    
    return {
        "source_vocab": {
            "size": translator.src_vocab.n_words,
            "top_words": sorted(
                translator.src_vocab.word_count.items(),
                key=lambda x: x[1],
                reverse=True
            )[:20]
        },
        "target_vocab": {
            "size": translator.tgt_vocab.n_words,
            "top_words": sorted(
                translator.tgt_vocab.word_count.items(),
                key=lambda x: x[1],
                reverse=True
            )[:20]
        }
    }


@app.post("/evaluate")
async def evaluate_model():
    """Evaluate model on sample test cases"""
    if translator is None or translator.model is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded"
        )
    
    test_cases = [
        {"pangasinan": "agew", "expected": "day"},
        {"pangasinan": "aso", "expected": "dog"},
        {"pangasinan": "maong", "expected": "good"},
        {"pangasinan": "kaaro", "expected": "friend"},
        {"pangasinan": "bahay", "expected": "house"},
    ]
    
    results = []
    correct = 0
    
    for case in test_cases:
        translation = translator.translate(case["pangasinan"])
        is_correct = case["expected"].lower() in translation.lower()
        
        if is_correct:
            correct += 1
        
        results.append({
            "input": case["pangasinan"],
            "expected": case["expected"],
            "predicted": translation,
            "correct": is_correct
        })
    
    accuracy = (correct / len(test_cases)) * 100
    
    return {
        "results": results,
        "accuracy": accuracy,
        "total_tests": len(test_cases),
        "correct": correct
    }


if __name__ == "__main__":
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
