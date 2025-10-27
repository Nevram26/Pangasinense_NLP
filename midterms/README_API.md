# Pangasinan Translation API

Machine Learning-based REST API for Pangasinan ↔ English translation using FastAPI and PyTorch.

## Features

- 🧠 **Neural Machine Translation** - LSTM-based Seq2Seq model with attention
- 🚀 **FastAPI** - Modern, fast REST API
- 📊 **Training Endpoint** - Train models via API
- 🔄 **Batch Translation** - Translate multiple texts at once
- 📈 **Evaluation** - Built-in model evaluation
- 💾 **Model Management** - Save, load, and list models

## Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

## Quick Start

### 1. Train the Model

```bash
# Train using the training script
python train_model.py --dataset midterm_dictionary.json --epochs 30
```

Or use custom parameters:

```bash
python train_model.py \
  --dataset midterm_dictionary.json \
  --epochs 50 \
  --batch-size 64 \
  --learning-rate 0.0005
```

### 2. Start the API Server

```bash
# Using uvicorn (recommended)
uvicorn api:app --reload --host 0.0.0.0 --port 8000

# Or using the built-in runner
python api.py
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## API Endpoints

### Translation

#### Translate Single Text
```bash
POST /translate
```

**Request:**
```json
{
  "text": "agew",
  "max_length": 50
}
```

**Response:**
```json
{
  "original": "agew",
  "translation": "day",
  "timestamp": "2025-10-27T10:30:00"
}
```

**cURL Example:**
```bash
curl -X POST "http://localhost:8000/translate" \
  -H "Content-Type: application/json" \
  -d '{"text": "agew"}'
```

#### Batch Translation
```bash
POST /batch-translate
```

**Request:**
```json
{
  "texts": ["agew", "aso", "maong"],
  "max_length": 50
}
```

**Response:**
```json
{
  "translations": [
    {"original": "agew", "translation": "day"},
    {"original": "aso", "translation": "dog"},
    {"original": "maong", "translation": "good"}
  ],
  "total": 3,
  "timestamp": "2025-10-27T10:30:00"
}
```

### Training

#### Train Model
```bash
POST /train
```

**Request:**
```json
{
  "dataset_path": "midterm_dictionary.json",
  "epochs": 30,
  "batch_size": 32,
  "learning_rate": 0.001
}
```

**Response:**
```json
{
  "message": "Training started in background",
  "status": "started"
}
```

#### Check Training Status
```bash
GET /training-status
```

**Response:**
```json
{
  "is_training": false,
  "progress": 100,
  "message": "Training complete! Final validation loss: 0.4321"
}
```

### Model Management

#### List Available Models
```bash
GET /models
```

**Response:**
```json
{
  "models": [
    {
      "name": "best_model",
      "size_mb": 45.2,
      "modified": "2025-10-27T10:00:00"
    }
  ],
  "count": 1
}
```

#### Load a Model
```bash
POST /load-model/{model_name}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/load-model/best_model"
```

### Evaluation

#### Evaluate Model
```bash
GET /evaluate
```

**Response:**
```json
{
  "results": [
    {
      "input": "agew",
      "expected": "day",
      "predicted": "day",
      "correct": true
    }
  ],
  "accuracy": 80.0,
  "total_tests": 5,
  "correct": 4
}
```

### Vocabulary Statistics
```bash
GET /vocab-stats
```

### Health Check
```bash
GET /health
```

## Python Client Example

```python
import requests

# Initialize client
base_url = "http://localhost:8000"

# Translate single text
response = requests.post(
    f"{base_url}/translate",
    json={"text": "agew"}
)
print(response.json())
# Output: {'original': 'agew', 'translation': 'day', ...}

# Batch translation
response = requests.post(
    f"{base_url}/batch-translate",
    json={"texts": ["agew", "aso", "maong"]}
)
print(response.json())

# Check health
response = requests.get(f"{base_url}/health")
print(response.json())
```

## JavaScript/Frontend Example

```javascript
// Translate function
async function translate(text) {
  const response = await fetch('http://localhost:8000/translate', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ text: text })
  });
  
  const data = await response.json();
  return data.translation;
}

// Usage
translate('agew').then(translation => {
  console.log(translation); // "day"
});
```

## Model Architecture

The translation system uses:

- **Encoder**: 2-layer bidirectional LSTM
- **Attention Mechanism**: Bahdanau attention
- **Decoder**: 2-layer LSTM with attention
- **Embedding Size**: 256
- **Hidden Size**: 512
- **Dropout**: 0.3

## Training Details

- **Dataset**: Pangasinan dictionary with ~30,000 entries
- **Train/Val Split**: 90/10
- **Optimizer**: Adam
- **Loss Function**: Cross-entropy (ignoring padding)
- **Gradient Clipping**: Max norm of 1.0
- **Teacher Forcing Ratio**: 0.5

## Directory Structure

```
midterms/
├── api.py                    # FastAPI application
├── ml_translator.py          # ML model implementation
├── train_model.py            # Training script
├── requirements.txt          # Python dependencies
├── midterm_dictionary.json   # Training dataset
└── models/                   # Saved models directory
    └── best_model.pt        # Best trained model
```

## Performance Tips

1. **GPU Acceleration**: The model automatically uses GPU if available
2. **Batch Size**: Increase for faster training (if you have enough RAM)
3. **Epochs**: More epochs = better accuracy (but watch for overfitting)
4. **Learning Rate**: Lower = more stable, higher = faster (but less stable)

## Troubleshooting

### Model not found
```bash
# Train a model first
python train_model.py
```

### Out of memory
```bash
# Reduce batch size
python train_model.py --batch-size 16
```

### Poor translation quality
```bash
# Train for more epochs
python train_model.py --epochs 50

# Or adjust learning rate
python train_model.py --learning-rate 0.0005
```

## API Documentation

Visit http://localhost:8000/docs for interactive API documentation with:
- All endpoints
- Request/response schemas
- Try-it-out functionality
- Examples

## License

MIT License - Free to use for educational purposes

## Authors

TEAM AMALZEN - Pangasinan NLP Project
