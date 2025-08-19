import datetime
from q2b import normalize, pick_for_date, QUOTES

def test_normalize():
    assert normalize(" Les Brown ") == "les brown"
    
def test_pick_is_deterministic():
    d = datetime.date(2025, 1, 1)
    q1 = pick_for_date(d, QUOTES)
    q2 = pick_for_date(d, QUOTES)
    assert q1 == q2
