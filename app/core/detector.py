"""
Framework and technology detection logic.
"""
from pathlib import Path
import json


def detect_framework(repo_path: Path) -> str:
    """
    Detect the primary framework used in a repository.
    
    Args:
        repo_path: Path to repository
        
    Returns:
        Framework name or "unknown"
        
    Detection is based on presence of framework-specific configuration files
    and package dependencies.
    """
    if not repo_path.exists() or not repo_path.is_dir():
        return "unknown"
    
    # Check for Next.js (highest priority for Node.js projects)
    if _is_nextjs(repo_path):
        return "nextjs"
    
    # Check for Node.js/Express
    if _is_nodejs_express(repo_path):
        return "express"
    
    # Check for FastAPI
    if _is_fastapi(repo_path):
        return "fastapi"
    
    # Check for Django
    if _is_django(repo_path):
        return "django"
    
    # Check for generic Node.js
    if _is_nodejs(repo_path):
        return "nodejs"
    
    # Check for generic Python
    if _is_python(repo_path):
        return "python"
    
    return "unknown"


def _is_nextjs(repo_path: Path) -> bool:
    """Check if repository is a Next.js project."""
    # Check for next.config.js or next.config.mjs
    if (repo_path / "next.config.js").exists():
        return True
    if (repo_path / "next.config.mjs").exists():
        return True
    
    # Check package.json for Next.js dependency
    package_json = repo_path / "package.json"
    if package_json.exists():
        try:
            with open(package_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
                dependencies = data.get('dependencies', {})
                dev_dependencies = data.get('devDependencies', {})
                
                if 'next' in dependencies or 'next' in dev_dependencies:
                    return True
        except (json.JSONDecodeError, OSError):
            pass
    
    return False


def _is_nodejs_express(repo_path: Path) -> bool:
    """Check if repository is a Node.js Express project."""
    package_json = repo_path / "package.json"
    if not package_json.exists():
        return False
    
    try:
        with open(package_json, 'r', encoding='utf-8') as f:
            data = json.load(f)
            dependencies = data.get('dependencies', {})
            
            # Check for Express in dependencies
            if 'express' in dependencies:
                return True
    except (json.JSONDecodeError, OSError):
        pass
    
    return False


def _is_nodejs(repo_path: Path) -> bool:
    """Check if repository is a Node.js project."""
    # Check for package.json
    if (repo_path / "package.json").exists():
        return True
    
    # Check for node_modules (might exist even without package.json)
    if (repo_path / "node_modules").exists():
        return True
    
    return False


def _is_fastapi(repo_path: Path) -> bool:
    """Check if repository is a FastAPI project."""
    # Check for common FastAPI entry point files
    fastapi_files = ['main.py', 'app.py', 'api.py']
    
    for filename in fastapi_files:
        file_path = repo_path / filename
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Check for FastAPI imports
                    if 'from fastapi import' in content or 'import fastapi' in content:
                        return True
            except OSError:
                pass
    
    # Check requirements.txt
    requirements = repo_path / "requirements.txt"
    if requirements.exists():
        try:
            with open(requirements, 'r', encoding='utf-8') as f:
                content = f.read().lower()
                if 'fastapi' in content:
                    return True
        except OSError:
            pass
    
    # Check pyproject.toml
    pyproject = repo_path / "pyproject.toml"
    if pyproject.exists():
        try:
            with open(pyproject, 'r', encoding='utf-8') as f:
                content = f.read().lower()
                if 'fastapi' in content:
                    return True
        except OSError:
            pass
    
    return False


def _is_django(repo_path: Path) -> bool:
    """Check if repository is a Django project."""
    # Check for manage.py (Django's management script)
    if (repo_path / "manage.py").exists():
        return True
    
    # Check for Django-specific directories
    for item in repo_path.iterdir():
        if item.is_dir():
            # Check for settings.py in subdirectories
            settings_file = item / "settings.py"
            if settings_file.exists():
                try:
                    with open(settings_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if 'DJANGO_SETTINGS_MODULE' in content or 'django.conf' in content:
                            return True
                except OSError:
                    pass
    
    # Check requirements.txt for Django
    requirements = repo_path / "requirements.txt"
    if requirements.exists():
        try:
            with open(requirements, 'r', encoding='utf-8') as f:
                content = f.read().lower()
                if 'django' in content and 'djangorestframework' not in content:
                    return True
                # Django REST framework also indicates Django
                if 'djangorestframework' in content:
                    return True
        except OSError:
            pass
    
    return False


def _is_python(repo_path: Path) -> bool:
    """Check if repository is a Python project."""
    # Check for Python-specific files
    python_markers = [
        'requirements.txt',
        'setup.py',
        'pyproject.toml',
        'Pipfile',
        'poetry.lock',
    ]
    
    for marker in python_markers:
        if (repo_path / marker).exists():
            return True
    
    return False
