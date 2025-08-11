import streamlit as st
import warnings
from services.api_client import AICodeReviewAPIClient
from components.upload_component import create_upload_section
from components.analysis_component import create_analysis_section, display_previous_results
from components.chat_component import create_chat_section

# Suppress warnings
warnings.filterwarnings("ignore", category=UserWarning, module="langchain")

# Page configuration
st.set_page_config(
    page_title="🧠 AI Code Review Platform", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Main title and description
st.title("🧠 AI Code Review & Optimizer Platform")
st.markdown("**Advanced AI-powered code analysis with dynamic prompting and enterprise architecture**")

# Initialize API client
@st.cache_resource
def get_api_client():
    """Initialize and cache API client"""
    return AICodeReviewAPIClient()

api_client = get_api_client()

# Backend health check
st.markdown("### 🔌 System Status")
with st.spinner("Checking backend connection..."):
    if api_client.is_backend_healthy():
        st.success("✅ Connected to AI Backend API (FastAPI + Dynamic Prompting)")
    else:
        st.error("❌ Backend API is not running")
        st.markdown("**To start the backend:**")
        st.code("cd backend && python main.py", language="bash")
        st.markdown("**Expected backend URL:** http://localhost:8000")
        st.stop()

# Main application flow
st.markdown("---")

# FIXED: Check if user wants to reset upload
if "reset_upload" not in st.session_state:
    st.session_state.reset_upload = False

if st.session_state.reset_upload:
    # Clear all upload-related session state
    keys_to_clear = []
    for key in st.session_state.keys():
        if any(x in key.lower() for x in ['upload', 'current_project', 'analysis_results', 'chat']):
            keys_to_clear.append(key)
    
    for key in keys_to_clear:
        if key != 'reset_upload':  # Don't clear the reset flag itself yet
            del st.session_state[key]
    
    st.session_state.reset_upload = False  # Reset the flag
    st.rerun()

# Phase 1: Upload Section
# In app.py - modify the upload section
if st.session_state.get('force_skip_upload_tabs', False):
    # Skip upload tabs, use persistent state
    upload_result = st.session_state.get('persistent_upload')
else:
    # Normal upload flow
    upload_result = create_upload_section(api_client)

if upload_result:
    # FIXED: Show current upload with switching options
    st.markdown("### 📁 Current Upload")
    
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        # Show upload info
        upload_type = upload_result["type"]
        if upload_type == "single_file":
            filename = upload_result["data"]["filename"]
            code_length = len(upload_result["data"]["code"])
            st.success(f"📄 **Single File:** {filename} ({code_length:,} characters)")
        elif upload_type in ["project", "github"]:
            project_name = upload_result["data"]["project_name"]
            total_files = upload_result["data"]["total_files"]
            source = "GitHub Repository" if upload_type == "github" else "ZIP Project"
            st.success(f"📁 **{source}:** {project_name} ({total_files} Python files)")
    
    with col2:
        # FIXED: Upload different file/project button
        if st.button("🔄 Upload Different", help="Choose a different file or project", key="upload_different"):
            st.session_state.reset_upload = True
            st.rerun()
    
    with col3:
        # FIXED: Clear everything button
        if st.button("🗑️ Clear All", help="Clear everything and start fresh", key="clear_all"):
            st.session_state.clear()
            st.rerun()
    
    st.markdown("---")
    
    # Phase 2: Analysis Section
    st.markdown("### 🔍 Code Analysis")
    
    analysis_result = create_analysis_section(upload_result, api_client)
    
    # Phase 3: Chat Section (always available after upload)
    st.markdown("---")
    create_chat_section(upload_result, api_client, analysis_result)

else:
    # No upload - show helpful message
    st.info("👆 Choose your upload method above to get started with AI code analysis!")

# Phase 4: Previous Results Display (only if results exist)
if ('analysis_results' in st.session_state and st.session_state['analysis_results']) or \
   ('project_analysis_results' in st.session_state and st.session_state['project_analysis_results']) or \
   ('multi_file_analysis_results' in st.session_state and st.session_state['multi_file_analysis_results']):
    st.markdown("---")
    display_previous_results()

# Sidebar: API Information and Help
with st.sidebar:
    st.markdown("### 🔧 System Information")
    
    # API status
    st.markdown("**Backend API Status:**")
    if api_client.is_backend_healthy():
        st.markdown("🟢 **Online** - All services available")
    else:
        st.markdown("🔴 **Offline** - Please start backend")
    
    # Available models
    st.markdown("**Available AI Models:**")
    models = api_client.get_available_models()
    for model in models:
        model_info = api_client.get_model_info(model)
        st.markdown(f"• {model_info}")
    
    # Feature overview
    st.markdown("### ✨ Platform Features")
    st.markdown("""
    **Single File Analysis:**
    • 🐞 Dynamic Bug Detection
    • ⚡ Code Optimization  
    • 📘 Context-Aware Explanation
    • 🧪 Unit Test Generation
    • ⚠️ Edge Case Detection
    
    **Project Analysis:**
    • 📦 ZIP File Upload
    • 🐙 GitHub Repository Analysis
    • 📄 File-Level Analysis
    • 💬 Project-Specific Chat
    
    **Advanced Features:**
    • 🎯 Dynamic Prompting (8+ contexts)
    • 🔄 Multi-File Batch Analysis
    • 💾 Persistent Chat History
    • 📊 Performance Metrics
    """)
    
    # Current session info
    if upload_result:
        st.markdown("### 📊 Current Session")
        st.markdown(f"**Upload Type:** {upload_result['type'].title()}")
        st.markdown(f"**Source:** {upload_result['source']}")
        
        if 'analysis_results' in st.session_state:
            results = st.session_state['analysis_results']
            st.metric("Analyses Completed", len(results))
            
            if results:
                avg_time = sum(r.get("execution_time", 0) for r in results.values()) / len(results)
                st.metric("Avg Response Time", f"{avg_time:.1f}s")
    
    # Quick actions
    st.markdown("### ⚡ Quick Actions")
    
    if st.button("🔄 Refresh API Connection", help="Reconnect to backend API"):
        st.cache_resource.clear()
        st.rerun()
    
    if upload_result and st.button("🆕 New Upload", help="Upload a different file/project"):
        st.session_state.reset_upload = True
        st.rerun()
    
    if st.button("🗑️ Clear All Data", help="Clear all session data"):
        st.session_state.clear()
        st.success("🗑️ All data cleared!")
        st.rerun()
    
    # Documentation links
    st.markdown("### 📚 Documentation")
    st.markdown(f"[🔗 API Docs](http://localhost:8000/docs)")
    st.markdown(f"[🔗 Backend Health](http://localhost:8000/health)")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p>🧠 <strong>AI Code Review Platform</strong> - Enterprise Architecture with FastAPI Backend</p>
        <p>Powered by Dynamic Prompting • Context-Aware Analysis • Microservices Architecture</p>
    </div>
    """, 
    unsafe_allow_html=True
)

# Debug information (only in development)
if st.checkbox("🔧 Show Debug Info", help="Show technical details for debugging"):
    st.markdown("### 🔧 Debug Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Session State Keys:**")
        debug_keys = [key for key in st.session_state.keys() if not key.startswith('_')]
        st.write(debug_keys)
    
    with col2:
        st.markdown("**API Client Status:**")
        st.write(f"Base URL: {api_client.base_url}")
        st.write(f"Backend Healthy: {api_client.is_backend_healthy()}")
        
        if upload_result:
            st.markdown("**Current Upload:**")
            st.write(f"Type: {upload_result['type']}")
            st.write(f"Source: {upload_result['source']}")
        
        # Test API endpoints
        if st.button("🧪 Test Backend Connection"):
            try:
                health = api_client.health_check()
                st.success(f"✅ Backend Response: {health}")
            except Exception as e:
                st.error(f"❌ Backend Error: {str(e)}")