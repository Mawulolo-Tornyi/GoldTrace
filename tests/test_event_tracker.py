from datetime import datetime, timezone, timedelta
from src.event_tracker import EventTracker

def test_event_persists():
    t=EventTracker(); now=datetime.now(timezone.utc); a=t.update("MACHINERY_ACTIVITY","MEDIUM",.7,["NODE_B"],now); b=t.update("MACHINERY_ACTIVITY","MEDIUM",.8,["NODE_B"],now+timedelta(seconds=5)); assert a["event_id"]==b["event_id"] and b["duration"]>=5
