# services/api_client.py - Fixed to match your backend
import requests
import json
from typing import Dict, Any, Optional, List
import time

class AICodeReviewAPIClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json"
        })
    
    def is_backend_healthy(self) -> bool:
        """Check if backend is running"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def health_check(self) -> Dict[str, Any]:
        """Get backend health status"""
        response = self.session.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def get_available_models(self) -> List[str]:
        """Get available AI models"""
        return ['gpt-4o', 'gpt-3.5-turbo', 'o3-mini']
    
    def get_model_info(self, model: str) -> str:
        """Get model information"""
        model_info = {
            'gpt-4o': 'GPT-4o (Fastest & Smartest)',
            'gpt-3.5-turbo': 'GPT-3.5 Turbo (Cheaper & Fast)', 
            'o3-mini': 'O3-Mini (Reasoning Model)'
        }
        return model_info.get(model, model)
    
    # FIXED: Analysis methods that match your backend exactly
    def analyze_bugs(self, code: str, model_choice: str = "gpt-4o") -> Dict[str, Any]:
        """Analyze code for bugs - matches POST /api/v1/analyze/bugs"""
        try:
            payload = {
                "code": code,
                "model_choice": model_choice
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/analyze/bugs",
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            
            # Normalize response format for frontend
            return {
                "status": result.get("status", "success"),
                "result": result.get("result", ""),  # Your backend uses 'result'
                "execution_time": result.get("execution_time", 0),
                "model_used": result.get("model_used", model_choice)
            }
            
        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "message": f"API request failed: {str(e)}"
            }
        except Exception as e:
            return {
                "status": "error", 
                "message": f"Bug analysis error: {str(e)}"
            }
    
    def explain_code(self, code: str, model_choice: str = "gpt-4o") -> Dict[str, Any]:
        """Explain code - matches POST /api/v1/analyze/explaincode"""
        try:
            payload = {
                "code": code,
                "model_choice": model_choice
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/analyze/explaincode",
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            
            # FIXED: Backend returns 'explanation', not 'result'
            return {
                "status": result.get("status", "success"),
                "result": result.get("explanation", ""),  # Backend field is 'explanation'
                "execution_time": result.get("execution_time", 0),
                "model_used": result.get("model_used", model_choice)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Code explanation error: {str(e)}"
            }
    
    def optimize_code(self, code: str, model_choice: str = "gpt-4o") -> Dict[str, Any]:
        """Optimize code - matches POST /api/v1/analyze/optimize"""
        try:
            payload = {
                "code": code,
                "model_choice": model_choice
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/analyze/optimize",
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            
            # FIXED: Backend returns 'optimized_code', not 'result'
            return {
                "status": result.get("status", "success"),
                "result": result.get("optimized_code", ""),  # Backend field is 'optimized_code'
                "execution_time": result.get("execution_time", 0),
                "model_used": result.get("model_used", model_choice)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Code optimization error: {str(e)}"
            }
    
    def generate_edge_cases(self, code: str, model_choice: str = "gpt-4o") -> Dict[str, Any]:
        """Generate edge cases - matches POST /api/v1/analyze/edgecase"""
        try:
            payload = {
                "code": code,
                "model_choice": model_choice
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/analyze/edgecase",
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            
            # FIXED: Backend returns 'edge_case_analysis', not 'result'
            return {
                "status": result.get("status", "success"),
                "result": result.get("edge_case_analysis", ""),  # Backend field is 'edge_case_analysis'
                "execution_time": result.get("execution_time", 0),
                "model_used": result.get("model_used", model_choice)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Edge case generation error: {str(e)}"
            }
    
    def generate_tests(self, code: str, model_choice: str = "gpt-4o") -> Dict[str, Any]:
        """Generate unit tests - matches POST /api/v1/analyze/unittest"""
        try:
            payload = {
                "code": code,
                "model_choice": model_choice
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/analyze/unittest",
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            
            # FIXED: Backend returns 'unit_tests', not 'result'
            return {
                "status": result.get("status", "success"),
                "result": result.get("unit_tests", ""),  # Backend field is 'unit_tests'
                "execution_time": result.get("execution_time", 0),
                "model_used": result.get("model_used", model_choice)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Unit test generation error: {str(e)}"
            }
    
    # FIXED: Chat methods that match your backend
    def chat_about_code(self, code: str, question: str, session_id: str, model_choice: str = "gpt-4o") -> Dict[str, Any]:
        """Chat about code - matches POST /api/v1/conversational/chat"""
        try:
            payload = {
                "code": code,
                "question": question,
                "session_id": session_id,
                "model_choice": model_choice
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/conversational/chat",
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Chat error: {str(e)}"
            }
    
    def chat_about_project(self, project_id: str, question: str, file_index: Optional[int], session_id: str) -> Dict[str, Any]:
        """Chat about project - matches POST /api/v1/conversational/{project_id}/chat"""
        try:
            payload = {
                "question": question,
                "session_id": session_id
            }
            
            if file_index is not None:
                payload["file_index"] = file_index
            
            response = self.session.post(
                f"{self.base_url}/api/v1/conversational/{project_id}/chat",
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Project chat error: {str(e)}"
            }
    
    # FIXED: Project methods 
    def upload_project(self, uploaded_file) -> Dict[str, Any]:
        """Upload ZIP project - matches POST /api/v1/projects/upload"""
        try:
            # Read file content
            file_content = uploaded_file.read() if hasattr(uploaded_file, 'read') else uploaded_file
            
            files = {
                'file': (uploaded_file.name, file_content, 'application/zip')
            }
            
            response = requests.post(
                f"{self.base_url}/api/v1/projects/upload",
                files=files,
                timeout=120
            )
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Project upload error: {str(e)}"
            }
    
    def download_github_repo(self, github_url: str) -> Dict[str, Any]:
        """Download GitHub repo - CLEAN VERSION without print statements"""
        try:
            # Validate GitHub URL first
            validation_result = self.validate_github_repo(github_url)
            
            if not validation_result.get("valid", False):
                return {
                    "status": "error",
                    "message": f"Invalid repository: {validation_result.get('error', 'Unknown validation error')}"
                }
            
            payload = {
                "repo_url": github_url
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/projects/github",
                json=payload,
                timeout=120
            )
            
            # Handle different error responses
            if response.status_code == 404:
                return {
                    "status": "error",
                    "message": "Repository not found or is private. Make sure the repository exists and is public."
                }
            elif response.status_code == 408:
                return {
                    "status": "error", 
                    "message": "Download timed out. Repository might be too large. Try a smaller repository."
                }
            elif response.status_code == 400:
                error_detail = response.json().get("detail", "Bad request")
                return {
                    "status": "error",
                    "message": f"Download failed: {error_detail}"
                }
            elif response.status_code != 200:
                return {
                    "status": "error",
                    "message": f"GitHub API error: HTTP {response.status_code}"
                }
            
            result = response.json()
            
            # Add success metadata without print statements
            result["download_info"] = {
                "original_url": github_url,
                "repo_name": validation_result.get("name"),
                "language": validation_result.get("language"),
                "description": validation_result.get("description")
            }
            
            return result
        except requests.exceptions.Timeout:
            return {
                "status": "error",
                "message": "Download timed out. Repository might be too large or GitHub is slow."
            }
        except requests.exceptions.ConnectionError:
            return {
                "status": "error", 
                "message": "Could not connect to backend API. Make sure the backend is running."
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"GitHub download error: {str(e)}"
            }
        
    def validate_github_repo(self, github_url: str) -> Dict[str, Any]:
        """Validate GitHub repository before download - NEW METHOD"""
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/projects/github/validate",
                params={"repo_url": github_url},
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "valid": False,
                    "error": f"Validation API error: {response.status_code}"
                }
        
        except Exception as e:
            return {
                "valid": False,
                "error": f"Validation failed: {str(e)}"
            }

    def get_github_repo_info(self, github_url: str) -> Dict[str, Any]:
        """Get GitHub repository information - NEW METHOD"""
        try:
            # Extract owner/repo from URL
            if not github_url.startswith('https://github.com/'):
                return {"error": "Invalid GitHub URL"}
            
            url_path = github_url.replace('https://github.com/', '').strip('/')
            parts = url_path.split('/')
            
            if len(parts) < 2:
                return {"error": "Invalid repository path"}
            
            owner, repo = parts[0], parts[1]
            
            # Call GitHub API directly for testing
            import requests
            api_url = f"https://api.github.com/repos/{owner}/{repo}"
            
            response = requests.get(
                api_url,
                headers={
                    'Accept': 'application/vnd.github.v3+json',
                    'User-Agent': 'AI-Code-Review-Platform/1.0'
                },
                timeout=10
            )
            
            if response.status_code == 200:
                repo_data = response.json()
                return {
                    "name": repo_data.get('full_name'),
                    "description": repo_data.get('description'),
                    "language": repo_data.get('language'),
                    "size": repo_data.get('size'),
                    "default_branch": repo_data.get('default_branch'),
                    "stars": repo_data.get('stargazers_count'),
                    "forks": repo_data.get('forks_count'),
                    "updated_at": repo_data.get('updated_at'),
                    "public": not repo_data.get('private', True)
                }
            else:
                return {"error": f"Repository not accessible: HTTP {response.status_code}"}
        
        except Exception as e:
            return {"error": f"Failed to get repo info: {str(e)}"}
            
        except requests.exceptions.Timeout:
            return {
                "status": "error",
                "message": "Download timed out. Repository might be too large or GitHub is slow."
            }
        except requests.exceptions.ConnectionError:
            return {
                "status": "error", 
                "message": "Could not connect to backend API. Make sure the backend is running."
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"GitHub download error: {str(e)}"
            }
        
    def analyze_project_file(self, project_id: str, file_index: int, analysis_type: str, model_choice: str) -> Dict[str, Any]:
        """Analyze project file - matches POST /api/v1/projects/{project_id}/analyze"""
        try:
            payload = {
                "file_index": file_index,
                "analysis_type": analysis_type,
                "model_choice": model_choice
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/projects/{project_id}/analyze",
                json=payload,
                timeout=120
            )
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Project file analysis error: {str(e)}"
            }