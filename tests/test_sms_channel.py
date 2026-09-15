from src.notifications.mock_sms import MockSMSChannel

def test_mock_sms():
    c=MockSMSChannel(); r=c.send('+233X','test'); assert r.success and r.status=='SENT'
