import hashlib
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class IdempotentAlertGateway:
    '''
    Prevents alarm fatigue during extended grid anomalies.
    Uses an idempotent hash filter over a time window to suppress duplicate alerts.
    '''
    def __init__(self, cache_ttl_seconds=300):
        self.cache_ttl = cache_ttl_seconds
        self.alert_cache = {}

    def _generate_fingerprint(self, fault_type, equipment_id):
        '''Creates a unique SHA-256 hash for the specific fault on specific equipment.'''
        raw = f"{fault_type}_{equipment_id}"
        return hashlib.sha256(raw.encode()).hexdigest()

    def dispatch_alert(self, fault_type, equipment_id, severity, timestamp=None):
        '''
        Dispatches an alert if it is novel, or suppresses it if it is a duplicate
        within the TTL window.
        '''
        fingerprint = self._generate_fingerprint(fault_type, equipment_id)
        current_time = timestamp if timestamp else time.time()
        
        if fingerprint in self.alert_cache:
            last_time = self.alert_cache[fingerprint]
            if current_time - last_time < self.cache_ttl:
                logging.debug(f"Suppressed duplicate alert for {equipment_id}")
                return {"status": "suppressed", "message": "Idempotent block: Alert recently dispatched."}
                
        # Register the new alert in the cache
        self.alert_cache[fingerprint] = current_time
        
        # In a real system, this triggers an API call to a PagerDuty or SCADA SMS system
        alert_msg = f"CRITICAL: {fault_type} on {equipment_id}. Severity: {severity}"
        logging.info(f"DISPATCHED: {alert_msg}")
        
        return {"status": "dispatched", "message": alert_msg}