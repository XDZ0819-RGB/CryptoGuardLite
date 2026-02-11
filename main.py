"""
Main entry point for CryptoGuardLite
"""
import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from utils import config, setup_logger


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="CryptoGuardLite - Encrypted Traffic Intrusion Detection System")
    parser.add_argument(
        'command',
        choices=['train', 'predict', 'api', 'preprocess'],
        help='Command to execute'
    )
    parser.add_argument('--model', type=str, default='hybrid', choices=['baseline', 'hybrid'],
                       help='Model type to use')
    parser.add_argument('--config', type=str, help='Path to config file')
    parser.add_argument('--data', type=str, help='Path to data file')
    parser.add_argument('--output', type=str, help='Output path')
    parser.add_argument('--epochs', type=int, default=50, help='Number of training epochs')
    parser.add_argument('--batch-size', type=int, default=32, help='Batch size')
    
    args = parser.parse_args()
    
    # Setup logger
    logger = setup_logger()
    
    logger.info(f"Starting CryptoGuardLite - Command: {args.command}")
    
    if args.command == 'train':
        from scripts.train import train_model
        logger.info("Training model...")
        train_model(
            model_type=args.model,
            epochs=args.epochs,
            batch_size=args.batch_size
        )
    
    elif args.command == 'predict':
        from scripts.predict import predict
        if not args.data:
            logger.error("--data argument required for predict command")
            sys.exit(1)
        logger.info(f"Making prediction on {args.data}")
        predict(args.data, args.model)
    
    elif args.command == 'api':
        logger.info("Starting API server...")
        import uvicorn
        from api.main import app
        
        host = config.get("api.host", "0.0.0.0")
        port = config.get("api.port", 8000)
        uvicorn.run(app, host=host, port=port)
    
    elif args.command == 'preprocess':
        from scripts.preprocess import preprocess_data
        if not args.data:
            logger.error("--data argument required for preprocess command")
            sys.exit(1)
        logger.info(f"Preprocessing data from {args.data}")
        preprocess_data(args.data, args.output)
    
    logger.info("Task completed successfully")


if __name__ == "__main__":
    main()
