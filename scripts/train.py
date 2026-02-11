"""
Training script for CryptoGuardLite models
"""
import torch
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from models import BaselineCNN, HybridModel
from models.trainer import ModelTrainer
from data_processing import DataProcessor
from utils import config, default_logger
import numpy as np


def train_model(model_type: str = 'hybrid', epochs: int = 50, batch_size: int = 32):
    """
    Train a model
    
    Args:
        model_type: Type of model to train ('baseline' or 'hybrid')
        epochs: Number of training epochs
        batch_size: Batch size
    """
    default_logger.info(f"Training {model_type} model...")
    
    # Initialize data processor
    data_processor = DataProcessor()
    
    # Load or generate dummy data for demonstration
    # In production, replace this with actual data loading
    default_logger.info("Generating dummy training data...")
    
    # Generate dummy features and labels
    num_samples = 1000
    sequence_length = config.get('feature_extraction.sequence_length', 100)
    feature_dim = 5
    num_classes = len(config.get('attack_types', []))
    
    X = np.random.randn(num_samples, sequence_length, feature_dim)
    y = np.random.randint(0, num_classes, num_samples)
    
    # Split data
    X_train, X_test, y_train, y_test = data_processor.train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    default_logger.info(f"Training set size: {len(X_train)}")
    default_logger.info(f"Test set size: {len(X_test)}")
    
    # Create data loaders
    train_loader = data_processor.create_dataloader(
        X_train, y_train, batch_size=batch_size, shuffle=True
    )
    test_loader = data_processor.create_dataloader(
        X_test, y_test, batch_size=batch_size, shuffle=False
    )
    
    # Initialize model
    if model_type == 'baseline':
        model = BaselineCNN(
            input_dim=sequence_length,
            num_classes=num_classes
        )
    else:
        model = HybridModel(
            input_dim=sequence_length,
            feature_dim=feature_dim,
            num_classes=num_classes,
            cnn_filters=config.get('model.hybrid.cnn_filters', [64, 128, 256]),
            lstm_hidden_size=config.get('model.hybrid.lstm_hidden_size', 128),
            transformer_heads=config.get('model.hybrid.transformer_heads', 8),
            transformer_layers=config.get('model.hybrid.transformer_layers', 4),
            dropout=config.get('model.hybrid.dropout', 0.3)
        )
    
    default_logger.info(f"Model architecture:\n{model}")
    
    # Initialize trainer
    device = config.get('training.device', 'cuda')
    learning_rate = config.get('model.hybrid.learning_rate', 0.0001) if model_type == 'hybrid' else config.get('model.baseline.learning_rate', 0.001)
    
    trainer = ModelTrainer(
        model=model,
        device=device,
        learning_rate=learning_rate
    )
    
    # Train model
    default_logger.info("Starting training...")
    history = trainer.train(
        train_loader=train_loader,
        val_loader=test_loader,
        epochs=epochs,
        early_stopping_patience=config.get('training.early_stopping_patience', 10),
        save_best=config.get('training.save_best_model', True)
    )
    
    # Save final model
    trainer.save_model(f'{model_type}_final.pth')
    
    default_logger.info("Training completed!")
    default_logger.info(f"Final train accuracy: {history['train_accuracies'][-1]:.2f}%")
    default_logger.info(f"Final validation accuracy: {history['val_accuracies'][-1]:.2f}%")
    
    return history


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Train CryptoGuardLite model")
    parser.add_argument('--model', type=str, default='hybrid', choices=['baseline', 'hybrid'])
    parser.add_argument('--epochs', type=int, default=50)
    parser.add_argument('--batch-size', type=int, default=32)
    
    args = parser.parse_args()
    
    train_model(args.model, args.epochs, args.batch_size)
