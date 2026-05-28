skills = [
    "python",
    "java",
    "c++",
]

def extract_skills(resume_text):

    resume_lower = resume_text.lower()

    found_skills = []

    for skill in skills:

        if skill.lower() in resume_lower:
            found_skills.append(skill)

    return list(set(found_skills))