"""
Heuristic rules for detecting common patterns.
"""
from pathlib import Path


# Common patterns to look for
PATTERNS = {
    "authentication": ["auth", "login", "guard", "jwt", "session", "oauth"],
    "database": ["db", "database", "sql", "mongo", "prisma", "sequelize", "mongoose"],
    "api": ["api", "router", "controller", "endpoint", "graphql", "rest"],
    "payment": ["stripe", "paypal", "billing", "payment"],
    "docker": ["docker", "compose", "container"],
    "ci_cd": ["github/workflows", "gitlab-ci", "jenkins", "circleci"],
}

def detect_patterns(repo_path: Path, files: list[Path]) -> dict[str, bool]:
    """
    Detect architectural patterns in the repository.
    """
    detected = {k: False for k in PATTERNS}
    
    # Check file names and paths
    for f in files:
        parts = f.parts
        file_str = str(f).lower()
        
        for category, keywords in PATTERNS.items():
            if detected[category]:
                continue
            
            # Check filename/path matches
            if any(k in file_str for k in keywords):
                detected[category] = True
                
    # Deep check could involve reading content, but file names are a good first pass
    
    return detected
