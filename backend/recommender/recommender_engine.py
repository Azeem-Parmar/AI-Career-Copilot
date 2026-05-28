import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

jobs_data = {

    "Job Role": [
        "Data Scientist",
        "Machine Learning Engineer",
        "AI Engineer",
        "Data Analyst",
        "Frontend Developer",
        "Backend Developer",
        "Computer Vision Engineer",
        "NLP Engineer",
        "Cloud Engineer",
        "Software Engineer"
    ],

    "Skills": [

        "python machine learning deep learning pandas numpy scikit-learn matplotlib statistics sql data analysis artificial intelligence",

        "python tensorflow keras pytorch machine learning deep learning ml ops pandas numpy scikit-learn",

        "python artificial intelligence machine learning deep learning nlp transformers tensorflow pytorch numpy pandas",

        "python pandas numpy excel power bi sql statistics data visualization matplotlib analytics",

        "html css javascript react nodejs frontend web development api",

        "python flask django fastapi sql api backend development mongodb",

        "opencv python deep learning tensorflow pytorch computer vision image processing numpy",

        "nlp python transformers spacy bert machine learning deep learning pandas numpy",

        "aws docker kubernetes linux python cloud computing devops api",

        "java c++ python problem solving data structures algorithms git github software development"
    ]
}

jobs_df = pd.DataFrame(jobs_data)

def recommend_jobs(found_skills):

    user_skills_text = " ".join(found_skills)

    job_skills = jobs_df["Skills"].tolist()

    all_text = job_skills + [user_skills_text]

    vectorizer = TfidfVectorizer()

    tfidf_matrix = vectorizer.fit_transform(all_text)

    cosine_sim = cosine_similarity(
        tfidf_matrix[-1],
        tfidf_matrix[:-1]
    )

    cosine_scores = cosine_sim[0]

    final_scores = []

    for i, skills_text in enumerate(job_skills):

        job_skill_set = set(skills_text.split())

        user_skill_set = set(found_skills)

        common_skills = user_skill_set.intersection(job_skill_set)

        overlap_score = (
            len(common_skills) / len(job_skill_set)
        ) * 100

        cosine_score = cosine_scores[i] * 100

        final_score = (
            0.5 * cosine_score +
            0.5 * overlap_score
        )

        final_score += len(common_skills) * 5

        if len(common_skills) >= 3:
            final_score += 25

        final_score = min(final_score, 100)

        final_scores.append(final_score)

    jobs_df["Match %"] = final_scores

    recommended_jobs = jobs_df.sort_values(
        by="Match %",
        ascending=False
    )

    top_jobs = recommended_jobs.head(3)

    return recommended_jobs, top_jobs