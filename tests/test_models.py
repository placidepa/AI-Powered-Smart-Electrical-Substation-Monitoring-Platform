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
def test_health_scorer_normal():
    from src.models.health_scorer import AssetHealthAssessor
    scorer = AssetHealthAssessor()
    health = scorer.calculate_health_score(temp_c=50, current_a=400)
    assert health == 100.0, "Equipment under rated specs should have 100 health"

def test_health_scorer_degradation():
    from src.models.health_scorer import AssetHealthAssessor
    scorer = AssetHealthAssessor()
    health = scorer.calculate_health_score(temp_c=90, current_a=700)
    assert health < 100.0, "Equipment operating above rated specs must degrade"

def test_rul_estimation():
    from src.models.health_scorer import AssetHealthAssessor
    scorer = AssetHealthAssessor()
    rul = scorer.estimate_rul(health_score=65.0, degradation_rate=0.1)
    assert rul == 350.0, "RUL should correctly calculate days remaining"
