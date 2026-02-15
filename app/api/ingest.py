"""
API endpoint for ingesting GitHub repositories.
"""
import shutil
import tempfile
from pathlib import Path
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, HttpUrl

from ..core import repo_loader, detector, graph_builder
from ..models.repo import RepoIndex
from ..models.file import FileNode

router = APIRouter()


class IngestRequest(BaseModel):
    """Request model for repository ingestion."""
    repo_url: str = Field(..., description="GitHub repository URL (https format)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "repo_url": "https://github.com/fastapi/fastapi"
            }
        }


@router.post("/ingest", response_model=RepoIndex)
async def ingest_repository(request: IngestRequest) -> RepoIndex:
    """
    Clone and analyze a GitHub repository.
    
    This endpoint:
    1. Clones the repository to a temporary directory
    2. Scans for source files
    3. Detects the framework
    4. Builds a dependency graph
    5. Returns a structured index of the repository
    
    Args:
        request: Contains the GitHub repository URL
        
    Returns:
        RepoIndex containing repository structure and metadata
        
    Raises:
        HTTPException: If cloning, scanning, or analysis fails
    """
    temp_dir = None
    
    try:
        # Create temporary directory for cloning
        temp_dir = Path(tempfile.mkdtemp(prefix="repo_"))
        
        # Clone repository
        try:
            repo_loader.clone_repo(request.repo_url, temp_dir)
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to clone repository: {str(e)}"
            )
        
        # Scan files
        try:
            file_paths = repo_loader.scan_files(temp_dir)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to scan repository files: {str(e)}"
            )
        
        # Detect framework
        try:
            framework = detector.detect_framework(temp_dir)
        except Exception as e:
            # Framework detection failure shouldn't block the process
            framework = "unknown"
        
        # Build dependency graph
        try:
            # Convert to absolute paths for processing
            absolute_paths = [temp_dir / path for path in file_paths]
            abs_graph = graph_builder.build_dependency_graph(absolute_paths)
            
            # Convert graph back to relative paths for response
            dependency_graph = {}
            for k, v in abs_graph.items():
                try:
                    rel_k = str(Path(k).relative_to(temp_dir).as_posix())
                    rel_v = []
                    for dep in v:
                        # Only include dependencies within the repo
                        if temp_dir in Path(dep).parents:
                            rel_v.append(str(Path(dep).relative_to(temp_dir).as_posix()))
                    dependency_graph[rel_k] = rel_v
                except ValueError:
                    continue
        except Exception as e:
            # Graph building failure shouldn't block the process
            dependency_graph = {}
        
        # Build FileNode objects
        file_nodes = []
        for file_path in file_paths:
            absolute_path = temp_dir / file_path
            
            # Determine language from extension
            language = _get_language(absolute_path)
            
            # Extract imports
            try:
                imports = graph_builder.extract_imports(absolute_path)
            except Exception:
                imports = []
            
            # Get file size
            try:
                size = absolute_path.stat().st_size
            except Exception:
                size = 0
            
            file_node = FileNode(
                path=str(file_path.as_posix()),
                language=language,
                imports=imports,
                size=size,
                file_type="source"
            )
            file_nodes.append(file_node)
        
        # Create RepoIndex
        repo_index = RepoIndex(
            repo_url=request.repo_url,
            framework=framework,
            files=file_nodes,
            dependency_graph=dependency_graph,
            total_files=len(file_nodes)
        )
        
        return repo_index
        
    finally:
        # Clean up temporary directory
        if temp_dir and temp_dir.exists():
            try:
                shutil.rmtree(temp_dir)
            except Exception:
                # Ignore cleanup errors
                pass


def _get_language(file_path: Path) -> str:
    """Determine programming language from file extension."""
    extension_map = {
        '.py': 'python',
        '.js': 'javascript',
        '.jsx': 'javascript',
        '.ts': 'typescript',
        '.tsx': 'typescript',
        '.go': 'go',
        '.java': 'java',
        '.rb': 'ruby',
        '.php': 'php',
        '.c': 'c',
        '.cpp': 'cpp',
        '.h': 'c',
        '.hpp': 'cpp',
        '.rs': 'rust',
        '.swift': 'swift',
        '.kt': 'kotlin',
        '.cs': 'csharp',
    }
    
    suffix = file_path.suffix.lower()
    return extension_map.get(suffix, 'unknown')
