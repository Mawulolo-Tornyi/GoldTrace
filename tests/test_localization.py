from src.localization import estimate_zone

def test_between_nodes(): assert estimate_zone(False,True)=="BETWEEN_NODE_A_AND_NODE_B"
def test_no_zone(): assert estimate_zone(False,False)=="NO_SUSPECTED_ZONE"
