"""
Test models
"""
import pytest
import torch
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from models import BaselineCNN, HybridModel


def test_baseline_cnn_init():
    """Test BaselineCNN initialization"""
    model = BaselineCNN(input_dim=100, num_classes=10)
    assert model is not None
    assert model.num_classes == 10


def test_baseline_cnn_forward():
    """Test BaselineCNN forward pass"""
    model = BaselineCNN(input_dim=100, num_classes=10)
    
    # Create dummy input: (batch_size, sequence_length, feature_dim)
    x = torch.randn(2, 100, 5)
    
    # Forward pass
    output = model(x)
    
    # Check output shape
    assert output.shape == (2, 10)  # (batch_size, num_classes)


def test_hybrid_model_init():
    """Test HybridModel initialization"""
    model = HybridModel(input_dim=100, num_classes=10)
    assert model is not None
    assert model.num_classes == 10


def test_hybrid_model_forward():
    """Test HybridModel forward pass"""
    model = HybridModel(input_dim=100, feature_dim=5, num_classes=10)
    
    # Create dummy input: (batch_size, sequence_length, feature_dim)
    x = torch.randn(2, 100, 5)
    
    # Forward pass
    output = model(x)
    
    # Check output shape
    assert output.shape == (2, 10)  # (batch_size, num_classes)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
