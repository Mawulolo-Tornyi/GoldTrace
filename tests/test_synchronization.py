from src.synchronization import synchronize_packets

def test_sync_ok():
    a={"timestamp":"2026-01-01T00:00:00Z"}; b={"timestamp":"2026-01-01T00:00:01Z"}; assert synchronize_packets(a,b,3)["synchronized"]
def test_sync_rejects_large_gap():
    a={"timestamp":"2026-01-01T00:00:00Z"}; b={"timestamp":"2026-01-01T00:01:00Z"}; assert not synchronize_packets(a,b,3)["synchronized"]
