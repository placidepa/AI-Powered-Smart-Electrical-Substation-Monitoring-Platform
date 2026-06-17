import os
import sys
import time

import numpy as np
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from dashboard.app import apply_fault_signature, infer_fault_label, make_reading
from src.utils.redis_store import push_reading, redis_configured


def main():
    if not redis_configured():
        print("[ERROR] Upstash Redis is not configured.")
        print("[HELP] Copy .env.example to .env and fill in your Upstash credentials.")
        raise SystemExit(1)

    print("[INFO] Publishing live simulated telemetry to Upstash Redis.")
    print("[INFO] Press CTRL+C to stop.")

    voltage_kv = 110.0
    current_a = 420.0
    transformer_temp_c = 62.0
    oil_temp_c = 52.0
    power_factor = 0.97

    while True:
        fault_label = 0
        if np.random.random() > 0.97:
            fault_label = int(np.random.choice([1, 2, 3]))

        voltage = voltage_kv + float(np.random.normal(0, 0.35))
        current = current_a + float(np.random.normal(0, 12))
        transformer_temp = transformer_temp_c + float(np.random.normal(0, 0.7))
        oil_temp = oil_temp_c + float(np.random.normal(0, 0.5))

        if fault_label:
            voltage, current, transformer_temp, oil_temp = apply_fault_signature(
                voltage, current, transformer_temp, oil_temp, fault_label
            )
        else:
            fault_label = infer_fault_label(voltage, current, transformer_temp, oil_temp)

        reading = make_reading(
            timestamp=pd.Timestamp.now(),
            voltage_kv=voltage,
            current_a=current,
            transformer_temp_c=transformer_temp,
            oil_temp_c=oil_temp,
            power_factor=power_factor,
            fault_label=fault_label,
        )
        push_reading(reading)
        print(
            "[PUBLISHED] "
            f"{reading['timestamp']} "
            f"V={reading['voltage_kv']}kV "
            f"I={reading['current_a']}A "
            f"T={reading['transformer_temp_c']}C "
            f"label={reading['label']}"
        )
        time.sleep(1)


if __name__ == "__main__":
    main()
