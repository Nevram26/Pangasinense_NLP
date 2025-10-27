"""
Machine Learning-based Pangasinan ↔ English Translator
Using Transformer architecture with the dictionary dataset
"""

import json
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from typing import List, Dict, Tuple, Optional
import re
from collections import Counter
import pickle
import os


class Vocabulary:
    """Vocabulary class for managing word-to-index mappings"""
    
    def __init__(self):
        self.word2idx = {'<PAD>': 0, '<SOS>': 1, '<EOS>': 2, '<UNK>': 3}
        self.idx2word = {0: '<PAD>', 1: '<SOS>', 2: '<EOS>', 3: '<UNK>'}
        self.word_count = {}
        self.n_words = 4
        
    def add_sentence(self, sentence: str):
        """Add all words in a sentence to vocabulary"""
        for word in self.tokenize(sentence):
            self.add_word(word)
    
    def add_word(self, word: str):
        """Add a word to vocabulary"""
        if word not in self.word2idx:
            self.word2idx[word] = self.n_words
            self.idx2word[self.n_words] = word
            self.word_count[word] = 1
            self.n_words += 1
        else:
            self.word_count[word] += 1
    
    @staticmethod
    def tokenize(text: str) -> List[str]:
        """Tokenize text into words"""
        # Normalize and tokenize
        text = text.lower().strip()
        # Split on whitespace and punctuation
        tokens = re.findall(r'\w+|[^\w\s]', text)
        return tokens
    
    def encode(self, sentence: str, max_length: int = 50) -> List[int]:
        """Convert sentence to indices"""
        tokens = self.tokenize(sentence)
        indices = [self.word2idx.get(token, self.word2idx['<UNK>']) for token in tokens]
        # Add EOS token
        indices.append(self.word2idx['<EOS>'])
        # Pad or truncate
        if len(indices) < max_length:
            indices += [self.word2idx['<PAD>']] * (max_length - len(indices))
        else:
            indices = indices[:max_length]
        return indices
    
    def decode(self, indices: List[int]) -> str:
        """Convert indices back to sentence"""
        words = []
        for idx in indices:
            word = self.idx2word.get(idx, '<UNK>')
            if word in ['<EOS>', '<PAD>']:
                break
            if word not in ['<SOS>', '<UNK>']:
                words.append(word)
        return ' '.join(words)


class TranslationDataset(Dataset):
    """Dataset for Pangasinan-English translation pairs"""
    
    def __init__(self, json_path: str, src_vocab: Vocabulary, tgt_vocab: Vocabulary, 
                 max_length: int = 50, create_vocab: bool = True):
        self.max_length = max_length
        self.src_vocab = src_vocab
        self.tgt_vocab = tgt_vocab
        self.pairs = []
        
        # Load data
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extract translation pairs
        for entry in data:
            pang = entry.get('word', '').strip()
            eng = entry.get('meaning', '').strip()
            
            if pang and eng and len(pang) > 0 and len(eng) > 0:
                # Skip very long entries
                if len(pang.split()) <= 15 and len(eng.split()) <= 20:
                    self.pairs.append((pang, eng))
                    
                    if create_vocab:
                        self.src_vocab.add_sentence(pang)
                        self.tgt_vocab.add_sentence(eng)
        
        print(f"Loaded {len(self.pairs)} translation pairs")
        print(f"Source vocab size: {self.src_vocab.n_words}")
        print(f"Target vocab size: {self.tgt_vocab.n_words}")
    
    def __len__(self):
        return len(self.pairs)
    
    def __getitem__(self, idx):
        src_text, tgt_text = self.pairs[idx]
        src_indices = self.src_vocab.encode(src_text, self.max_length)
        tgt_indices = self.tgt_vocab.encode(tgt_text, self.max_length)
        
        return {
            'src': torch.tensor(src_indices, dtype=torch.long),
            'tgt': torch.tensor(tgt_indices, dtype=torch.long),
            'src_text': src_text,
            'tgt_text': tgt_text
        }


