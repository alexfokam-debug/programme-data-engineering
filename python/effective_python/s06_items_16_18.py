scores = [100, 90, 80, 70, 60, 50]


def split_scores(scores):
    first, *middle, last = scores
    return first, middle, last


tasks = ["SQL", "Python", "PySpark", "Databricks"]


def number_tasks(tasks):

    result = []

    for number, task in enumerate(tasks, start=1):
        result.append((number, task))

    return result


def build_study_plan(subjects, durations):

    study_plan = []
    for subject, duration in zip(subjects, durations):
        study_plan.append((subject, duration))
    return study_plan


def organize_study_plan(subjects, durations):
    plan = []
    for number, (subject, duration) in enumerate(zip(subjects, durations), start=1):
        plan.append((number, subject, duration))

    first, *middle, last = plan
    return first, middle, last
