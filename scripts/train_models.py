import os
import sys
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.models.anomaly_detector import SubstationAutoencoder
from src.models.fault_classifier import FaultClassifier

def main():
    print("[INFO] Loading telemetry data...")
    df = pd.read_csv('data/substation_telemetry.csv')
    
    # Feature Engineering
    features = ['voltage_kv', 'current_a', 'frequency_hz', 'transformer_temp_c', 'oil_temp_c', 'power_factor']
    X = df[features].values
    y = df['label'].values
    
    # Split and Scale
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    print("[INFO] Training Deep Learning Autoencoder on NORMAL data only...")
    # Isolate normal data for unsupervised training
    X_train_normal = X_train_scaled[y_train == 0]
    
    autoencoder = SubstationAutoencoder(input_dim=len(features))
    autoencoder.compile(optimizer='adam', loss='mse')
    autoencoder.fit(X_train_normal, X_train_normal, epochs=10, batch_size=64, validation_split=0.1, verbose=1)
    
    print("\n[INFO] Training XGBoost Fault Classifier...")
    classifier = FaultClassifier(use_xgb=True)
    classifier.train(X_train_scaled, y_train)
    
    print("\n[EVALUATION] Fault Classification Report:")
    print(classifier.evaluate(X_test_scaled, y_test))
    
    print("[SUCCESS] Models trained successfully.")

if __name__ == '__main__':
    main()