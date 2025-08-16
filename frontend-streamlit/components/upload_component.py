# frontend/components/upload_component.py
import streamlit as st
from typing import Dict, Any, Optional, List
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from services.api_client import AICodeReviewAPIClient

def create_upload_section(api_client: AICodeReviewAPIClient) -> Optional[Dict[str, Any]]:
    """
    Create upload interface with multiple input methods
    
    Returns:
        Dict with upload result or None if no upload
    """
    
    st.markdown("### 📂 Upload Your Code")
    
    # Create tabs for different upload methods
    upload_tab1, upload_tab2, upload_tab3 = st.tabs([
        "📄 Single File", 
        "📦 Project ZIP", 
        "🔗 GitHub Repo"
    ])
    
    # Tab 1: Single File Upload
    with upload_tab1:
        result = _handle_single_file_upload()
        if result:
            return result
    
    # Tab 2: Project ZIP Upload  
    with upload_tab2:
        result = _handle_project_upload(api_client)
        if result:
            return result
    
    # Tab 3: GitHub Repository
    with upload_tab3:
        result = _handle_github_upload(api_client)
        if result:
            return result
    
    return None

def _handle_single_file_upload() -> Optional[Dict[str, Any]]:
    """Handle single Python file upload or text input"""
    
    # File upload option
    uploaded_file = st.file_uploader(
        "Upload a Python File", 
        type="py", 
        key="single_file",
        help="Upload a .py file for analysis"
    )
    
    if uploaded_file is not None:
        try:
            code_input = uploaded_file.read().decode("utf-8")
            st.success(f"✅ File uploaded: {uploaded_file.name} ({len(code_input)} characters)")
            
            return {
                "type": "single_file",
                "data": {
                    "code": code_input,
                    "filename": uploaded_file.name
                },
                "source": "file_upload"
            }
        except UnicodeDecodeError:
            st.error("❌ Could not decode file. Please ensure it's a valid Python file.")
            return None
    
    # Text input fallback (only if no file uploaded)
    code_input = st.text_area(
        "✍️ Or paste your Python code below:", 
        height=300,
        placeholder="def hello_world():\n    return 'Hello, World!'"
    )
    
    if code_input and code_input.strip():
        return {
            "type": "single_file",
            "data": {
                "code": code_input,
                "filename": "pasted_code.py"
            },
            "source": "text_input"
        }
    
    return None

def _handle_project_upload(api_client: AICodeReviewAPIClient) -> Optional[Dict[str, Any]]:
    """Handle ZIP project upload with API integration"""
    
    uploaded_zip = st.file_uploader(
        "Upload Python Project ZIP File",
        type="zip",
        key="project_zip",
        help="Upload your Python project as a ZIP file"
    )
    
    if uploaded_zip is not None:
        # Validate file size
        if uploaded_zip.size > 50 * 1024 * 1024:  # 50MB limit
            st.error("❌ File too large. Please keep ZIP files under 50MB.")
            return None
        
        try:
            # Call backend API to handle upload and processing
            api_response = api_client.upload_project(uploaded_zip)
            
            if api_response["status"] == "success":
                project_data = api_response
                
                # Store project in session state for later use
                st.session_state['current_project'] = project_data
                
                # Display project overview
                _display_project_overview(project_data)
                
                return {
                    "type": "project",
                    "data": project_data,
                    "source": "zip_upload"
                }
            else:
                st.error(f"❌ Upload failed: {api_response.get('message', 'Unknown error')}")
                return None
                
        except Exception as e:
            st.error(f"❌ Upload error: {str(e)}")
            return None
    
    return None

