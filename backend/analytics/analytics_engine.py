import pandas as pd


# =====================================================
# HISTORY STATISTICS
# =====================================================

def calculate_history_statistics(history):

    total_analyses = len(history)

    avg_ats = (
        sum(item.get('ats_score', 0) for item in history) / total_analyses
        if total_analyses > 0 else 0
    )

    max_ats = max(
        (item.get('ats_score', 0) for item in history),
        default=0
    )

    total_skills = sum(
        item.get('skills_count', 0) for item in history
    )

    return {
        "total_analyses": total_analyses,
        "avg_ats": avg_ats,
        "max_ats": max_ats,
        "total_skills": total_skills
    }


# =====================================================
# TREND DATA
# =====================================================

def prepare_trend_data(history):

    trend_data = pd.DataFrame({
        'Analysis': [f"#{i+1}" for i in range(len(history))],
        'ATS Score': [item.get('ats_score', 0) for item in history]
    })

    return trend_data


# =====================================================
# COMPARISON DATA
# =====================================================

def compare_analyses(analysis1, analysis2):

    score1 = analysis1.get('ats_score', 0)
    score2 = analysis2.get('ats_score', 0)

    improvement = score2 - score1

    skills1 = set(analysis1.get('found_skills', []))
    skills2 = set(analysis2.get('found_skills', []))

    new_skills = skills2 - skills1

    removed_skills = skills1 - skills2

    comparison_df = pd.DataFrame({
        'Analysis': ['Analysis 1', 'Analysis 2'],
        'ATS Score': [
            analysis1.get('ats_score', 0),
            analysis2.get('ats_score', 0)
        ],
        'Skills': [
            analysis1.get('skills_count', 0),
            analysis2.get('skills_count', 0)
        ]
    })

    return {
        "improvement": improvement,
        "new_skills": new_skills,
        "removed_skills": removed_skills,
        "comparison_df": comparison_df
    }