from src.agency_alert_dispatcher import AgencyAlertDispatcher
from src.notifications.mock_sms import MockSMSChannel
from src.database import Database


def result():
    return {'event_id':'GT-DISPATCH','prediction':'HIGH_RISK_MINING_ACTIVITY','risk_level':'CRITICAL','confidence':.93,'suspected_zone':'BETWEEN_NODE_A_AND_NODE_B','location':{'segment_id':'SEGMENT_A_B','centroid':{'latitude':5.6059,'longitude':-.1842},'district':'Example District'},'evidence':{'turbidity_difference':62.4,'audio_machine_probability':.91,'vibration_machinery_probability':.87,'persistent_activity':True,'persistence_seconds':42}}

def test_demo_dispatch_and_dedupe(tmp_path):
    db=Database(tmp_path/'db.sqlite'); mock=MockSMSChannel(True); d=AgencyAlertDispatcher(db,channels={'sms':mock})
    x=d.dispatch(result()); assert x['eligible']; assert x['dispatch_status']=='SIMULATED'; assert len(mock.sent)==3
    y=d.dispatch(result()); assert y['dispatch_status']=='DEDUPLICATED'
