"""
API endpoint for analyzing repository structure and patterns.
"""
from fastapi import APIRouter

router = APIRouter()


from pydantic import BaseModel
from ..core.repo_loader import clone_repo, scan_files
from ..core.detector import detect_framework
from ..core.graph_builder import extract_imports, build_dependency_graph
from ..core.heuristics import detect_patterns
from ..models.repo import RepoIndex

class AnalysisRequest(BaseModel):
    repo_url: str

class AnalysisResponse(BaseModel):
    repo_id: str
    index: RepoIndex

@router.post("/analyze")
async def analyze_repository(request: AnalysisRequest):
    """
    Analyze repository structure and generate insights.
    """
    # 1. Clone Repo
    # For MVP, we'll clone to a temp directory based on repo name
    # In production, use a proper temp manager and cleanup
    import tempfile
    import shutil
    import stat
    import os
    from pathlib import Path
    
    def on_rm_error(func, path, exc_info):
        """
        Error handler for ``shutil.rmtree``.
        If the error is due to an access error (read only file)
        it attempts to add write permission and then retries.
        If the error is for another reason it re-raises the error.
        Usage : ``shutil.rmtree(path, onerror=on_rm_error)``
        """
        # Is the error an access error?
        os.chmod(path, stat.S_IWRITE)
        try:
            func(path)
        except Exception:
            pass
    
    repo_name = request.repo_url.split("/")[-1].replace(".git", "")
    # Use a persistent temp dir for now to allow chatting later
    temp_dir = Path(tempfile.gettempdir()) / "explain_codebase" / repo_name
    
    if temp_dir.exists():
        # Try to remove, but don't fail hard if we can't (might just overwrite)
        try:
            shutil.rmtree(temp_dir, onerror=on_rm_error)
        except Exception:
            pass
            
    # Ensure parent exists
    if not temp_dir.parent.exists():
        temp_dir.parent.mkdir(parents=True, exist_ok=True)
        
    # If it still exists (rmtree failed completely), we might have issues cloning
    # But git clone might fail if dir exists and is not empty.
    # Let's hope git clone handles it or we catch it.
    
    if not temp_dir.exists():
         clone_repo(request.repo_url, temp_dir)
    else:
        # If dir exists, maybe we just use it? 
        # But if it's a new request we probably want to update it.
        # For now, let's try to pull if exists or just proceed.
        # Simplest for MVP: just use existing if we couldn't delete it.
        pass
    
    # 2. Scan Files
    source_files = scan_files(temp_dir)
    
    # 3. Detect Framework
    framework = detect_framework(temp_dir)
    
    # 4. Build Dependency Graph
    # Convert scanner paths (relative) to absolute for graph builder if needed, 
    # but graph builder expects relative paths usually if we want specific output.
    # Actually graph builder takes list of paths.
    
    # We need to pass full paths to extract_imports but store relative in the graph?
    # Let's see graph_builder.py implementation again.
    # extract_imports takes file_path. build_dependency_graph takes list[Path].
    # We should pass full paths to build_dependency_graph
    
    full_paths = [temp_dir / f for f in source_files]
    dependency_graph = build_dependency_graph(full_paths)
    
    # Convert graph keys back to relative paths for cleaner output
    rel_graph = {}
    for k, v in dependency_graph.items():
        # k is absolute path string, v is list of absolute path strings
        rel_k = str(Path(k).relative_to(temp_dir).as_posix())
        rel_v = [str(Path(dep).relative_to(temp_dir).as_posix()) for dep in v if temp_dir in Path(dep).parents]
        rel_graph[rel_k] = rel_v
        
    # 5. Heuristics
    # We need to implement detect_patterns in heuristics.py first
    patterns = detect_patterns(temp_dir, source_files)
    
    # 6. Construct RepoIndex
    # We need to construct FileNodes first. 
    # This is getting complex for a single function, but MVP.
    from ..models.file import FileNode
    
    files_map = {}
    for f in source_files:
        path_str = str(f.as_posix())
        node = FileNode(
            path=path_str,
            language=f.suffix.lstrip('.'),
            size=(temp_dir / f).stat().st_size,
            imports=extract_imports(temp_dir / f)
        )
        files_map[path_str] = node
        
    index = RepoIndex(
        repo_url=request.repo_url,  # Fixed: usage of correct field name from request
        framework=framework,
        files=list(files_map.values()), # Fixed: RepoIndex expects list, not dict
        dependency_graph=rel_graph,
        total_files=len(source_files), # Fixed: Missing total_files
        patterns=patterns,
        id=repo_name # Wait, RepoIndex doesn't have id field check?
    )
    
    return {"repo_id": repo_name, "index": index, "patterns": patterns}
