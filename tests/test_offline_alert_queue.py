from src.agency_alert_dispatcher import AgencyAlertDispatcher
from src.notifications.mock_sms import MockSMSChannel
from src.database import Database


def critical():
    return {'event_id':'GT-QUEUE','prediction':'HIGH_RISK_MINING_ACTIVITY','risk_level':'CRITICAL','confidence':.95,'suspected_zone':'BETWEEN_NODE_A_AND_NODE_B','location':{'segment_id':'SEGMENT_A_B','centroid':{'latitude':5.6,'longitude':-.18}},'evidence':{'turbidity_difference':70,'audio_machine_probability':.95,'vibration_machinery_probability':.92,'persistent_activity':True,'persistence_seconds':50}}

def test_failure_queues_then_retry(tmp_path):
    db=Database(tmp_path/'db.sqlite'); failing=MockSMSChannel(False); d=AgencyAlertDispatcher(db,channels={'sms':failing}); d.dispatch(critical()); assert len(db.pending_alert_queue())==3
    d.channels['sms']=MockSMSChannel(True); x=d.retry_queue(); assert x['sent']==3; assert db.pending_alert_queue()==[]
