"""
Dependency graph construction logic.
"""
import re
from pathlib import Path


# TODO: These patterns are naive and may produce false positives
# Consider using AST parsing (ast module for Python, esprima/babel for JS/TS) for more accuracy

# Python import patterns
PYTHON_IMPORT_PATTERNS = [
    r'^import\s+([\w\.]+)',  # import module
    r'^from\s+([\w\.]+)\s+import',  # from module import ...
]

# JavaScript/TypeScript import patterns
JS_IMPORT_PATTERNS = [
    r'import\s+.*?\s+from\s+[\'"]([^\'"]+)[\'"]',  # import ... from 'module'
    r'require\([\'"]([^\'"]+)[\'"]\)',  # require('module')
]


def extract_imports(file_path: Path) -> list[str]:
    """
    Extract import statements from a source file.
    
    Args:
        file_path: Path to source file
        
    Returns:
        List of imported module/file names (relative imports only)
        
    Note:
        This implementation uses regex and is naive. It may miss complex
        import statements or produce false positives. External packages
        are filtered out heuristically.
    """
    if not file_path.exists() or not file_path.is_file():
        return []
    
    suffix = file_path.suffix.lower()
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except OSError:
        return []
    
    imports = []
    
    # Python files
    if suffix == '.py':
        imports = _extract_python_imports(content)
    
    # JavaScript/TypeScript files
    elif suffix in {'.js', '.jsx', '.ts', '.tsx'}:
        imports = _extract_js_imports(content)
    
    # Filter out external packages (heuristic: relative imports only)
    filtered_imports = []
    for imp in imports:
        if _is_local_import(imp, suffix):
            filtered_imports.append(imp)
    
    return filtered_imports


def build_dependency_graph(files: list[Path]) -> dict[str, list[str]]:
    """
    Build a dependency graph from a list of files.
    
    Args:
        files: List of source file paths (should be relative paths)
        
    Returns:
        Dictionary mapping file paths (as strings) to their dependencies (as strings)
        
    Note:
        The graph is an adjacency list where keys are file paths and values
        are lists of files they depend on. Circular dependencies are allowed.
    """
    graph = {}
    
    # Create a mapping of module names to file paths for resolution
    file_map = _build_file_map(files)
    
    for file_path in files:
        file_str = str(file_path.as_posix())  # Use forward slashes for consistency
        imports = extract_imports(file_path)
        
        # Resolve imports to actual file paths
        dependencies = []
        for imp in imports:
            resolved = _resolve_import(imp, file_path, file_map)
            if resolved:
                dependencies.append(resolved)
        
        graph[file_str] = dependencies
    
    return graph


def _extract_python_imports(content: str) -> list[str]:
    """Extract Python import statements from file content."""
    imports = []
    
    for line in content.split('\n'):
        line = line.strip()
        
        # Skip comments
        if line.startswith('#'):
            continue
        
        for pattern in PYTHON_IMPORT_PATTERNS:
            match = re.match(pattern, line)
            if match:
                module = match.group(1)
                imports.append(module)
                break
    
    return imports


def _extract_js_imports(content: str) -> list[str]:
    """Extract JavaScript/TypeScript import statements from file content."""
    imports = []
    
    for pattern in JS_IMPORT_PATTERNS:
        matches = re.findall(pattern, content)
        imports.extend(matches)
    
    return imports


def _is_local_import(import_path: str, file_suffix: str) -> bool:
    """
    Heuristically determine if an import is local/relative.
    
    Args:
        import_path: The imported module/file path
        file_suffix: The suffix of the source file (.py, .js, etc.)
        
    Returns:
        True if the import appears to be local/relative
    """
    # Python: relative imports start with '.'
    if file_suffix == '.py':
        if import_path.startswith('.'):
            return True
        # Filter out common stdlib and third-party packages
        # This is a simple heuristic - may need refinement
        external_prefixes = [
            'os', 'sys', 'json', 're', 'pathlib', 'typing',
            'fastapi', 'django', 'flask', 'requests', 'numpy',
            'pandas', 'pydantic', 'sqlalchemy', 'asyncio'
        ]
        if any(import_path.startswith(prefix) for prefix in external_prefixes):
            return False
        # If it contains a dot, might be a local module (e.g., app.models)
        if '.' in import_path:
            return True
        # Single-word imports might be local modules
        return True
    
    # JS/TS: relative imports start with './' or '../'
    if file_suffix in {'.js', '.jsx', '.ts', '.tsx'}:
        if import_path.startswith('./'):
            return True
        if import_path.startswith('../'):
            return True
        if import_path.startswith('@/'):
            return True  # Common alias for src directory
        # Filter out node_modules packages (don't start with '.')
        return False
    
    return False


def _build_file_map(files: list[Path]) -> dict[str, Path]:
    """
    Build a mapping from module names to file paths.
    
    Args:
        files: List of file paths
        
    Returns:
        Dictionary mapping module names to file paths
    """
    file_map = {}
    
    for file_path in files:
        # Map by filename without extension
        stem = file_path.stem
        if stem not in file_map:
            file_map[stem] = file_path
        
        # Map by full path without extension (for nested modules)
        path_parts = file_path.parts[:-1] + (stem,)
        module_path = '.'.join(path_parts)
        file_map[module_path] = file_path
    
    return file_map


def _resolve_import(import_path: str, source_file: Path, file_map: dict[str, Path]) -> str | None:
    """
    Resolve an import path to an actual file path.
    
    Args:
        import_path: The imported module/file path
        source_file: The file containing the import
        file_map: Mapping of module names to file paths
        
    Returns:
        Resolved file path as string, or None if not found
    """
    # TODO: This is a simplified resolution - may need more sophisticated logic
    
    # Try direct lookup in file map
    if import_path in file_map:
        return str(file_map[import_path].as_posix())
    
    # Try removing leading dots (for relative Python imports)
    cleaned = import_path.lstrip('.')
    if cleaned in file_map:
        return str(file_map[cleaned].as_posix())
    
    # Try just the last component
    last_component = import_path.split('.')[-1]
    if last_component in file_map:
        return str(file_map[last_component].as_posix())
    
    # For JS/TS, try resolving relative paths
    if import_path.startswith('./') or import_path.startswith('../'):
        # TODO: Implement proper relative path resolution
        # This would require knowing the source file's directory
        pass
    
    return None