def _handle_github_upload(api_client: AICodeReviewAPIClient) -> Optional[Dict[str, Any]]:
    """ENHANCED GitHub repository download and analysis with validation"""
    
    st.markdown("#### 🐙 GitHub Repository Analysis")
    st.caption("Download and analyze any public GitHub repository")
    
    # GitHub URL input with validation
    col1, col2 = st.columns([3, 1])
    
    with col1:
        github_url = st.text_input(
            "Enter GitHub Repository URL:",
            placeholder="https://github.com/username/repository",
            help="Enter the full GitHub URL of a public repository"
        )
    
    with col2:
        st.markdown("&nbsp;")  # Spacing
        validate_button = st.button("✅ Validate", help="Check if repository is valid and accessible")
    
    # ENHANCED: Repository validation
    if validate_button and github_url:
        with st.spinner("🔍 Validating repository..."):
            validation = api_client.validate_github_repo(github_url)
            
            if validation.get("valid", False):
                st.success("✅ Repository is valid and accessible!")
                
                # Show repository information
                with st.expander("📊 Repository Information", expanded=True):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("⭐ Stars", validation.get("stars", "N/A"))
                    with col2:
                        st.metric("🍴 Forks", validation.get("forks", "N/A"))
                    with col3:
                        st.metric("📦 Size", f"{validation.get('size', 0)} KB")
                    
                    st.markdown(f"**📝 Description:** {validation.get('description', 'No description')}")
                    st.markdown(f"**💻 Language:** {validation.get('language', 'Unknown')}")
                    st.markdown(f"**🌿 Default Branch:** {validation.get('default_branch', 'main')}")
                    st.markdown(f"**🕐 Last Updated:** {validation.get('updated_at', 'Unknown')}")
            else:
                st.error(f"❌ Validation failed: {validation.get('error', 'Unknown error')}")
                st.info("💡 **Tips:**\n• Make sure the repository is public\n• Check the URL format\n• Verify the repository exists")
                return None
    
    # ENHANCED: Download section with better UX
    if github_url and _validate_github_url(github_url):
        st.markdown("---")
        
        # Show download preview
        repo_name = github_url.split('/')[-1]
        st.info(f"🎯 Ready to download: **{repo_name}**")
        
        # Download options
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # ENHANCED: Show estimated download info
            if st.session_state.get('repo_validated', False):
                st.caption("✅ Repository validated and ready for download")
            else:
                st.caption("💡 Click 'Validate' first to check repository accessibility")
        
        with col2:
            analyze_github = st.button(
                "🚀 Download & Analyze", 
                type="primary",
                help="Download repository and prepare for analysis",
                disabled=not st.session_state.get('repo_validated', True)  # Allow download even without validation
            )
        
        if analyze_github:
            return _process_github_download(github_url, api_client)
    
    return None

def _process_github_download(github_url: str, api_client: AICodeReviewAPIClient) -> Optional[Dict[str, Any]]:
    try:
        with st.spinner("⬇️ Downloading GitHub repository..."):
            api_response = api_client.download_github_repo(github_url)
        
        if api_response["status"] == "success":
            project_data = api_response
            
            github_upload_result = {
                "type": "github",
                "data": project_data,
                "source": "github_download"
            }
            
            # NUCLEAR: Force persistent state and immediate rerun
            st.session_state['persistent_upload'] = github_upload_result
            st.session_state['current_project'] = project_data
            st.session_state['github_download_complete'] = True
            
            # Clear the upload tabs so they don't interfere
            st.session_state['force_skip_upload_tabs'] = True
            
            st.success("✅ GitHub repository downloaded! Redirecting to analysis...")
            st.rerun()  # Force immediate page refresh
            
        else:
            st.error(f"❌ Failed: {api_response.get('message')}")
            return None
            
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        return None
    
def _display_project_overview(project_data: Dict[str, Any], is_github: bool = False):
    """Display project overview with metrics and file list - FIXED KEYS"""
    
    source_label = "🐙 GitHub Repository" if is_github else "📦 ZIP Project"
    
    with st.expander(f"📊 {source_label} Overview", expanded=True):
        # Project metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("📁 Project", project_data["project_name"])
        with col2:
            st.metric("📄 Python Files", project_data["total_files"])
        with col3:
            total_size = sum(f["size"] for f in project_data["files"])
            st.metric("💾 Total Size", f"{total_size:,} bytes")
        
        # FIXED: Use unique key that won't conflict
        project_id = project_data.get("project_id", "default")
        unique_key = f"show_files_github_{project_id}" if is_github else f"show_files_zip_{project_id}"
        
        if st.checkbox("📋 Show File List", key=unique_key):
            st.markdown("**📁 Project Files:**")
            for file_info in project_data["files"][:10]:  # Show first 10 files
                size_kb = file_info["size"] / 1024
                st.write(f"📄 **{file_info['name']}** - {size_kb:.1f} KB - `{file_info['path']}`")
            
            if len(project_data["files"]) > 10:
                st.caption(f"... and {len(project_data['files']) - 10} more files")

def _validate_github_url(url: str) -> bool:
    """Validate GitHub URL format"""
    return (
        url.startswith("https://github.com/") and
        len(url.split("/")) >= 5 and
        not url.endswith("/")
    )

def get_current_project() -> Optional[Dict[str, Any]]:
    """Get currently loaded project from session state"""
    return st.session_state.get('current_project', None)

def clear_current_project():
    """Clear current project from session state"""
    if 'current_project' in st.session_state:
        del st.session_state['current_project']

def is_project_loaded() -> bool:
    """Check if a project is currently loaded"""
    return 'current_project' in st.session_state and st.session_state['current_project'] is not None

def get_project_files() -> List[Dict[str, Any]]:
    """Get file list from current project"""
    project = get_current_project()
    return project["files"] if project else []