class Encoder(nn.Module):
    """LSTM-based encoder"""
    
    def __init__(self, vocab_size: int, embed_size: int, hidden_size: int, 
                 num_layers: int = 2, dropout: float = 0.3):
        super().__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        self.embedding = nn.Embedding(vocab_size, embed_size, padding_idx=0)
        self.lstm = nn.LSTM(embed_size, hidden_size, num_layers, 
                           batch_first=True, dropout=dropout if num_layers > 1 else 0)
        self.dropout = nn.Dropout(dropout)
    
    def forward(self, x):
        # x: [batch_size, seq_len]
        embedded = self.dropout(self.embedding(x))
        # embedded: [batch_size, seq_len, embed_size]
        
        outputs, (hidden, cell) = self.lstm(embedded)
        # outputs: [batch_size, seq_len, hidden_size]
        # hidden: [num_layers, batch_size, hidden_size]
        
        return outputs, hidden, cell


class Attention(nn.Module):
    """Attention mechanism"""
    
    def __init__(self, hidden_size: int):
        super().__init__()
        self.attn = nn.Linear(hidden_size * 2, hidden_size)
        self.v = nn.Linear(hidden_size, 1, bias=False)
    
    def forward(self, hidden, encoder_outputs):
        # hidden: [batch_size, hidden_size]
        # encoder_outputs: [batch_size, seq_len, hidden_size]
        
        batch_size = encoder_outputs.shape[0]
        seq_len = encoder_outputs.shape[1]
        
        # Repeat hidden state seq_len times
        hidden = hidden.unsqueeze(1).repeat(1, seq_len, 1)
        # hidden: [batch_size, seq_len, hidden_size]
        
        # Calculate attention energies
        energy = torch.tanh(self.attn(torch.cat((hidden, encoder_outputs), dim=2)))
        # energy: [batch_size, seq_len, hidden_size]
        
        attention = self.v(energy).squeeze(2)
        # attention: [batch_size, seq_len]
        
        return torch.softmax(attention, dim=1)


class Decoder(nn.Module):
    """LSTM-based decoder with attention"""
    
    def __init__(self, vocab_size: int, embed_size: int, hidden_size: int, 
                 num_layers: int = 2, dropout: float = 0.3):
        super().__init__()
        self.vocab_size = vocab_size
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        self.embedding = nn.Embedding(vocab_size, embed_size, padding_idx=0)
        self.attention = Attention(hidden_size)
        self.lstm = nn.LSTM(embed_size + hidden_size, hidden_size, num_layers,
                           batch_first=True, dropout=dropout if num_layers > 1 else 0)
        self.fc_out = nn.Linear(hidden_size * 2 + embed_size, vocab_size)
        self.dropout = nn.Dropout(dropout)
    
    def forward(self, x, hidden, cell, encoder_outputs):
        # x: [batch_size, 1]
        # hidden: [num_layers, batch_size, hidden_size]
        # encoder_outputs: [batch_size, seq_len, hidden_size]
        
        embedded = self.dropout(self.embedding(x))
        # embedded: [batch_size, 1, embed_size]
        
        # Calculate attention weights using top layer hidden state
        attn_weights = self.attention(hidden[-1], encoder_outputs)
        # attn_weights: [batch_size, seq_len]
        
        attn_weights = attn_weights.unsqueeze(1)
        # attn_weights: [batch_size, 1, seq_len]
        
        # Apply attention to encoder outputs
        context = torch.bmm(attn_weights, encoder_outputs)
        # context: [batch_size, 1, hidden_size]
        
        # Concatenate embedded input and context
        lstm_input = torch.cat((embedded, context), dim=2)
        # lstm_input: [batch_size, 1, embed_size + hidden_size]
        
        output, (hidden, cell) = self.lstm(lstm_input, (hidden, cell))
        # output: [batch_size, 1, hidden_size]
        
        # Prepare output
        embedded = embedded.squeeze(1)
        output = output.squeeze(1)
        context = context.squeeze(1)
        
        prediction = self.fc_out(torch.cat((output, context, embedded), dim=1))
        # prediction: [batch_size, vocab_size]
        
        return prediction, hidden, cell


