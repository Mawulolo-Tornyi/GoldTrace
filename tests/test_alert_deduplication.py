from src.database import Database

def test_dispatch_record_detection(tmp_path):
    db=Database(tmp_path/'db.sqlite'); assert not db.has_recent_agency_dispatch('E','CRITICAL')
    db.record_agency_dispatch('E','CRITICAL','SIMULATED',{})
    assert db.has_recent_agency_dispatch('E','CRITICAL')
