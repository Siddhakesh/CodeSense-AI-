"""
File-level data models.
"""
from pydantic import BaseModel, Field


class FileNode(BaseModel):
    """
    Representation of a source file in the repository.
    """
    path: str = Field(..., description="Relative path to the file from repository root")
    language: str = Field(..., description="Programming language (python, javascript, typescript, etc.)")
    imports: list[str] = Field(default_factory=list, description="List of imported modules/files")
    size: int = Field(..., description="File size in bytes")
    file_type: str = Field(default="source", description="Type of file (module, component, config, etc.)")
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "path": "app/main.py",
                "language": "python",
                "imports": ["fastapi", "app.models.user"],
                "size": 1024,
                "file_type": "module"
            }
        }
