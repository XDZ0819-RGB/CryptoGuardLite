"""
FastAPI backend for CryptoGuardLite
"""
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import torch
import numpy as np
from pathlib import Path
import tempfile
import os

# Import project modules
import sys
sys.path.append(str(Path(__file__).parent.parent))

from models import BaselineCNN, HybridModel
from feature_extraction import TrafficFeatureExtractor
from utils import config, default_logger

# Initialize FastAPI app
app = FastAPI(
    title="CryptoGuardLite API",
    description="Encrypted Traffic Intrusion Detection System",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.get("api.cors_origins", ["*"]),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for model and feature extractor
model = None
feature_extractor = None
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Attack type labels
ATTACK_TYPES = config.get("attack_types", [
    "Normal", "DDoS", "C2", "Mining", "Port Scan",
    "Brute Force", "SQL Injection", "XSS", "Malware", "Exfiltration"
])


class PredictionRequest(BaseModel):
    """Request model for prediction"""
    features: List[List[float]]


class PredictionResponse(BaseModel):
    """Response model for prediction"""
    prediction: str
    confidence: float
    probabilities: Dict[str, float]


class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str
    model_loaded: bool
    device: str


@app.on_event("startup")
async def startup_event():
    """Initialize model and feature extractor on startup"""
    global model, feature_extractor
    
    default_logger.info("Starting CryptoGuardLite API...")
    
    # Initialize feature extractor
    feature_extractor = TrafficFeatureExtractor(
        max_packet_length=config.get("feature_extraction.max_packet_length", 1500),
        sequence_length=config.get("feature_extraction.sequence_length", 100)
    )
    
    # Load model (try to load pre-trained model if exists)
    model_path = Path("data/models/best_model.pth")
    
    if model_path.exists():
        try:
            # Initialize model architecture
            model = HybridModel(
                input_dim=config.get("model.hybrid.input_dim", 100),
                num_classes=len(ATTACK_TYPES)
            )
            
            # Load weights
            checkpoint = torch.load(model_path, map_location=device)
            model.load_state_dict(checkpoint['model_state_dict'])
            model.to(device)
            model.eval()
            
            default_logger.info(f"Model loaded successfully from {model_path}")
        except Exception as e:
            default_logger.error(f"Failed to load model: {e}")
            model = None
    else:
        default_logger.warning("No pre-trained model found. API will run in limited mode.")
        model = None


@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - health check"""
    return {
        "status": "running",
        "model_loaded": model is not None,
        "device": str(device)
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "device": str(device)
    }


@app.post("/predict/features", response_model=PredictionResponse)
async def predict_from_features(request: PredictionRequest):
    """
    Make prediction from extracted features
    
    Args:
        request: PredictionRequest with features
        
    Returns:
        PredictionResponse with prediction results
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Convert features to tensor
        features = torch.FloatTensor(request.features).unsqueeze(0).to(device)
        
        # Make prediction
        with torch.no_grad():
            output = model(features)
            probabilities = torch.softmax(output, dim=1)
            predicted_class = torch.argmax(probabilities, dim=1).item()
            confidence = probabilities[0, predicted_class].item()
        
        # Prepare response
        prob_dict = {
            ATTACK_TYPES[i]: float(probabilities[0, i])
            for i in range(len(ATTACK_TYPES))
        }
        
        return {
            "prediction": ATTACK_TYPES[predicted_class],
            "confidence": confidence,
            "probabilities": prob_dict
        }
    
    except Exception as e:
        default_logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict/pcap")
async def predict_from_pcap(file: UploadFile = File(...)):
    """
    Make prediction from PCAP file
    
    Args:
        file: PCAP file upload
        
    Returns:
        Prediction results
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    if not file.filename.endswith(('.pcap', '.pcapng')):
        raise HTTPException(status_code=400, detail="File must be a PCAP file")
    
    try:
        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pcap') as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_path = temp_file.name
        
        # Extract features
        flow_features, stat_features = feature_extractor.process_pcap(temp_path)
        
        # Convert to tensor
        features = torch.FloatTensor(flow_features).unsqueeze(0).to(device)
        
        # Make prediction
        with torch.no_grad():
            output = model(features)
            probabilities = torch.softmax(output, dim=1)
            predicted_class = torch.argmax(probabilities, dim=1).item()
            confidence = probabilities[0, predicted_class].item()
        
        # Clean up temporary file
        os.unlink(temp_path)
        
        # Prepare response
        prob_dict = {
            ATTACK_TYPES[i]: float(probabilities[0, i])
            for i in range(len(ATTACK_TYPES))
        }
        
        return {
            "prediction": ATTACK_TYPES[predicted_class],
            "confidence": confidence,
            "probabilities": prob_dict,
            "statistics": {
                "packet_count": len(flow_features),
                "mean_packet_length": float(stat_features[0]),
                "std_packet_length": float(stat_features[1])
            }
        }
    
    except Exception as e:
        default_logger.error(f"PCAP prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/model/info")
async def model_info():
    """Get model information"""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    return {
        "model_type": model.__class__.__name__,
        "num_classes": len(ATTACK_TYPES),
        "attack_types": ATTACK_TYPES,
        "device": str(device)
    }


if __name__ == "__main__":
    import uvicorn
    
    host = config.get("api.host", "0.0.0.0")
    port = config.get("api.port", 8000)
    
    uvicorn.run(app, host=host, port=port)
