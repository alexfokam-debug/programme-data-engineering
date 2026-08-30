from python.effective_python.s03_items_07_09 import classify_score, describe_event, normalize_topic


def test_classify_score():
    assert classify_score(85) == 'ready', "Score of 85 should be classified as 'ready'."
    assert classify_score(80) == 'ready', "Score of 80 should be classified as 'ready'."
    assert classify_score(79) == 'review', "Score of 79 should be classified as 'review'."
    assert classify_score(0) == 'review', "Score of 0 should be classified as 'review'."

def test_normalize_topic():
    assert normalize_topic("  python  ") == "python"
    assert normalize_topic("") is None
    assert normalize_topic("   ") is None



def test_describe_event():
    assert describe_event(("study", "python", 45)) == "studying python for 45 minutes"
    assert describe_event(("break", 10)) == "taking a break for 10 minutes"
    assert describe_event(("study", "python", 0)) == "invalid duration"
    assert describe_event(("break", -5)) == "invalid duration"
    assert describe_event(("unknown",)) == "unknown event"