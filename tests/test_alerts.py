def test_idempotent_alert_suppression():
    from src.utils.alert_gateway import IdempotentAlertGateway
    
    # Set a 60-second Time-To-Live
    gateway = IdempotentAlertGateway(cache_ttl_seconds=60)
    
    # First alert should dispatch
    res1 = gateway.dispatch_alert("Overload", "TX_01", "HIGH", timestamp=1000)
    assert res1["status"] == "dispatched", "First unique alert must dispatch"
    
    # Identical alert 10 seconds later should be suppressed
    res2 = gateway.dispatch_alert("Overload", "TX_01", "HIGH", timestamp=1010)
    assert res2["status"] == "suppressed", "Duplicate alert within TTL must be suppressed"
    
    # Identical alert 65 seconds later should dispatch (TTL expired)
    res3 = gateway.dispatch_alert("Overload", "TX_01", "HIGH", timestamp=1065)
    assert res3["status"] == "dispatched", "Alert must dispatch after TTL expires"