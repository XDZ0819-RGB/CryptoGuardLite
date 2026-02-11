"""
Test feature extraction module
"""
import pytest
import numpy as np
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from feature_extraction import TrafficFeatureExtractor


def test_feature_extractor_init():
    """Test feature extractor initialization"""
    extractor = TrafficFeatureExtractor(max_packet_length=1500, sequence_length=100)
    assert extractor.max_packet_length == 1500
    assert extractor.sequence_length == 100


def test_extract_flow_features():
    """Test flow feature extraction"""
    extractor = TrafficFeatureExtractor()
    
    # Create mock packets (empty list for now)
    packets = []
    
    features = extractor.extract_flow_features(packets)
    
    # Should return padded features
    assert features.shape == (100, 5)  # sequence_length x feature_dim


def test_extract_statistical_features():
    """Test statistical feature extraction"""
    extractor = TrafficFeatureExtractor()
    
    # Empty packets
    packets = []
    features = extractor.extract_statistical_features(packets)
    
    # Should return 8 statistical features, all zeros
    assert features.shape == (8,)
    assert np.all(features == 0)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
