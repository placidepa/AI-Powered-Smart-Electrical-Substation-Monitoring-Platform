import numpy as np
import pandas as pd

class SubstationDataSimulator:
    "`"`"
    Generates synthetic industrial telemetry data for electrical substations.
    Simulates real-world harmonics, thermal inertia, and transient anomalies.
    "`"`"
    def __init__(self, start_date='2026-01-01', days=30, freq='5T'):
        self.start_date = pd.to_datetime(start_date)
        # Calculate total periods based on frequency (e.g., '5T' = 5 minutes)
        minutes_per_day = 24 * 60
        freq_minutes = int(freq[:-1])
        self.periods = (days * minutes_per_day) // freq_minutes
        self.timestamps = pd.date_range(start=self.start_date, periods=self.periods, freq=freq)
        self.n_samples = len(self.timestamps)

    def generate_baseline(self) -> pd.DataFrame:
        "`"`"Generates baseline operational data with diurnal load cycles."`"`"
        # Time of day in hours (0.0 to 23.99)
        time_hours = np.array([t.hour + t.minute / 60 for t in self.timestamps])
        
        # Diurnal load profile: L(t) = Base + Amp * sin(pi * (t - 6) / 12) + Noise
        load_profile = 0.6 + 0.3 * np.sin(np.pi * (time_hours - 6) / 12) + np.random.normal(0, 0.02, self.n_samples)
        load_profile = np.clip(load_profile, 0.2, 1.0)
        
        # Electrical Parameters
        voltage_kv = 110 + np.random.normal(0, 0.5, self.n_samples) - (load_profile * 1.5)
        current_a = load_profile * 500
        frequency_hz = np.random.normal(50.0, 0.015, self.n_samples)
        power_factor = np.random.uniform(0.95, 0.99, self.n_samples)
        
        # Thermal Parameters (Approximating thermal inertia lag)
        transformer_temp_c = 40 + (load_profile * 35) + np.random.normal(0, 1.0, self.n_samples)
        oil_temp_c = transformer_temp_c - 10 + np.random.normal(0, 0.5, self.n_samples)
        
        df = pd.DataFrame({
            'timestamp': self.timestamps,
            'voltage_kv': np.round(voltage_kv, 2),
            'current_a': np.round(current_a, 2),
            'frequency_hz': np.round(frequency_hz, 3),
            'transformer_temp_c': np.round(transformer_temp_c, 1),
            'oil_temp_c': np.round(oil_temp_c, 1),
            'power_factor': np.round(power_factor, 3),
            'breaker_status': np.ones(self.n_samples, dtype=int),
            'label': 0  # 0 = Normal Operation
        })
        return df

    def inject_anomalies(self, df: pd.DataFrame, contamination=0.02) -> pd.DataFrame:
        "`"`"
        Injects specific fault signatures using vectorized operations.
        Labels: 1 (Overload), 2 (Short Circuit), 3 (Cooling Failure)
        "`"`"
        np.random.seed(42)
        n_anomalies = int(self.n_samples * contamination)
        
        # Select random indices for anomalies
        anomaly_indices = np.random.choice(df.index, n_anomalies, replace=False)
        
        # Distribute anomaly types evenly
        fault_types = np.random.choice([1, 2, 3], size=n_anomalies)
        
        for fault_type in [1, 2, 3]:
            mask = anomaly_indices[fault_types == fault_type]
            
            if fault_type == 1: # Overload (High current, rising temp)
                df.loc[mask, 'current_a'] *= np.random.uniform(1.3, 1.8, len(mask))
                df.loc[mask, 'transformer_temp_c'] += np.random.uniform(10, 20, len(mask))
                df.loc[mask, 'label'] = 1
                
            elif fault_type == 2: # Short Circuit (Voltage sag, extreme current, breaker trip)
                df.loc[mask, 'voltage_kv'] *= np.random.uniform(0.4, 0.7, len(mask))
                df.loc[mask, 'current_a'] *= np.random.uniform(3.0, 6.0, len(mask))
                df.loc[mask, 'breaker_status'] = 0
                df.loc[mask, 'label'] = 2
                
            elif fault_type == 3: # Cooling Failure (Normal electrical, severe thermal deviation)
                df.loc[mask, 'transformer_temp_c'] += np.random.uniform(25, 40, len(mask))
                df.loc[mask, 'oil_temp_c'] += np.random.uniform(20, 35, len(mask))
                df.loc[mask, 'label'] = 3
                
        return df

    def generate_dataset(self) -> pd.DataFrame:
        df = self.generate_baseline()
        df = self.inject_anomalies(df)
        return df