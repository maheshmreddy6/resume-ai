ANALYSIS_PROMPT = """
You are an expert technical recruiter.

Analyze the candidate resume against the job description.

Job Description:
{job_description}

Resume Information:
{resume_context}

Return JSON format:

{
    "match_score": "percentage",

    "strengths": [
        "skill or experience"
    ],

    "missing_skills": [
        "missing requirement"
    ],

    "interview_questions": [
        "question 1",
        "question 2"
    ],

    "summary": "short evaluation"
}
"""
