from typing import List, Dict, Optional
from pydantic import BaseModel

class RepositorySummary(BaseModel):
    name: str
    description: Optional[str] = None
    language: Optional[str] = None
    stars: int
    forks: int
    url: str

class ProfileAnalysis(BaseModel):
    username: str
    name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: str
    public_repos: int
    followers: int
    following: int
    languages: Dict[str, int]
    top_repos: List[RepositorySummary]
    summary: Optional[str] = None
