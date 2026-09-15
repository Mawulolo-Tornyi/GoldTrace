from src.database import Database

def test_database_roundtrip(tmp_path):
    d=Database(tmp_path/"test.db"); x={"timestamp":"x","event_id":"e","prediction":"SAFE"}; d.save_prediction(x); assert d.latest_prediction()["event_id"]=="e"
