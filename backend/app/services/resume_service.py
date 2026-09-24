from pathlib import Path

from app.services import ai_service
from app.services.text_extraction import extract_text

RESUME_ANALYSIS_PROMPT = """You are a technical placement advisor reviewing a student's resume.

Analyze the resume text below and respond ONLY with a JSON object matching this exact schema:
{{
  "detected_skills": [string],
  "missing_skills": [string],
  "relevant_technologies": [string],
  "strengths": [string],
  "improvement_areas": [string],
  "suggestions": [string],
  "summary": string
}}

Guidelines:
- "detected_skills" are technical and soft skills clearly present in the resume.
- "missing_skills" are commonly expected skills for the student's apparent target roles that are absent.
- "relevant_technologies" are frameworks, tools, and languages mentioned or implied.
- Keep every list realistic, specific, and limited to at most 8 items.
- "summary" should be 2-3 sentences.
- Do not fabricate experience the resume does not support.

Resume:
\"\"\"
{resume_text}
\"\"\"
"""

JOB_MATCH_PROMPT = """You are a technical placement advisor comparing a resume against a job description.

Respond ONLY with a JSON object matching this exact schema:
{{
  "matching_skills": [string],
  "missing_skills": [string],
  "relevant_technologies": [string],
  "alignment_percentage": integer between 0 and 100,
  "suggestions": [string]
}}

Guidelines:
- "matching_skills" are skills present in both the resume and job description.
- "missing_skills" are skills the job description requires that the resume does not demonstrate.
- "alignment_percentage" is an approximate estimate, not a guarantee of selection.
- Keep lists realistic and at most 8 items each.
- Do not claim the candidate will be selected.

Resume:
\"\"\"
{resume_text}
\"\"\"

Job Description:
\"\"\"
{job_description}
\"\"\"
"""


def analyze_resume_file(file_path: Path) -> dict:
    resume_text = extract_text(file_path)
    if not resume_text.strip():
        raise ValueError("No readable text found in the uploaded resume.")

    prompt = RESUME_ANALYSIS_PROMPT.format(resume_text=resume_text[:12000])
    return ai_service.generate_json(prompt)


def match_resume_to_job(file_path: Path, job_description: str) -> dict:
    resume_text = extract_text(file_path)
    if not resume_text.strip():
        raise ValueError("No readable text found in the uploaded resume.")

    prompt = JOB_MATCH_PROMPT.format(
        resume_text=resume_text[:12000], job_description=job_description[:6000]
    )
    return ai_service.generate_json(prompt)
