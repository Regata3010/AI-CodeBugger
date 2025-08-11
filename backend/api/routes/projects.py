from fastapi import APIRouter, HTTPException, UploadFile, File
import tempfile
import zipfile
import os
from pathlib import Path
import uuid
import time
from langchain_openai import ChatOpenAI
from api.models.requests import ProjectChatRequest, ProjectAnalysisRequest, GitHubRequest
from api.models.responses import ProjectUploadResponse, ProjectChatResponse, ProjectFileAnalysisResponse
import requests
import tempfile
import os
from core.storage import projects_storage, store_project

router = APIRouter()


@router.post("/projects/upload", response_model=ProjectUploadResponse)
async def upload_project(file: UploadFile = File(...)):
    """Upload ZIP file and return project with indexed file list"""
    try:
        if not file.filename.endswith('.zip'):
            raise HTTPException(status_code=400, detail="Only ZIP files are supported")
        
        # Generate unique project ID
        project_id = str(uuid.uuid4())[:8]  # Short ID for easier use
        
        # Create temp directory for this project
        project_temp_dir = tempfile.mkdtemp(prefix=f"project_{project_id}_")
        extract_dir = os.path.join(project_temp_dir, "extracted")
        os.makedirs(extract_dir)
        
        # Save and extract ZIP
        zip_path = os.path.join(project_temp_dir, file.filename)
        content = await file.read()
        with open(zip_path, "wb") as f:
            f.write(content)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        # Analyze Python files with INDEX
        python_files = []
        file_index = 0
        
        for root, _, files in os.walk(extract_dir):
            for file_name in files:
                if file_name.endswith('.py'):
                    file_path = os.path.join(root, file_name)
                    relative_path = os.path.relpath(file_path, extract_dir)
                    file_size = os.path.getsize(file_path)
                    
                    python_files.append({
                        "index": file_index,
                        "name": file_name,
                        "path": relative_path,
                        "full_path": file_path,
                        "size": file_size
                    })
                    file_index += 1
        
        # Store project info
        project_info = {
            "project_id": project_id,
            "name": file.filename.replace('.zip', ''),
            "upload_time": time.time(),
            "extracted_path": extract_dir,
            "python_files": python_files,
            "total_files": len(python_files)
        }
        
        store_project(project_id, project_info)
        
        return ProjectUploadResponse(
            status="success",
            project_id=project_id,
            project_name=project_info["name"],
            total_files=len(python_files),
            files=[{
                "index": f["index"],
                "name": f["name"], 
                "path": f["path"],
                "size": f["size"]
            } for f in python_files]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Project upload failed: {str(e)}")

@router.post("/projects/{project_id}/analyze", response_model=ProjectFileAnalysisResponse)
async def analyze_project_file(project_id: str, request: ProjectAnalysisRequest):
    """Analyze specific file in uploaded project"""
    try:
        if project_id not in projects_storage:
            raise HTTPException(status_code=404, detail="Project not found")
        
        project = projects_storage[project_id]
        
        # Validate file index
        if request.file_index >= len(project["python_files"]):
            raise HTTPException(status_code=400, detail=f"File index {request.file_index} out of range. Project has {len(project['python_files'])} files.")
        
        # Get specific file
        target_file = project["python_files"][request.file_index]
        
        # Read file content
        with open(target_file["full_path"], 'r', encoding='utf-8', errors='ignore') as f:
            file_content = f.read()
        
        start_time = time.time()
        
        # Run analysis based on type
        openai_api_key = os.getenv("OPENAI_API_KEY")
        llm = ChatOpenAI(temperature=0, model=request.model_choice, openai_api_key=openai_api_key)
        
        if request.analysis_type == "optimize":
            from core.chains.optimize_chains import get_optimized_chains
            chain = get_optimized_chains(llm, file_content, use_dynamic=True)
        elif request.analysis_type == "bugs":
            from core.chains.bug_chains import get_bugchains
            chain = get_bugchains(llm, file_content, use_dynamic=True)
        elif request.analysis_type == "explain":
            from core.chains.explanation_chains import get_explanationchains
            chain = get_explanationchains(llm, file_content, use_dynamic=True)
        elif request.analysis_type == "tests":
            from core.chains.unittest import unittestchains
            chain = unittestchains(llm, file_content, use_dynamic=True)
        elif request.analysis_type == "edge-cases":
            from core.chains.edgecases_chain import get_edge_case_chains
            chain = get_edge_case_chains(llm, file_content, use_dynamic=True)
        else:
            raise HTTPException(status_code=400, detail="Invalid analysis type")
        
        result = chain.invoke({"code": file_content})
        execution_time = time.time() - start_time
        
        return ProjectFileAnalysisResponse(
            status="success",
            project_id=project_id,
            file_index=request.file_index,
            file_name=target_file["name"],
            analysis_type=request.analysis_type,
            result=result,
            execution_time=execution_time,
            model_used=request.model_choice
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File analysis failed: {str(e)}")

@router.post("/projects/github", response_model=ProjectUploadResponse)
async def analyze_github_repo(request: GitHubRequest):
    """Download GitHub repo and use existing ZIP processing pipeline"""
    try:
        repo_url = request.repo_url.strip().rstrip('/')
        
        if not repo_url.startswith('https://github.com/'):
            raise HTTPException(status_code=400, detail="Invalid GitHub URL")
        
        # Extract repo name for display
        repo_name = repo_url.split('/')[-1]
        
        # SIMPLE: Try multiple download URLs (main, master branches)
        download_urls = [
            f"{repo_url}/archive/refs/heads/main.zip",
            f"{repo_url}/archive/refs/heads/master.zip"
        ]
        
        zip_content = None
        for download_url in download_urls:
            try:
                response = requests.get(download_url, timeout=30)
                if response.status_code == 200:
                    zip_content = response.content
                    break
            except:
                continue
        
        if not zip_content:
            raise HTTPException(status_code=400, detail="Could not download repository. Make sure it's public.")
        
        # SIMPLE: Create a fake UploadFile and use existing upload_project function
        class FakeGitHubZip:
            def __init__(self, content, repo_name):
                self.filename = f"{repo_name}-github.zip"
                self.content = content
                self.size = len(content)
            
            async def read(self):
                return self.content
        
        fake_zip_file = FakeGitHubZip(zip_content, repo_name)
        
        # BRILLIANT: Reuse your existing ZIP processing!
        result = await upload_project(fake_zip_file)
        
        # Just add GitHub context to the result
        if hasattr(result, 'dict'):
            result_dict = result.dict()
        else:
            result_dict = result
        
        result_dict["project_name"] = f"GitHub: {repo_name}"
        
        return ProjectUploadResponse(**result_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"GitHub download failed: {str(e)}")


# FIXED: Add GitHub repository validation endpoint
@router.get("/projects/github/validate")
async def validate_github_repo(repo_url: str):
    """Validate GitHub repository before download"""
    try:
        repo_url = repo_url.strip().rstrip('/')
        
        if not repo_url.startswith('https://github.com/'):
            return {"valid": False, "error": "Invalid GitHub URL format"}
        
        # Extract owner and repo
        url_parts = repo_url.replace('https://github.com/', '').split('/')
        if len(url_parts) < 2:
            return {"valid": False, "error": "Invalid URL structure"}
        
        owner, repo = url_parts[0], url_parts[1]
        
        # Check if repository exists and is public
        github_api_url = f"https://api.github.com/repos/{owner}/{repo}"
        
        response = requests.get(
            github_api_url,
            headers={
                'Accept': 'application/vnd.github.v3+json',
                'User-Agent': 'AI-Code-Review-Platform/1.0'
            },
            timeout=10
        )
        
        if response.status_code == 200:
            repo_info = response.json()
            return {
                "valid": True,
                "repo_name": repo_info.get('full_name'),
                "default_branch": repo_info.get('default_branch'),
                "size": repo_info.get('size'),
                "language": repo_info.get('language'),
                "description": repo_info.get('description')
            }
        elif response.status_code == 404:
            return {"valid": False, "error": "Repository not found or is private"}
        else:
            return {"valid": False, "error": f"GitHub API error: {response.status_code}"}
    
    except Exception as e:
        return {"valid": False, "error": f"Validation error: {str(e)}"}

# FIXED: Add better logging setup
import logging

# Configure logging for GitHub operations
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add this logging to your existing upload_project function too
@router.post("/projects/upload", response_model=ProjectUploadResponse)
async def upload_project(file: UploadFile = File(...)):
    """Upload ZIP file and return project with indexed file list - ENHANCED WITH LOGGING"""
    
    logger.info(f"Starting project upload: {file.filename}")
    
    try:
        if not file.filename.endswith('.zip'):
            logger.warning(f"Invalid file type: {file.filename}")
            raise HTTPException(status_code=400, detail="Only ZIP files are supported")
        
        # Generate unique project ID
        project_id = str(uuid.uuid4())[:8]
        logger.info(f"Generated project ID: {project_id}")
        
        # Create temp directory for this project
        project_temp_dir = tempfile.mkdtemp(prefix=f"project_{project_id}_")
        extract_dir = os.path.join(project_temp_dir, "extracted")
        os.makedirs(extract_dir)
        
        logger.info(f"Created temp directory: {project_temp_dir}")
        
        # Save and extract ZIP
        zip_path = os.path.join(project_temp_dir, file.filename)
        content = await file.read()
        
        logger.info(f"Read {len(content)} bytes from uploaded file")
        
        with open(zip_path, "wb") as f:
            f.write(content)
        
        # FIXED: Better ZIP extraction with error handling
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Check for malicious paths
                for member in zip_ref.infolist():
                    if member.filename.startswith('/') or '..' in member.filename:
                        logger.warning(f"Suspicious file path detected: {member.filename}")
                        continue
                    
                zip_ref.extractall(extract_dir)
                logger.info(f"Extracted ZIP to: {extract_dir}")
                
        except zipfile.BadZipFile:
            logger.error("Invalid ZIP file uploaded")
            raise HTTPException(status_code=400, detail="Invalid ZIP file")
        
        # Analyze Python files with INDEX
        python_files = []
        file_index = 0
        
        for root, _, files in os.walk(extract_dir):
            for file_name in files:
                if file_name.endswith('.py') and not file_name.startswith('._'):  # FIXED: Skip macOS hidden files
                    file_path = os.path.join(root, file_name)
                    relative_path = os.path.relpath(file_path, extract_dir)
                    
                    # FIXED: Skip very small files (likely empty or just imports)
                    file_size = os.path.getsize(file_path)
                    if file_size < 10:  # Skip tiny files
                        continue
                    
                    python_files.append({
                        "index": file_index,
                        "name": file_name,
                        "path": relative_path,
                        "full_path": file_path,
                        "size": file_size
                    })
                    file_index += 1
        
        logger.info(f"Found {len(python_files)} Python files")
        
        if len(python_files) == 0:
            logger.warning("No Python files found in uploaded project")
            raise HTTPException(status_code=400, detail="No Python files found in the uploaded project")
        
        # Store project info
        project_info = {
            "project_id": project_id,
            "name": file.filename.replace('.zip', ''),
            "upload_time": time.time(),
            "extracted_path": extract_dir,
            "python_files": python_files,
            "total_files": len(python_files)
        }
        
        store_project(project_id, project_info)
        logger.info(f"Stored project {project_id} with {len(python_files)} files")
        
        return ProjectUploadResponse(
            status="success",
            project_id=project_id,
            project_name=project_info["name"],
            total_files=len(python_files),
            files=[{
                "index": f["index"],
                "name": f["name"], 
                "path": f["path"],
                "size": f["size"]
            } for f in python_files]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Project upload failed: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Project upload failed: {str(e)}")