"""
Prediction script for CryptoGuardLite
"""
import torch
import sys
from pathlib import Path
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from models import BaselineCNN, HybridModel
from feature_extraction import TrafficFeatureExtractor
from utils import config, default_logger


def predict(data_path: str, model_type: str = 'hybrid'):
    """
    Make prediction on data
    
    Args:
        data_path: Path to data file (PCAP or features)
        model_type: Type of model to use
    """
    default_logger.info(f"Making prediction with {model_type} model...")
    
    # Initialize feature extractor
    feature_extractor = TrafficFeatureExtractor(
        max_packet_length=config.get('feature_extraction.max_packet_length', 1500),
        sequence_length=config.get('feature_extraction.sequence_length', 100)
    )
    
    # Load model
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model_path = Path('data/models/best_model.pth')
    
    num_classes = len(config.get('attack_types', []))
    
    if model_type == 'baseline':
        model = BaselineCNN(input_dim=100, num_classes=num_classes)
    else:
        model = HybridModel(input_dim=100, feature_dim=5, num_classes=num_classes)
    
    if model_path.exists():
        checkpoint = torch.load(model_path, map_location=device)
        model.load_state_dict(checkpoint['model_state_dict'])
        model.to(device)
        model.eval()
        default_logger.info("Model loaded successfully")
    else:
        default_logger.error(f"Model not found at {model_path}")
        return
    
    # Extract features from PCAP
    if data_path.endswith(('.pcap', '.pcapng')):
        default_logger.info(f"Extracting features from {data_path}")
        flow_features, stat_features = feature_extractor.process_pcap(data_path)
        features = torch.FloatTensor(flow_features).unsqueeze(0).to(device)
    else:
        default_logger.error("Unsupported file format. Please provide a PCAP file.")
        return
    
    # Make prediction
    with torch.no_grad():
        output = model(features)
        probabilities = torch.softmax(output, dim=1)
        predicted_class = torch.argmax(probabilities, dim=1).item()
        confidence = probabilities[0, predicted_class].item()
    
    # Get attack type
    attack_types = config.get('attack_types', [])
    predicted_attack = attack_types[predicted_class]
    
    default_logger.info(f"\nPrediction Results:")
    default_logger.info(f"  Predicted Attack: {predicted_attack}")
    default_logger.info(f"  Confidence: {confidence:.4f}")
    default_logger.info(f"\nAll Probabilities:")
    for i, attack_type in enumerate(attack_types):
        prob = probabilities[0, i].item()
        default_logger.info(f"  {attack_type}: {prob:.4f}")
    
    return predicted_attack, confidence


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Make predictions with CryptoGuardLite")
    parser.add_argument('data', type=str, help='Path to PCAP file')
    parser.add_argument('--model', type=str, default='hybrid', choices=['baseline', 'hybrid'])
    
    args = parser.parse_args()
    
    predict(args.data, args.model)
