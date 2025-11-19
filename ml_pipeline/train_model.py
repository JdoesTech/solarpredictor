"""
Standalone script to train solar energy prediction model
Can be run independently or called from Django
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from ml_models.trainer import ModelTrainer

if __name__ == '__main__':
    trainer = ModelTrainer()
    result = trainer.train_model(model_type='regression')
    print(f"Training completed!")
    print(f"Model version: {result['version_name']}")
    print(f"R² Score: {result['r2_score']:.4f}")
    print(f"MSE: {result['mse']:.4f}")
    print(f"MAE: {result['mae']:.4f}")

