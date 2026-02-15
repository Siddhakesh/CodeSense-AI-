import os
import google.generativeai as genai
from typing import Dict, List, Any

def _configure_genai():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("WARN: GEMINI_API_KEY not set. Skipping summary generation.")
        return False
    genai.configure(api_key=api_key)
    return True

async def generate_profile_summary(
    username: str,
    bio: str,
    repos_count: int,
    followers: int,
    languages: Dict[str, int],
    top_repos: List[Any]
) -> str:
    """
    Generate a professional summary for a GitHub profile using Gemini.
    """
    if not _configure_genai():
        return "Summary generation unavailable (API key missing)."

    try:
        model = genai.GenerativeModel('gemini-2.5-flash')

        # Format top repos for context
        repos_context = "\n".join([
            f"- {r.name}: {r.description} ({r.language}, {r.stars} stars)"
            for r in top_repos
        ])

        # Format languages
        sorted_langs = sorted(languages.items(), key=lambda x: x[1], reverse=True)[:5]
        langs_context = ", ".join([f"{l} ({c})" for l, c in sorted_langs])

        prompt = f"""
You are a professional career coach and technical recruiter. 
Analyze the following GitHub profile data and write a concise, professional summary (approx 2-3 paragraphs) for this developer.
Highlight their primary tech stack, expertise, and potential suitable roles.

Profile:
- Username: {username}
- Bio: {bio or "Not provided"}
- Public Repos: {repos_count}
- Followers: {followers}
- Top Languages: {langs_context}

Top Repositories:
{repos_context}

The summary should be engaging and written in markdown. Focus on their technical strengths demonstrated by the repositories.
"""

        response = await model.generate_content_async(prompt)
        return response.text
    except Exception as e:
        print(f"Error generating profile summary: {e}")
        return "Unable to generate summary at this time."
