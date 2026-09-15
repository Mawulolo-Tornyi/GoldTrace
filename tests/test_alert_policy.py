from src.alert_policy import evaluate_agency_alert


def critical_result():
    return {
        'event_id':'GT-X','prediction':'HIGH_RISK_MINING_ACTIVITY','risk_level':'CRITICAL','confidence':.93,
        'location':{'centroid':{'latitude':5.6,'longitude':-.18}},
        'evidence':{'turbidity_difference':62.4,'audio_machine_probability':.91,'vibration_machinery_probability':.87,'persistent_activity':True,'persistence_seconds':42}
    }

def test_critical_multi_sensor_is_eligible(): assert evaluate_agency_alert(critical_result())['eligible'] is True

def test_uncertain_never_eligible():
    r=critical_result(); r['prediction']='SYSTEM_UNCERTAIN'; r['risk_level']='UNKNOWN'
    assert evaluate_agency_alert(r)['eligible'] is False

def test_rain_like_not_eligible():
    r=critical_result(); r['risk_level']='MEDIUM'; r['evidence'].update({'audio_machine_probability':.1,'vibration_machinery_probability':.1})
    assert evaluate_agency_alert(r)['eligible'] is False
