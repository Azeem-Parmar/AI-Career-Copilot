def chatbot_response(user_question):

    question = user_question.lower()

    response = ""

    # =====================================================
    # ATS QUESTIONS
    # =====================================================

    if "ats" in question:

        response = """
        ✅ ATS Optimization Tips

        • Add technical keywords
        • Use clean resume formatting
        • Add measurable achievements
        • Mention tools & technologies
        • Include project experience
        • Add certifications
        """

    # =====================================================
    # RESUME QUESTIONS
    # =====================================================

    elif "resume" in question:

        response = """
        📄 Resume Improvement Tips

        • Keep resume concise
        • Add strong AI/ML projects
        • Mention GitHub links
        • Add quantified achievements
        • Use ATS-friendly formatting
        • Add technical skills section
        """

    # =====================================================
    # SKILLS QUESTIONS
    # =====================================================

    elif "skill" in question:

        response = """
        🚀 Important AI/ML Skills

        • Python
        • Machine Learning
        • Deep Learning
        • NLP
        • TensorFlow
        • PyTorch
        • SQL
        • Streamlit
        • Data Structures
        """

    # =====================================================
    # PROJECT QUESTIONS
    # =====================================================

    elif "project" in question:

        response = """
        💡 Recommended AI Projects

        • AI Career Copilot
        • AI Interview Bot
        • Fake News Detection
        • Medical Diagnosis AI
        • Stock Market Prediction
        • AI Resume Analyzer
        """

    # =====================================================
    # ROADMAP QUESTIONS
    # =====================================================

    elif "roadmap" in question:

        response = """
        🛣️ AI/ML Roadmap

        1. Learn Python
        2. Learn Machine Learning
        3. Build Projects
        4. Learn Deep Learning
        5. Build Portfolio
        6. Learn Deployment
        7. Practice DSA
        """

    # =====================================================
    # JOB QUESTIONS
    # =====================================================

    elif "job" in question or "career" in question:

        response = """
        💼 Career Advice

        • Build strong projects
        • Optimize your resume
        • Improve LinkedIn profile
        • Practice interviews
        • Contribute to GitHub
        • Learn system design basics
        """

    # =====================================================
    # DEFAULT RESPONSE
    # =====================================================

    else:

        response = """
        🤖 I can help you with:

        • ATS optimization
        • Resume improvement
        • AI/ML roadmap
        • Career guidance
        • Skill recommendations
        • Project ideas
        • Job preparation
        """

    return response