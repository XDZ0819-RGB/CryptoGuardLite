"""
Traffic Feature Extractor for encrypted traffic analysis
"""
import numpy as np
from typing import List, Dict, Any, Tuple
from scapy.all import rdpcap, Packet, IP, TCP, UDP
from pathlib import Path


class TrafficFeatureExtractor:
    """Extract features from network traffic packets"""
    
    def __init__(self, max_packet_length: int = 1500, sequence_length: int = 100):
        """
        Initialize feature extractor
        
        Args:
            max_packet_length: Maximum packet length for normalization
            sequence_length: Number of packets in a sequence
        """
        self.max_packet_length = max_packet_length
        self.sequence_length = sequence_length
    
    def extract_packet_features(self, packet: Packet) -> Dict[str, Any]:
        """
        Extract features from a single packet
        
        Args:
            packet: Scapy packet object
            
        Returns:
            Dictionary of packet features
        """
        features = {
            'packet_length': len(packet),
            'protocol': self._get_protocol(packet),
            'tcp_flags': self._get_tcp_flags(packet),
            'payload_size': len(packet.payload) if hasattr(packet, 'payload') else 0,
            'header_length': self._get_header_length(packet),
        }
        
        return features
    
    def extract_flow_features(self, packets: List[Packet]) -> np.ndarray:
        """
        Extract features from a flow of packets
        
        Args:
            packets: List of packets in a flow
            
        Returns:
            Numpy array of flow features
        """
        # Limit to sequence_length packets
        packets = packets[:self.sequence_length]
        
        # Extract features for each packet
        packet_features = []
        inter_arrival_times = []
        last_time = None
        
        for pkt in packets:
            # Packet length
            pkt_len = len(pkt) / self.max_packet_length  # Normalize
            
            # Inter-arrival time
            if last_time is not None and hasattr(pkt, 'time'):
                iat = pkt.time - last_time
                inter_arrival_times.append(iat)
            else:
                inter_arrival_times.append(0)
            
            if hasattr(pkt, 'time'):
                last_time = pkt.time
            
            # Protocol
            protocol = self._get_protocol_num(pkt)
            
            # Payload size
            payload_size = len(pkt.payload) if hasattr(pkt, 'payload') else 0
            payload_size = payload_size / self.max_packet_length  # Normalize
            
            # Direction (simplified: based on port numbers)
            direction = self._get_direction(pkt)
            
            packet_features.append([pkt_len, protocol, payload_size, direction])
        
        # Pad if necessary
        while len(packet_features) < self.sequence_length:
            packet_features.append([0, 0, 0, 0])
            inter_arrival_times.append(0)
        
        # Combine features
        packet_features = np.array(packet_features)
        inter_arrival_times = np.array(inter_arrival_times).reshape(-1, 1)
        
        # Add inter-arrival times as a feature
        flow_features = np.hstack([packet_features, inter_arrival_times])
        
        return flow_features
    
    def extract_statistical_features(self, packets: List[Packet]) -> np.ndarray:
        """
        Extract statistical features from a flow
        
        Args:
            packets: List of packets in a flow
            
        Returns:
            Numpy array of statistical features
        """
        if len(packets) == 0:
            return np.zeros(8)
        
        packet_lengths = [len(pkt) for pkt in packets]
        
        features = [
            np.mean(packet_lengths),
            np.std(packet_lengths),
            np.min(packet_lengths),
            np.max(packet_lengths),
            np.percentile(packet_lengths, 25),
            np.percentile(packet_lengths, 75),
            len(packets),
            sum(packet_lengths)
        ]
        
        return np.array(features)
    
    def _get_protocol(self, packet: Packet) -> str:
        """Get protocol name"""
        if TCP in packet:
            return 'TCP'
        elif UDP in packet:
            return 'UDP'
        elif IP in packet:
            return 'IP'
        else:
            return 'Other'
    
    def _get_protocol_num(self, packet: Packet) -> int:
        """Get protocol number for encoding"""
        protocol_map = {'TCP': 1, 'UDP': 2, 'IP': 3, 'Other': 0}
        return protocol_map.get(self._get_protocol(packet), 0)
    
    def _get_tcp_flags(self, packet: Packet) -> int:
        """Get TCP flags"""
        if TCP in packet:
            return int(packet[TCP].flags)
        return 0
    
    def _get_header_length(self, packet: Packet) -> int:
        """Get header length"""
        if IP in packet:
            return packet[IP].ihl * 4
        return 0
    
    def _get_direction(self, packet: Packet) -> int:
        """
        Get packet direction (simplified)
        0: Unknown, 1: Forward, -1: Backward
        """
        if TCP in packet:
            if packet[TCP].sport < packet[TCP].dport:
                return 1
            else:
                return -1
        elif UDP in packet:
            if packet[UDP].sport < packet[UDP].dport:
                return 1
            else:
                return -1
        return 0
    
    def load_pcap(self, pcap_file: str) -> List[Packet]:
        """
        Load packets from PCAP file
        
        Args:
            pcap_file: Path to PCAP file
            
        Returns:
            List of packets
        """
        return rdpcap(pcap_file)
    
    def process_pcap(self, pcap_file: str) -> Tuple[np.ndarray, np.ndarray]:
        """
        Process PCAP file and extract features
        
        Args:
            pcap_file: Path to PCAP file
            
        Returns:
            Tuple of (flow_features, statistical_features)
        """
        packets = self.load_pcap(pcap_file)
        flow_features = self.extract_flow_features(packets)
        stat_features = self.extract_statistical_features(packets)
        
        return flow_features, stat_features
