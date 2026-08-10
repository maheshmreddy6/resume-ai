import json

from openai import OpenAI

from app.config import settings
from app.utils.prompts import ANALYSIS_PROMPT


class LLMService:

    def __init__(self):
        self.client = OpenAI(
            api_key=settings.OPENAI_API_KEY
        )

    def analyze_resume(
        self,
        job_description: str,
        resume_context: str
    ):
        prompt = ANALYSIS_PROMPT.format(
            job_description=job_description,
            resume_context=resume_context
        )

        response = self.client.chat.completions.create(
            model=settings.MODEL_NAME,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        content = response.choices[0].message.content

        if not content:
            raise ValueError(
                "The AI model returned an empty response."
            )

        # Remove Markdown JSON fences if the model returns them
        content = content.strip()

        if content.startswith("```json"):
            content = content[7:]

        if content.startswith("```"):
            content = content[3:]

        if content.endswith("```"):
            content = content[:-3]

        content = content.strip()

        try:
            return json.loads(content)

        except json.JSONDecodeError:
            return {
                "match_score": "N/A",
                "strengths": [],
                "missing_skills": [],
                "interview_questions": [],
                "summary": content
            }
