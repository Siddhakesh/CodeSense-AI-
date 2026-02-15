"""
Repository cloning and file scanning logic.
"""
import subprocess
from pathlib import Path


# Directories to ignore during file scanning
IGNORE_DIRS = {
    '.git',
    'node_modules',
    'dist',
    'build',
    '__pycache__',
    '.venv',
    'venv',
    '.pytest_cache',
    '.mypy_cache',
    'coverage',
    '.next',
    'out',
}

# Source file extensions to include
SOURCE_EXTENSIONS = {
    '.py',
    '.js',
    '.jsx',
    '.ts',
    '.tsx',
    '.go',
    '.java',
    '.rb',
    '.php',
    '.c',
    '.cpp',
    '.h',
    '.hpp',
    '.rs',
    '.swift',
    '.kt',
    '.cs',
}


def clone_repo(repo_url: str, dest: Path) -> None:
    """
    Clone a GitHub repository to the specified destination.
    
    Args:
        repo_url: GitHub repository URL (https or git format)
        dest: Destination path for cloning
        
    Raises:
        subprocess.CalledProcessError: If git clone fails
        FileExistsError: If destination already exists
    """
    if dest.exists():
        # If it exists and is a git repo, we can reuse it
        if (dest / ".git").exists():
            # Optional: git pull to update
            return
        
        # If it's an empty directory, we can use it (e.g. created by mkdtemp)
        if any(dest.iterdir()):
             # Not empty and not a git repo -> error
             raise FileExistsError(f"Destination {dest} exists and is not a git repository")
        
        # If empty, proceed to clone
    
    dest.parent.mkdir(parents=True, exist_ok=True)
    
    # Use git CLI for cloning
    # --depth=1 for shallow clone to save bandwidth
    # --single-branch to clone only the default branch
    result = subprocess.run(
        ['git', 'clone', '--depth=1', '--single-branch', repo_url, str(dest)],
        capture_output=True,
        text=True,
        check=True
    )
    
    if result.returncode != 0:
        raise subprocess.CalledProcessError(
            result.returncode,
            result.args,
            result.stdout,
            result.stderr
        )


def scan_files(repo_path: Path) -> list[Path]:
    """
    Scan repository and return list of source files.
    
    Args:
        repo_path: Path to cloned repository
        
    Returns:
        List of source file paths (relative to repo_path)
        
    Raises:
        FileNotFoundError: If repo_path does not exist
    """
    if not repo_path.exists():
        raise FileNotFoundError(f"Repository path {repo_path} does not exist")
    
    if not repo_path.is_dir():
        raise NotADirectoryError(f"{repo_path} is not a directory")
    
    source_files = []
    
    def should_ignore_dir(dir_path: Path) -> bool:
        """Check if directory should be ignored."""
        return dir_path.name in IGNORE_DIRS
    
    def is_source_file(file_path: Path) -> bool:
        """Check if file is a source code file."""
        return file_path.suffix in SOURCE_EXTENSIONS
    
    # Recursively walk the directory tree
    for item in repo_path.rglob('*'):
        # Skip if any parent directory should be ignored
        if any(should_ignore_dir(parent) for parent in item.parents):
            continue
        
        # Add source files
        if item.is_file() and is_source_file(item):
            # Store relative path from repo root
            source_files.append(item.relative_to(repo_path))
    
    return source_files
