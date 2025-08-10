# services/training.py
from models.model_registry import load_model, DEFAULT_MODEL
from services.data_provider import DataProvider
from common.logger import logger

provider = DataProvider()

def train_and_save(model_name: str = DEFAULT_MODEL):
    model = load_model(model_name)
    X, y = provider.get_training_data()
    model.train(X, y)
    model.save()
    logger.info("✅ Training complete")
