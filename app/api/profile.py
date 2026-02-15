from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.core.github_client import GithubClient
from app.core.security import get_current_hr_user
from app.models.profile import ProfileAnalysis
from app.models.user import User

router = APIRouter()

@router.get("/profile/{username}", response_model=ProfileAnalysis)
async def analyze_profile(
    username: str,
    current_user: Annotated[User, Depends(get_current_hr_user)]
):
    """
    Analyze a GitHub user profile.
    """
    client = GithubClient()
    try:
        analysis = await client.analyze_profile(username)
        return analysis
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
