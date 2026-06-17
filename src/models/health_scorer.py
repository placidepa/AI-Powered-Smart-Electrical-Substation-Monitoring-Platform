import numpy as np

class AssetHealthAssessor:
    '''
    Calculates Asset Health Score (0-100) and Remaining Useful Life (RUL).
    Uses cumulative degradation modeling based on thermal and electrical stress
    approximating IEEE C57.91 guidelines.
    '''
    def __init__(self):
        self.base_health = 100.0
        
    def calculate_health_score(self, temp_c, current_a, rated_temp=75, rated_current=600):
        '''
        Penalty function: Exponential decay if operating above rated parameters.
        '''
        # Calculate stress penalties without taking fractional powers of
        # negative values, which can produce invalid scalar warnings.
        temp_excess = np.maximum(np.asarray(temp_c) - rated_temp, 0)
        current_excess = np.maximum(np.asarray(current_a) - rated_current, 0)
        temp_penalty = temp_excess ** 1.2 * 0.1
        current_penalty = current_excess ** 1.1 * 0.05
        
        health = self.base_health - temp_penalty - current_penalty
        return np.clip(health, 0, 100)

    def estimate_rul(self, health_score, degradation_rate=0.05):
        '''
        Estimates days remaining until health drops below critical threshold (30.0).
        '''
        critical_threshold = 30.0
        # Handle arrays or scalar inputs
        if isinstance(health_score, (int, float)):
            if health_score <= critical_threshold:
                return 0.0
            return round((health_score - critical_threshold) / degradation_rate, 1)
        else:
            rul = (health_score - critical_threshold) / degradation_rate
            rul = np.where(rul < 0, 0, rul)
            return np.round(rul, 1)
