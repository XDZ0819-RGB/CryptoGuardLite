"""
Hybrid CNN-BiLSTM-Transformer model for traffic classification
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
import math


class PositionalEncoding(nn.Module):
    """Positional encoding for transformer"""
    
    def __init__(self, d_model: int, max_len: int = 5000):
        super(PositionalEncoding, self).__init__()
        
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
        
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0)
        
        self.register_buffer('pe', pe)
    
    def forward(self, x):
        return x + self.pe[:, :x.size(1), :]


class HybridModel(nn.Module):
    """Hybrid CNN-BiLSTM-Transformer model for encrypted traffic classification"""
    
    def __init__(
        self,
        input_dim: int = 100,
        feature_dim: int = 5,
        num_classes: int = 10,
        cnn_filters: list = None,
        lstm_hidden_size: int = 128,
        transformer_heads: int = 8,
        transformer_layers: int = 4,
        dropout: float = 0.3
    ):
        """
        Initialize Hybrid model
        
        Args:
            input_dim: Sequence length
            feature_dim: Feature dimension per time step
            num_classes: Number of output classes
            cnn_filters: List of CNN filter sizes
            lstm_hidden_size: LSTM hidden size
            transformer_heads: Number of attention heads
            transformer_layers: Number of transformer layers
            dropout: Dropout rate
        """
        super(HybridModel, self).__init__()
        
        if cnn_filters is None:
            cnn_filters = [64, 128, 256]
        
        self.input_dim = input_dim
        self.feature_dim = feature_dim
        self.num_classes = num_classes
        
        # CNN layers for local feature extraction
        self.conv1 = nn.Conv1d(feature_dim, cnn_filters[0], kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm1d(cnn_filters[0])
        
        self.conv2 = nn.Conv1d(cnn_filters[0], cnn_filters[1], kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm1d(cnn_filters[1])
        
        self.conv3 = nn.Conv1d(cnn_filters[1], cnn_filters[2], kernel_size=3, padding=1)
        self.bn3 = nn.BatchNorm1d(cnn_filters[2])
        
        self.pool = nn.MaxPool1d(kernel_size=2)
        self.dropout1 = nn.Dropout(dropout)
        
        # BiLSTM layers for temporal dependencies
        self.lstm = nn.LSTM(
            input_size=cnn_filters[2],
            hidden_size=lstm_hidden_size,
            num_layers=2,
            batch_first=True,
            bidirectional=True,
            dropout=dropout
        )
        
        # Transformer layers for long-range dependencies
        self.d_model = lstm_hidden_size * 2  # BiLSTM output
        self.pos_encoder = PositionalEncoding(self.d_model, max_len=input_dim)
        
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=self.d_model,
            nhead=transformer_heads,
            dim_feedforward=self.d_model * 4,
            dropout=dropout,
            batch_first=True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=transformer_layers)
        
        # Attention pooling
        self.attention_weights = nn.Linear(self.d_model, 1)
        
        # Fully connected layers
        self.fc1 = nn.Linear(self.d_model, 512)
        self.dropout2 = nn.Dropout(dropout)
        self.fc2 = nn.Linear(512, 256)
        self.dropout3 = nn.Dropout(dropout)
        self.fc3 = nn.Linear(256, num_classes)
    
    def forward(self, x):
        """
        Forward pass
        
        Args:
            x: Input tensor of shape (batch_size, sequence_length, feature_dim)
            
        Returns:
            Output logits
        """
        batch_size = x.size(0)
        
        # CNN feature extraction
        # Reshape for Conv1d: (batch, feature_dim, sequence_length)
        x = x.permute(0, 2, 1)
        
        x = self.pool(F.relu(self.bn1(self.conv1(x))))
        x = self.pool(F.relu(self.bn2(self.conv2(x))))
        x = F.relu(self.bn3(self.conv3(x)))
        x = self.dropout1(x)
        
        # Reshape back for LSTM: (batch, sequence_length, feature_dim)
        x = x.permute(0, 2, 1)
        
        # BiLSTM temporal modeling
        x, _ = self.lstm(x)
        
        # Transformer for long-range dependencies
        x = self.pos_encoder(x)
        x = self.transformer(x)
        
        # Attention pooling
        attention_scores = torch.softmax(self.attention_weights(x), dim=1)
        x = torch.sum(x * attention_scores, dim=1)
        
        # Fully connected layers
        x = F.relu(self.fc1(x))
        x = self.dropout2(x)
        x = F.relu(self.fc2(x))
        x = self.dropout3(x)
        x = self.fc3(x)
        
        return x
    
    def predict(self, x):
        """
        Make predictions
        
        Args:
            x: Input tensor
            
        Returns:
            Predicted class indices and probabilities
        """
        with torch.no_grad():
            logits = self.forward(x)
            probabilities = F.softmax(logits, dim=1)
            predictions = torch.argmax(probabilities, dim=1)
        
        return predictions, probabilities
