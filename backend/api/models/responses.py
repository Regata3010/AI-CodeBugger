from pydantic import BaseModel
from typing import Optional, List

class AnalysisResponse(BaseModel):
    status: str
    result: str
    execution_time: float
    model_used: str
    
class ExplanationResponse(BaseModel):
    status: str
    explanation: str  
    execution_time: float
    model_used: str
    
class OptimizationResponse(BaseModel):
    status: str
    optimized_code : str
    execution_time: float
    model_used: str
    
class EdgeCaseResponse(BaseModel):
    status: str
    edge_case_analysis: str
    execution_time: float
    model_used: str
    
class UnitTestResponse(BaseModel):
    status : str
    unit_tests : str
    execution_time: float
    model_used: str
    
class ConversationalResponse(BaseModel):
    status: str
    response : str
    session_id: str
    execution_time: float
    model_used: str
    
class ProjectUploadResponse(BaseModel):
    status: str
    project_id: str
    project_name: str
    total_files: int
    files: List[dict]  # [{"index": 0, "name": "main.py", "path": "main.py", "size": 1234}]

class ProjectChatResponse(BaseModel):
    status: str
    response: str
    context_info: str  # "File: main.py" or "Project: MyApp"
    session_id: str
    execution_time: float
    project_id: str

class ProjectFileAnalysisResponse(BaseModel):
    status: str
    project_id: str
    file_index: int
    file_name: str
    analysis_type: str
    result: str
    execution_time: float
    model_used: str

class GitHubAnalysisResponse(BaseModel):
    status: str
    repo_url: str
    repo_name: str
    project_id: str
    total_files: int
    files: List[dict]
    download_time: float