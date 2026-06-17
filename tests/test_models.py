import pytest
import numpy as np
from src.models.anomaly_detector import SubstationAutoencoder
from src.models.fault_classifier import FaultClassifier

def test_autoencoder_architecture():
    model = SubstationAutoencoder(input_dim=6)
    dummy_data = np.random.rand(10, 6)
    output = model(dummy_data)
    assert output.shape == (10, 6), "Autoencoder must reconstruct exact input dimensions"

def test_xgboost_classifier():
    clf = FaultClassifier(use_xgb=True)
    X = np.random.rand(20, 6)
    y = np.random.randint(0, 4, 20)
    clf.train(X, y)
    preds = clf.predict(X)
    assert len(preds) == 20, "Classifier must return predictions for all inputs"