class Seq2SeqTranslator(nn.Module):
    """Sequence-to-Sequence translator with attention"""
    
    def __init__(self, src_vocab_size: int, tgt_vocab_size: int,
                 embed_size: int = 256, hidden_size: int = 512, 
                 num_layers: int = 2, dropout: float = 0.3):
        super().__init__()
        
        self.encoder = Encoder(src_vocab_size, embed_size, hidden_size, 
                              num_layers, dropout)
        self.decoder = Decoder(tgt_vocab_size, embed_size, hidden_size,
                              num_layers, dropout)
        
    def forward(self, src, tgt, teacher_forcing_ratio: float = 0.5):
        # src: [batch_size, src_len]
        # tgt: [batch_size, tgt_len]
        
        batch_size = src.shape[0]
        tgt_len = tgt.shape[1]
        tgt_vocab_size = self.decoder.vocab_size
        
        # Tensor to store decoder outputs
        outputs = torch.zeros(batch_size, tgt_len, tgt_vocab_size).to(src.device)
        
        # Encode source sentence
        encoder_outputs, hidden, cell = self.encoder(src)
        
        # First input to decoder is <SOS> token (index 1)
        decoder_input = tgt[:, 0].unsqueeze(1)
        
        for t in range(1, tgt_len):
            # Decode
            output, hidden, cell = self.decoder(decoder_input, hidden, cell, encoder_outputs)
            
            # Store output
            outputs[:, t] = output
            
            # Teacher forcing: use actual next token as next input
            # Otherwise: use predicted token
            teacher_force = torch.rand(1).item() < teacher_forcing_ratio
            top1 = output.argmax(1).unsqueeze(1)
            decoder_input = tgt[:, t].unsqueeze(1) if teacher_force else top1
        
        return outputs


