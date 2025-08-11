from pydantic import BaseModel
from typing import Optional, List

class BugAnalysisRequest(BaseModel):
    code: str
    model_choice: str = "gpt-4o"
    
class ExplanationRequest(BaseModel):
    code:str
    model_choice :str = "gpt-4o"
    
class OptimizationRequest(BaseModel):
    code: str
    model_choice: str = "gpt-4o"
    
class EdgeCaseRequest(BaseModel):
    code:str
    model_choice : str ="gpt-4o"
    
class UnitTestRequest(BaseModel):
    code:str
    model_choice : str = "gpt-4o"
    
class ConversationalRequest(BaseModel):
    code:str
    question: str
    session_id: str
    model_choice: str = "gpt-4o"
    
class ProjectChatRequest(BaseModel):
    question: str
    file_index: Optional[int] = None  # 0=first file, 1=second file, None=entire project
    session_id: str = "default"
    model_choice: str = "gpt-4o"

class ProjectAnalysisRequest(BaseModel):
    file_index: int  # Required for file-specific analysis
    analysis_type: str  # "bugs", "optimize", "explain", "tests", "edge-cases"
    model_choice: str = "gpt-4o"
    
class GitHubRequest(BaseModel):
    repo_url: str
    model_choice: str = "gpt-4o"

