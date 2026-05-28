def calculate_ats_score(found_skills):

    score = 0

    score += len(found_skills) * 4

    important_skills = [
        "python",
        "machine learning",
        "deep learning",
        "tensorflow",
        "nlp",
        "sql",
        "opencv",
        "streamlit",
        "scikit-learn"
    ]

    matched_important = 0

    for skill in important_skills:

        if skill in found_skills:
            matched_important += 1

    score += matched_important * 5

    score = min(score, 100)

    return score