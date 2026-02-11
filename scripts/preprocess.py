"""
Data preprocessing script for CryptoGuardLite
"""
import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from feature_extraction import TrafficFeatureExtractor
from data_processing import DataProcessor
from utils import config, default_logger


def preprocess_data(data_path: str, output_path: str = None):
    """
    Preprocess raw data
    
    Args:
        data_path: Path to raw data directory or file
        output_path: Output path for processed data
    """
    default_logger.info(f"Preprocessing data from {data_path}")
    
    # Initialize processors
    feature_extractor = TrafficFeatureExtractor(
        max_packet_length=config.get('feature_extraction.max_packet_length', 1500),
        sequence_length=config.get('feature_extraction.sequence_length', 100)
    )
    data_processor = DataProcessor()
    
    # Check if input is directory or file
    data_path = Path(data_path)
    
    if data_path.is_dir():
        # Process all PCAP files in directory
        pcap_files = list(data_path.glob('*.pcap')) + list(data_path.glob('*.pcapng'))
        default_logger.info(f"Found {len(pcap_files)} PCAP files")
        
        all_features = []
        all_labels = []
        
        for pcap_file in pcap_files:
            try:
                default_logger.info(f"Processing {pcap_file.name}...")
                flow_features, stat_features = feature_extractor.process_pcap(str(pcap_file))
                
                # Assign label based on filename (simple heuristic)
                # In production, use proper labeling
                label = 0  # Default to normal
                if 'attack' in pcap_file.name.lower():
                    label = 1
                
                all_features.append(flow_features)
                all_labels.append(label)
                
            except Exception as e:
                default_logger.error(f"Error processing {pcap_file.name}: {e}")
                continue
        
        # Stack all features
        features = np.array(all_features)
        labels = np.array(all_labels)
        
    elif data_path.is_file() and data_path.suffix == '.csv':
        # Process CSV file
        default_logger.info("Processing CSV file...")
        df = data_processor.load_csv_data(str(data_path))
        
        # Assume CSV has feature columns and a label column
        # Adjust column names based on your dataset
        feature_columns = [col for col in df.columns if col != 'label']
        features = df[feature_columns].values
        labels = df['label'].values if 'label' in df.columns else np.zeros(len(df))
        
    else:
        default_logger.error("Invalid input path. Must be a directory or CSV file.")
        return
    
    default_logger.info(f"Processed {len(features)} samples")
    
    # Normalize features
    default_logger.info("Normalizing features...")
    features = data_processor.normalize_features(features)
    
    # Save processed data
    if output_path is None:
        output_path = 'processed_data.npz'
    
    data_processor.save_processed_data(features, labels, output_path)
    default_logger.info(f"Saved processed data to {output_path}")
    
    return features, labels


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Preprocess data for CryptoGuardLite")
    parser.add_argument('data', type=str, help='Path to raw data directory or CSV file')
    parser.add_argument('--output', type=str, help='Output file path')
    
    args = parser.parse_args()
    
    preprocess_data(args.data, args.output)
