import json
import os
import re

try:
    from google import genai as google_genai
except Exception:  # pragma: no cover
    google_genai = None

try:
    import google.generativeai as legacy_genai
except Exception:  # pragma: no cover
    legacy_genai = None


def _read_api_key():
    """Read Gemini API key from environment or Streamlit secrets file."""
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        return api_key.strip()

    secrets_path = os.path.join(os.getcwd(), ".streamlit", "secrets.toml")
    if os.path.exists(secrets_path):
        try:
            import tomllib

            with open(secrets_path, "rb") as f:
                data = tomllib.load(f)
            api_key = data.get("GEMINI_API_KEY") or data.get("gemini_api_key")
            if api_key:
                return str(api_key).strip()
        except Exception:
            pass

    return None


def _call_gemini(prompt):
    api_key = _read_api_key()
    if not api_key:
        raise ValueError(
            "Gemini API key is missing. Add GEMINI_API_KEY to your environment or create .streamlit/secrets.toml."
        )

    model_name = "gemini-2.5-flash"

    if google_genai is not None:
        client = google_genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
        )
        return getattr(response, "text", str(response))

    if legacy_genai is not None:
        legacy_genai.configure(api_key=api_key)
        model = legacy_genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        return response.text

    raise RuntimeError(
        "No supported Google Gemini SDK is installed. Reinstall requirements with the project dependencies."
    )


def generate_fallback_feedback(resume_text, job_title, job_description, reason="Offline fallback mode activated."):
    resume = (resume_text or "").lower()
    job = (job_title + " " + job_description).lower()

    essential_keywords = [
        "python", "sql", "api", "flask", "fastapi", "docker", "aws", "javascript",
        "react", "data", "machine learning", "ai", "teamwork", "communication",
        "problem solving", "projects", "testing", "git"
    ]

    found = [kw for kw in essential_keywords if kw in resume or kw in job]
    missing = [kw for kw in essential_keywords if kw not in resume and kw not in job][:5]

    score = max(65, min(94, 78 + len(found) * 2 - len(missing)))
    strengths = [
        "Strong foundation in practical technical skills and project execution.",
        "Resume shows clear evidence of relevant job-ready experience and learning momentum.",
        "The experience and skills align well with modern role expectations."
    ]
    if not found:
        strengths = [
            "The profile can be strengthened by emphasizing core responsibilities and measurable outcomes.",
            "Targeted keyword improvement will make the resume more ATS-friendly.",
            "The candidate has room to showcase tools, projects, and business impact more clearly."
        ]

    improvements = [
        "Add measurable results such as project impact, metrics, and business outcomes.",
        "Emphasize domain-specific tools, frameworks, and problem-solving examples.",
        "Align bullet points more closely with the exact job description keywords."
    ]

    rewrite_text = "Built and shipped end-to-end Python backend services using Flask/FastAPI, optimized database queries, and reduced deployment issues through CI and containerization."

    return {
        "overall_score": int(score),
        "strengths": strengths[:3],
        "areas_for_improvement": improvements,
        "keyword_analysis": {
            "found": found[:8],
            "missing": missing,
        },
        "suggested_rewrite": {
            "original": "Worked on various projects and used Python and SQL regularly.",
            "improved": rewrite_text,
        },
        "source": "fallback",
        "status_message": reason,
    }


def get_ai_feedback(resume_text, job_title, job_description):
    """Attempt Gemini analysis and gracefully fall back to a local assessment if the API is unavailable."""
    try:
        prompt_template = f"""
        You are an expert career coach and professional resume reviewer for a top tech company.
        Analyze this resume and job description.
        Respond with a single JSON object only.
        {{
            "overall_score": 0,
            "strengths": ["..."],
            "areas_for_improvement": ["..."],
            "keyword_analysis": {{"found": ["..."], "missing": ["..."]}},
            "suggested_rewrite": {{"original": "...", "improved": "..."}}
        }}

        JOB TITLE: {job_title}
        JOB DESCRIPTION: {job_description}
        RESUME TEXT: {resume_text}
        """

        response_text = _call_gemini(prompt_template)
        match = re.search(r"\{.*\}", response_text, re.DOTALL)
        if match:
            json_string = match.group(0)
            parsed = json.loads(json_string)
            parsed["source"] = "gemini"
            return parsed

        return generate_fallback_feedback(resume_text, job_title, job_description, "AI returned an unexpected format; using local fallback.")

    except ValueError as e:
        return generate_fallback_feedback(resume_text, job_title, job_description, f"API key missing; using offline fallback. Details: {e}")
    except Exception as e:
        error_text = str(e)
        if "quota" in error_text.lower() or "429" in error_text or "rate limit" in error_text.lower():
            return generate_fallback_feedback(
                resume_text,
                job_title,
                job_description,
                "Gemini quota exceeded; offline analysis is running in fallback mode."
            )
        return generate_fallback_feedback(
            resume_text,
            job_title,
            job_description,
            f"AI unavailable; offline analysis is running. Details: {error_text}"
        )


