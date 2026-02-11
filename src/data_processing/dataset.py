"""
Dataset loader for CryptoGuardLite
"""
import os
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Tuple, List, Dict, Any
from torch.utils.data import Dataset, DataLoader
import torch


class TrafficDataset(Dataset):
    """PyTorch Dataset for network traffic data"""
    
    def __init__(self, features: np.ndarray, labels: np.ndarray, transform=None):
        """
        Initialize dataset
        
        Args:
            features: Feature array
            labels: Label array
            transform: Optional transform to apply to features
        """
        self.features = torch.FloatTensor(features)
        self.labels = torch.LongTensor(labels)
        self.transform = transform
    
    def __len__(self) -> int:
        return len(self.features)
    
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        feature = self.features[idx]
        label = self.labels[idx]
        
        if self.transform:
            feature = self.transform(feature)
        
        return feature, label


class DataProcessor:
    """Process and prepare data for training"""
    
    def __init__(self, data_dir: str = "data"):
        """
        Initialize data processor
        
        Args:
            data_dir: Base directory for data
        """
        self.data_dir = Path(data_dir)
        self.raw_dir = self.data_dir / "raw"
        self.processed_dir = self.data_dir / "processed"
        
        # Create directories if they don't exist
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
    
    def load_csv_data(self, csv_file: str) -> pd.DataFrame:
        """
        Load data from CSV file
        
        Args:
            csv_file: Path to CSV file
            
        Returns:
            DataFrame with loaded data
        """
        return pd.read_csv(csv_file)
    
    def preprocess_data(
        self, 
        data: pd.DataFrame, 
        feature_columns: List[str], 
        label_column: str
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Preprocess data by separating features and labels
        
        Args:
            data: Input DataFrame
            feature_columns: List of feature column names
            label_column: Label column name
            
        Returns:
            Tuple of (features, labels)
        """
        features = data[feature_columns].values
        labels = data[label_column].values
        
        return features, labels
    
    def normalize_features(self, features: np.ndarray) -> np.ndarray:
        """
        Normalize features to [0, 1] range
        
        Args:
            features: Input features
            
        Returns:
            Normalized features
        """
        min_vals = features.min(axis=0)
        max_vals = features.max(axis=0)
        
        # Avoid division by zero
        range_vals = max_vals - min_vals
        range_vals[range_vals == 0] = 1
        
        normalized = (features - min_vals) / range_vals
        return normalized
    
    def train_test_split(
        self, 
        features: np.ndarray, 
        labels: np.ndarray, 
        test_size: float = 0.2,
        random_state: int = 42
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Split data into train and test sets
        
        Args:
            features: Feature array
            labels: Label array
            test_size: Proportion of test set
            random_state: Random seed
            
        Returns:
            Tuple of (X_train, X_test, y_train, y_test)
        """
        from sklearn.model_selection import train_test_split
        
        return train_test_split(
            features, 
            labels, 
            test_size=test_size, 
            random_state=random_state,
            stratify=labels
        )
    
    def create_dataloader(
        self, 
        features: np.ndarray, 
        labels: np.ndarray, 
        batch_size: int = 32, 
        shuffle: bool = True
    ) -> DataLoader:
        """
        Create PyTorch DataLoader
        
        Args:
            features: Feature array
            labels: Label array
            batch_size: Batch size
            shuffle: Whether to shuffle data
            
        Returns:
            DataLoader object
        """
        dataset = TrafficDataset(features, labels)
        dataloader = DataLoader(
            dataset, 
            batch_size=batch_size, 
            shuffle=shuffle,
            num_workers=0  # Set to 0 for compatibility
        )
        
        return dataloader
    
    def save_processed_data(
        self, 
        features: np.ndarray, 
        labels: np.ndarray, 
        filename: str
    ):
        """
        Save processed data to file
        
        Args:
            features: Feature array
            labels: Label array
            filename: Output filename
        """
        output_path = self.processed_dir / filename
        np.savez_compressed(
            output_path,
            features=features,
            labels=labels
        )
    
    def load_processed_data(self, filename: str) -> Tuple[np.ndarray, np.ndarray]:
        """
        Load processed data from file
        
        Args:
            filename: Input filename
            
        Returns:
            Tuple of (features, labels)
        """
        input_path = self.processed_dir / filename
        data = np.load(input_path)
        
        return data['features'], data['labels']
