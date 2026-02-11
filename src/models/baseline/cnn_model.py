"""
Baseline CNN model for traffic classification
"""
import torch
import torch.nn as nn
import torch.nn.functional as F


class BaselineCNN(nn.Module):
    """Baseline CNN model for encrypted traffic classification"""
    
    def __init__(
        self, 
        input_dim: int = 100, 
        num_classes: int = 10,
        hidden_dims: list = None
    ):
        """
        Initialize CNN model
        
        Args:
            input_dim: Input dimension (sequence length)
            num_classes: Number of output classes
            hidden_dims: List of hidden dimensions for CNN layers
        """
        super(BaselineCNN, self).__init__()
        
        if hidden_dims is None:
            hidden_dims = [64, 128, 256]
        
        self.input_dim = input_dim
        self.num_classes = num_classes
        
        # Convolutional layers
        self.conv1 = nn.Conv1d(in_channels=5, out_channels=hidden_dims[0], kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm1d(hidden_dims[0])
        self.pool1 = nn.MaxPool1d(kernel_size=2)
        
        self.conv2 = nn.Conv1d(in_channels=hidden_dims[0], out_channels=hidden_dims[1], kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm1d(hidden_dims[1])
        self.pool2 = nn.MaxPool1d(kernel_size=2)
        
        self.conv3 = nn.Conv1d(in_channels=hidden_dims[1], out_channels=hidden_dims[2], kernel_size=3, padding=1)
        self.bn3 = nn.BatchNorm1d(hidden_dims[2])
        self.pool3 = nn.MaxPool1d(kernel_size=2)
        
        # Calculate flattened size
        self.flatten_size = hidden_dims[2] * (input_dim // 8)
        
        # Fully connected layers
        self.fc1 = nn.Linear(self.flatten_size, 512)
        self.dropout = nn.Dropout(0.5)
        self.fc2 = nn.Linear(512, num_classes)
    
    def forward(self, x):
        """
        Forward pass
        
        Args:
            x: Input tensor of shape (batch_size, sequence_length, feature_dim)
            
        Returns:
            Output logits
        """
        # Reshape for Conv1d: (batch, feature_dim, sequence_length)
        x = x.permute(0, 2, 1)
        
        # Convolutional layers with ReLU and pooling
        x = self.pool1(F.relu(self.bn1(self.conv1(x))))
        x = self.pool2(F.relu(self.bn2(self.conv2(x))))
        x = self.pool3(F.relu(self.bn3(self.conv3(x))))
        
        # Flatten
        x = x.view(x.size(0), -1)
        
        # Fully connected layers
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)
        
        return x
    
    def predict(self, x):
        """
        Make predictions
        
        Args:
            x: Input tensor
            
        Returns:
            Predicted class indices
        """
        with torch.no_grad():
            logits = self.forward(x)
            predictions = torch.argmax(logits, dim=1)
        
        return predictions
