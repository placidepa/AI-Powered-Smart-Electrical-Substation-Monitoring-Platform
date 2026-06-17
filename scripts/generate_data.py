import os
import sys

# Ensure Python can find the src directory when running from the root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data.simulator import SubstationDataSimulator

def main():
    print("[INFO] Initializing Substation Data Simulator...")
    
    # Generate 90 days of 5-minute interval data (~25,000 rows)
    sim = SubstationDataSimulator(start_date='2026-01-01', days=90, freq='5T')
    
    print("[INFO] Simulating baseline diurnal load and thermal properties...")
    print("[INFO] Injecting synthetic fault signatures (Overloads, Short Circuits, Cooling Failures)...")
    df = sim.generate_dataset()
    
    # Save to the data directory
    os.makedirs('data', exist_ok=True)
    out_path = 'data/substation_telemetry.csv'
    df.to_csv(out_path, index=False)
    
    print(f"[SUCCESS] Synthetic dataset generated successfully at {out_path}")
    print(f"[STATS] Total Records: {len(df)}")
    print(f"[STATS] Class Distribution:\n{df['label'].value_counts().to_string()}")

if __name__ == '__main__':
    main()