class PangasinanTranslator:
    """High-level translator interface"""
    
    def __init__(self, model_dir: str = 'models'):
        self.model_dir = model_dir
        os.makedirs(model_dir, exist_ok=True)
        
        self.src_vocab = Vocabulary()
        self.tgt_vocab = Vocabulary()
        self.model = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
    def train(self, json_path: str, epochs: int = 50, batch_size: int = 32,
              learning_rate: float = 0.001, save_every: int = 10):
        """Train the translation model"""
        
        print(f"Training on device: {self.device}")
        
        # Create dataset
        dataset = TranslationDataset(json_path, self.src_vocab, self.tgt_vocab, 
                                    create_vocab=True)
        
        # Split into train/val
        train_size = int(0.9 * len(dataset))
        val_size = len(dataset) - train_size
        train_dataset, val_dataset = torch.utils.data.random_split(
            dataset, [train_size, val_size]
        )
        
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=batch_size)
        
        # Create model
        self.model = Seq2SeqTranslator(
            src_vocab_size=self.src_vocab.n_words,
            tgt_vocab_size=self.tgt_vocab.n_words,
            embed_size=256,
            hidden_size=512,
            num_layers=2,
            dropout=0.3
        ).to(self.device)
        
        # Loss and optimizer
        criterion = nn.CrossEntropyLoss(ignore_index=0)  # Ignore padding
        optimizer = torch.optim.Adam(self.model.parameters(), lr=learning_rate)
        
        # Training loop
        best_val_loss = float('inf')
        
        for epoch in range(epochs):
            self.model.train()
            train_loss = 0
            
            for batch in train_loader:
                src = batch['src'].to(self.device)
                tgt = batch['tgt'].to(self.device)
                
                optimizer.zero_grad()
                
                # Forward pass
                output = self.model(src, tgt)
                
                # Reshape for loss calculation
                output_dim = output.shape[-1]
                output = output[:, 1:].reshape(-1, output_dim)
                tgt = tgt[:, 1:].reshape(-1)
                
                # Calculate loss
                loss = criterion(output, tgt)
                
                # Backward pass
                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1)
                optimizer.step()
                
                train_loss += loss.item()
            
            # Validation
            self.model.eval()
            val_loss = 0
            
            with torch.no_grad():
                for batch in val_loader:
                    src = batch['src'].to(self.device)
                    tgt = batch['tgt'].to(self.device)
                    
                    output = self.model(src, tgt, teacher_forcing_ratio=0)
                    
                    output_dim = output.shape[-1]
                    output = output[:, 1:].reshape(-1, output_dim)
                    tgt = tgt[:, 1:].reshape(-1)
                    
                    loss = criterion(output, tgt)
                    val_loss += loss.item()
            
            train_loss /= len(train_loader)
            val_loss /= len(val_loader)
            
            print(f"Epoch {epoch+1}/{epochs} - Train Loss: {train_loss:.4f}, Val Loss: {val_loss:.4f}")
            
            # Save best model
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                self.save_model('best_model')
                print(f"  → Saved best model (val_loss: {val_loss:.4f})")
            
            # Save checkpoint
            if (epoch + 1) % save_every == 0:
                self.save_model(f'checkpoint_epoch_{epoch+1}')
        
        print("Training complete!")
        return best_val_loss
    
    def translate(self, text: str, max_length: int = 50) -> str:
        """Translate Pangasinan text to English"""
        if self.model is None:
            raise ValueError("Model not loaded. Train or load a model first.")
        
        self.model.eval()
        
        with torch.no_grad():
            # Encode input
            src_indices = self.src_vocab.encode(text, max_length)
            src_tensor = torch.tensor([src_indices], dtype=torch.long).to(self.device)
            
            # Encode
            encoder_outputs, hidden, cell = self.model.encoder(src_tensor)
            
            # Start with <SOS> token
            decoder_input = torch.tensor([[1]], dtype=torch.long).to(self.device)
            
            decoded_indices = []
            
            for _ in range(max_length):
                output, hidden, cell = self.model.decoder(decoder_input, hidden, cell, encoder_outputs)
                
                # Get most likely word
                top_idx = output.argmax(1).item()
                
                # Stop if <EOS>
                if top_idx == 2:
                    break
                
                decoded_indices.append(top_idx)
                decoder_input = torch.tensor([[top_idx]], dtype=torch.long).to(self.device)
            
            # Decode to text
            translation = self.tgt_vocab.decode(decoded_indices)
            
        return translation
    
    def save_model(self, name: str = 'model'):
        """Save model and vocabularies"""
        path = os.path.join(self.model_dir, f'{name}.pt')
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'src_vocab': self.src_vocab,
            'tgt_vocab': self.tgt_vocab,
        }, path)
        print(f"Model saved to {path}")
    
    def load_model(self, name: str = 'best_model'):
        """Load model and vocabularies"""
        path = os.path.join(self.model_dir, f'{name}.pt')
        
        if not os.path.exists(path):
            raise FileNotFoundError(f"Model file not found: {path}")
        
        checkpoint = torch.load(path, map_location=self.device)
        
        self.src_vocab = checkpoint['src_vocab']
        self.tgt_vocab = checkpoint['tgt_vocab']
        
        self.model = Seq2SeqTranslator(
            src_vocab_size=self.src_vocab.n_words,
            tgt_vocab_size=self.tgt_vocab.n_words,
            embed_size=256,
            hidden_size=512,
            num_layers=2,
            dropout=0.3
        ).to(self.device)
        
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.model.eval()
        
        print(f"Model loaded from {path}")


if __name__ == '__main__':
    # Training script
    translator = PangasinanTranslator()
    
    print("Starting training...")
    translator.train('midterm_dictionary.json', epochs=30, batch_size=32)
    
    # Test translations
    print("\n" + "="*60)
    print("Testing translations:")
    print("="*60)
    
    test_words = [
        "agew",
        "aso", 
        "bahay",
        "maong",
        "kaaro"
    ]
    
    for word in test_words:
        translation = translator.translate(word)
        print(f"{word:15} → {translation}")
