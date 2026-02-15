"""
Repository data models.
"""
from datetime import datetime
from pydantic import BaseModel, Field

from .file import FileNode


class RepoIndex(BaseModel):
    """
    Index of a repository's structure and metadata.
    """
    repo_url: str = Field(..., description="GitHub repository URL")
    framework: str = Field(..., description="Detected framework (nextjs, express, fastapi, django, etc.)")
    files: list[FileNode] = Field(default_factory=list, description="List of source files in the repository")
    dependency_graph: dict[str, list[str]] = Field(
        default_factory=dict,
        description="Adjacency list mapping file paths to their dependencies"
    )
    total_files: int = Field(..., description="Total number of source files")
    patterns: dict[str, bool] = Field(default_factory=dict, description="Detected architectural patterns")
    indexed_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of indexing")
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "repo_url": "https://github.com/user/repo",
                "framework": "fastapi",
                "files": [
                    {
                        "path": "app/main.py",
                        "language": "python",
                        "imports": ["fastapi"],
                        "size": 1024,
                        "file_type": "module"
                    }
                ],
                "dependency_graph": {
                    "app/main.py": ["app/models.py"]
                },
                "total_files": 1,
                "indexed_at": "2025-12-30T16:00:00Z"
            }
        }
