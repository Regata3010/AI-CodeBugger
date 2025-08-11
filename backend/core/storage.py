from typing import Dict, Any

# Shared storage for all modules
projects_storage: Dict[str, Any] = {}

def get_project(project_id: str) -> Dict[str, Any]:
    """Get project by ID with validation"""
    if project_id not in projects_storage:
        return None
    return projects_storage[project_id]

def store_project(project_id: str, project_data: Dict[str, Any]) -> None:
    """Store project data"""
    projects_storage[project_id] = project_data

def get_file_content(project_id: str, file_index: int) -> Dict[str, str]:
    """Get specific file content by index"""
    project = get_project(project_id)
    if not project:
        raise ValueError("Project not found")
    
    if file_index >= len(project["python_files"]):
        raise ValueError(f"File index {file_index} out of range")
    
    target_file = project["python_files"][file_index]
    
    with open(target_file["full_path"], 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    return {
        "content": content,
        "file_name": target_file["name"],
        "file_path": target_file["path"]
    }