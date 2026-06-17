# System Architecture Document

## Overview
This platform bridges the physical power grid with modern software infrastructure. Data from Substation IEDs (Intelligent Electronic Devices) is aggregated and passed to our containerized analytics engine.

## Machine Learning Pipeline
1. **Data Ingestion**: High-frequency parsing of telemetry simulating IEC 61850.
2. **Feature Engineering**: Computation of thermal gradients and electrical stresses.
3. **Anomaly Detection**: An Autoencoder deep neural network identifies unknown anomalies by tracking reconstruction loss (MSE > Threshold).
4. **Classification**: Known faults are routed to an XGBoost classifier for precise tagging (Overload, Short Circuit, Cooling Failure).

## Predictive Maintenance Methodology
We utilize an active degradation model based on IEEE C57.91 thermal guidelines. By tracking temperature excursions and applying time-series forecasting, we compute the Remaining Useful Life (RUL) of critical assets.

## Alerting & Webhook Routing
The Idempotent Gateway processes events and generates a SHA-256 fingerprint. This ensures that duplicate sensor bursts do not result in multiple identical alarms for the operators.