from src.confidence_engine import calculate_confidence

def test_confidence_range():
    c=calculate_confidence(.9,.9,.8,.85,["HEALTHY","HEALTHY"],1,.1,1); assert 0<=c<=1 and c>.7
