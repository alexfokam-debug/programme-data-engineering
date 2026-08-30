
# item 7: Use assignment expressions to simplify code

'''def classify_score(score):
    if score >= 80:
        return 'ready'
    else:
        return 'review'
'''

def classify_score(score):
    return 'ready' if score >= 80 else 'review'


# item 8: prevent repetion with assignment expressions
'''def normalize_topic(raw_topic):
    raw_topic = raw_topic.strip().lower()
    if raw_topic:
        return raw_topic    
    else:
        return None'''

def normalize_topic(raw_topic):
    if normalized := raw_topic.strip().lower():
        return normalized
    else:
        return None

# item 9: Consider match for destructuring in flow control; Avoid when if statemznts are sufficient

def describe_event(event):
    match event:
        case ('study', subject, duration) if duration > 0:
            return f'studying {subject} for {duration} minutes'
        case ('break', duration) if duration > 0   :
            return f'taking a break for {duration} minutes'
        case ('study', _,_) | ('break', _):
            return 'invalid duration'
        case _:
            return 'unknown event'
        