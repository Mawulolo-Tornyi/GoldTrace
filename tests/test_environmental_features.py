from src.environmental_features import extract_environmental_features

def test_turbidity_slope_positive():
    f=extract_environmental_features([10,12,15,20],[26,26.1,26.2,26.3]); assert f["turbidity_slope"]>0
