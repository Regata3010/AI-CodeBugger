import streamlit as st
from typing import Dict, Any, Optional
import time
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from services.api_client import AICodeReviewAPIClient

def create_chat_section(upload_data: Dict[str, Any], api_client: AICodeReviewAPIClient, analysis_results: Optional[Dict[str, Any]] = None) -> None:
    """
    Create chat interface based on upload context
    
    Args:
        upload_data: Result from upload component  
        api_client: API client for backend communication
        analysis_results: Optional results from analysis component
    """
    
    st.markdown("---")
    st.markdown("### 💬 AI Code Assistant")
    
    # Determine chat context and show appropriate interface
    if upload_data["type"] == "single_file":
        _handle_single_file_chat(upload_data, api_client, analysis_results)
    elif upload_data["type"] in ["project", "github"]:
        _handle_project_chat(upload_data, api_client, analysis_results)

def _handle_single_file_chat(upload_data: Dict[str, Any], api_client: AICodeReviewAPIClient, analysis_results: Optional[Dict[str, Any]] = None) -> None:
    """Handle chat for single uploaded file"""
    
    code = upload_data["data"]["code"]
    filename = upload_data["data"]["filename"]
    
    st.info(f"💡 Chatting about: **{filename}**")
    
    # Quick action buttons if analysis was done
    if analysis_results:
        st.markdown("#### ⚡ Quick Follow-up Questions")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔍 Explain results", key="explain_results"):
                _ask_quick_question("Can you explain the analysis results in simple terms?", code, api_client)
        
        with col2:
            if st.button("🚀 How to improve?", key="improve_code"):
                _ask_quick_question("Based on the analysis, how can I improve this code?", code, api_client)
        
        with col3:
            if st.button("🧪 Testing advice?", key="test_advice"):
                _ask_quick_question("What should I test for this code?", code, api_client)
    
    # Regular chat interface
    _create_chat_interface(code, "single_file", api_client)

def _handle_project_chat(upload_data: Dict[str, Any], api_client: AICodeReviewAPIClient, analysis_results: Optional[Dict[str, Any]] = None) -> None:
    """Handle chat for uploaded project (ZIP or GitHub)"""
    
    project_data = upload_data["data"]
    project_name = project_data["project_name"]
    files = project_data["files"]
    
    st.info(f"📁 Project chat: **{project_name}** ({len(files)} files)")
    
    # Chat scope selection
    chat_scope = st.radio(
        "Chat about:",
        ["💬 Entire Project", "📄 Specific File"],
        help="Choose whether to discuss the whole project or focus on one file"
    )
    
    selected_file_index = None
    context_info = f"Project: {project_name}"
    
    if chat_scope == "📄 Specific File":
        # File selection for chat
        selected_file_index = st.selectbox(
            "Select file to discuss:",
            options=range(len(files)),
            format_func=lambda i: f"📄 {files[i]['name']} ({files[i]['size']} bytes)",
            help="Choose which file you want to ask questions about"
        )
        
        selected_file = files[selected_file_index]
        context_info = f"File: {selected_file['name']}"
        st.success(f"💡 Chatting about: **{selected_file['name']}**")
        
        # Quick questions for specific file
        if analysis_results and 'project_analysis_results' in st.session_state:
            _show_file_specific_quick_questions(selected_file, api_client, project_data["project_id"])
    
    # Project chat interface
    _create_project_chat_interface(project_data["project_id"], selected_file_index, context_info, api_client)

def _create_chat_interface(code: str, context_type: str, api_client: AICodeReviewAPIClient) -> None:
    """Create general chat interface for single file"""
    
    # Chat input
    user_question = st.text_input(
        "Ask something about your code:",
        placeholder="e.g., 'How does this function work?' or 'Any security issues?'",
        help="Ask any question about your code - the AI will provide context-aware answers"
    )
    
    # Send button
    col1, col2 = st.columns([3, 1])
    with col1:
        send_chat = st.button("📩 Send Question", type="secondary")
    with col2:
        if st.button("🗑️ Clear Chat", help="Clear conversation history"):
            _clear_chat_history("single_file")
    
    if send_chat and user_question:
        _process_single_file_chat(code, user_question, api_client)

def _create_project_chat_interface(project_id: str, file_index: Optional[int], context_info: str, api_client: AICodeReviewAPIClient) -> None:
    """Create project chat interface"""
    
    # Show current chat context
    st.caption(f"🎯 Current context: {context_info}")
    
    # Chat input
    user_question = st.text_input(
        "Ask about your project:",
        placeholder="e.g., 'How do these files work together?' or 'What's the architecture?'",
        help="Ask questions about your project - specify files or ask about overall architecture"
    )
    
    # Send button with project context
    col1, col2 = st.columns([3, 1])
    with col1:
        send_chat = st.button("📩 Send Question", type="secondary")
    with col2:
        if st.button("🗑️ Clear Project Chat"):
            _clear_project_chat_history(project_id)
    
    if send_chat and user_question:
        _process_project_chat(project_id, user_question, file_index, api_client)

def _ask_quick_question(question: str, code: str, api_client: AICodeReviewAPIClient) -> None:
    """Process quick question and display response"""
    
    try:
        with st.spinner(f"🤔 {question}"):
            session_id = st.session_state.get("chat_session_id", "quick_questions")
            
            api_response = api_client.chat_about_code(
                code=code,
                question=question,
                session_id=session_id,
                model_choice="gpt-4o"
            )
            
            if api_response["status"] == "success":
                with st.expander(f"🧠 AI Response: {question[:50]}...", expanded=True):
                    st.markdown(api_response["response"])
                    st.caption(f"⏱️ Response time: {api_response['execution_time']:.2f}s")
            else:
                st.error(f"❌ Quick question failed: {api_response.get('message', 'Unknown error')}")
    
    except Exception as e:
        st.error(f"❌ Quick question error: {str(e)}")

def _process_single_file_chat(code: str, question: str, api_client: AICodeReviewAPIClient) -> None:
    """Process single file chat and display response"""
    
    try:
        # Get or create session ID
        if "chat_session_id" not in st.session_state:
            st.session_state["chat_session_id"] = f"user_{int(time.time())}"
        
        session_id = st.session_state["chat_session_id"]
        
        api_response = api_client.chat_about_code(
            code=code,
            question=question,
            session_id=session_id,
            model_choice="gpt-4o"
        )
        
        if api_response["status"] == "success":
            # Display conversation
            with st.container():
                st.markdown("**🧑 You:**")
                st.write(question)
                
                st.markdown("**🤖 AI Assistant:**")
                st.markdown(api_response["response"])
                
                st.caption(f"⏱️ Response time: {api_response['execution_time']:.2f}s")
                st.markdown("---")
        else:
            st.error(f"❌ Chat failed: {api_response.get('message', 'Unknown error')}")
    
    except Exception as e:
        st.error(f"❌ Chat error: {str(e)}")

def _process_project_chat(project_id: str, question: str, file_index: Optional[int], api_client: AICodeReviewAPIClient) -> None:
    """Process project chat and display response"""
    
    try:
        # Create project-specific session ID
        session_id = f"project_{project_id}_user"
        
        api_response = api_client.chat_about_project(
            project_id=project_id,
            question=question,
            file_index=file_index,
            session_id=session_id
        )
        
        if api_response["status"] == "success":
            # Display conversation with project context
            with st.container():
                st.markdown("**🧑 You:**")
                st.write(question)
                
                st.markdown("**🤖 AI Assistant:**")
                st.markdown(api_response["response"])
                
                # Show context info
                st.caption(f"🎯 Context: {api_response.get('context_info', 'Project')}")
                st.caption(f"⏱️ Response time: {api_response['execution_time']:.2f}s")
                st.markdown("---")
        else:
            st.error(f"❌ Project chat failed: {api_response.get('message', 'Unknown error')}")
    
    except Exception as e:
        st.error(f"❌ Project chat error: {str(e)}")

def _show_file_specific_quick_questions(selected_file: Dict[str, Any], api_client: AICodeReviewAPIClient, project_id: str) -> None:
    """Show quick questions specific to the selected file"""
    
    st.markdown("#### ⚡ Quick Questions About This File")
    
    file_name = selected_file["name"]
    file_size = selected_file["size"]
    
    # Generate contextual questions based on file characteristics
    quick_questions = []
    
    if file_name.startswith("test_"):
        quick_questions = [
            f"What does {file_name} test?",
            f"How comprehensive are these tests?",
            f"Any missing test cases in {file_name}?"
        ]
    elif file_name in ["main.py", "app.py"]:
        quick_questions = [
            f"What is the main purpose of {file_name}?",
            f"How is {file_name} structured?",
            f"Any architectural issues in {file_name}?"
        ]
    elif "model" in file_name.lower():
        quick_questions = [
            f"What data models are defined in {file_name}?",
            f"How do these models relate to each other?",
            f"Any data validation issues in {file_name}?"
        ]
    else:
        quick_questions = [
            f"What does {file_name} do?",
            f"How does {file_name} fit in the project?",
            f"Any improvements for {file_name}?"
        ]
    
    # Display quick question buttons
    cols = st.columns(len(quick_questions))
    for i, question in enumerate(quick_questions):
        with cols[i]:
            if st.button(f"❓ {question[:20]}...", key=f"quick_q_{i}"):
                _process_project_chat(project_id, question, selected_file["index"], api_client)

def _clear_chat_history(context: str) -> None:
    """Clear chat history for given context"""
    
    chat_keys = [key for key in st.session_state.keys() if key.startswith(f"chat_{context}")]
    for key in chat_keys:
        del st.session_state[key]
    
    st.success("🗑️ Chat history cleared!")
    st.rerun()

def _clear_project_chat_history(project_id: str) -> None:
    """Clear chat history for specific project"""
    
    chat_keys = [key for key in st.session_state.keys() if f"project_{project_id}" in key]
    for key in chat_keys:
        del st.session_state[key]
    
    st.success(f"🗑️ Project chat history cleared!")
    st.rerun()

def display_chat_suggestions(upload_data: Dict[str, Any]) -> None:
    """Display helpful chat suggestions based on context"""
    
    if upload_data["type"] == "single_file":
        suggestions = [
            "What does this code do?",
            "Are there any security issues?",
            "How can I optimize this?",
            "What edge cases should I consider?",
            "Is this code following best practices?"
        ]
    else:  # Project
        suggestions = [
            "What is the overall architecture?",
            "How do these files work together?",
            "What's the main entry point?",
            "Any architectural improvements?",
            "Which files are most critical?"
        ]
    
    with st.expander("💡 Suggested Questions", expanded=False):
        st.markdown("**Click any question to ask:**")
        for suggestion in suggestions:
            if st.button(f"❓ {suggestion}", key=f"suggestion_{hash(suggestion)}"):
                return suggestion
    
    return None

def create_enhanced_chat_interface(upload_data: Dict[str, Any], api_client: AICodeReviewAPIClient) -> None:
    """Enhanced chat interface with context awareness"""
    
    st.markdown("### 💬 Enhanced AI Code Assistant")
    
    # Show current context
    if upload_data["type"] == "single_file":
        st.success(f"🎯 Ready to chat about: **{upload_data['data']['filename']}**")
    else:
        project = st.session_state.get('current_project', {})
        st.success(f"🎯 Ready to chat about: **{project.get('project_name', 'Project')}**")
    
    # Chat history display
    _display_recent_chat_history(upload_data)
    
    # Main chat interface
    col1, col2 = st.columns([4, 1])
    
    with col1:
        user_question = st.text_input(
            "Ask your question:",
            placeholder="Type your question about the code...",
            help="Ask anything about your code - the AI provides context-aware answers"
        )
    
    with col2:
        st.markdown("&nbsp;")  # Spacing
        send_button = st.button("📩 Send", type="primary")
    
    # Process chat
    if send_button and user_question:
        if upload_data["type"] == "single_file":
            _process_single_file_chat(upload_data["data"]["code"], user_question, api_client)
        else:
            # For projects, default to entire project chat unless user specifies file
            project_id = upload_data["data"]["project_id"]
            _process_project_chat(project_id, user_question, None, api_client)
    
    # Suggested questions
    suggestion = display_chat_suggestions(upload_data)
    if suggestion:
        if upload_data["type"] == "single_file":
            _process_single_file_chat(upload_data["data"]["code"], suggestion, api_client)
        else:
            project_id = upload_data["data"]["project_id"]
            _process_project_chat(project_id, suggestion, None, api_client)

def _display_recent_chat_history(upload_data: Dict[str, Any]) -> None:
    """Display recent chat history from session state"""
    
    if upload_data["type"] == "single_file":
        history_key = "single_file_chat_history"
    else:
        project_id = upload_data["data"]["project_id"]
        history_key = f"project_{project_id}_chat_history"
    
    if history_key in st.session_state and st.session_state[history_key]:
        with st.expander("📜 Recent Conversation", expanded=False):
            history = st.session_state[history_key]
            
            for i, chat_item in enumerate(history[-3:]):  # Show last 3 exchanges
                st.markdown(f"**🧑 You:** {chat_item['question']}")
                st.markdown(f"**🤖 AI:** {chat_item['response'][:200]}{'...' if len(chat_item['response']) > 200 else ''}")
                if i < len(history[-3:]) - 1:
                    st.markdown("---")

def store_chat_in_session(context_key: str, question: str, response: str) -> None:
    """Store chat exchange in session state for history"""
    
    history_key = f"{context_key}_chat_history"
    
    if history_key not in st.session_state:
        st.session_state[history_key] = []
    
    chat_item = {
        "question": question,
        "response": response,
        "timestamp": time.time()
    }
    
    st.session_state[history_key].append(chat_item)
    
    # Keep only last 10 exchanges
    if len(st.session_state[history_key]) > 10:
        st.session_state[history_key] = st.session_state[history_key][-10:]

def is_chat_available(upload_data: Dict[str, Any]) -> bool:
    """Check if chat is available for current context"""
    
    if upload_data["type"] == "single_file":
        return bool(upload_data["data"]["code"].strip())
    elif upload_data["type"] in ["project", "github"]:
        return "project_id" in upload_data["data"]
    
    return False

def get_chat_context_info(upload_data: Dict[str, Any], file_index: Optional[int] = None) -> str:
    """Get human-readable chat context information"""
    
    if upload_data["type"] == "single_file":
        return f"Single file: {upload_data['data']['filename']}"
    elif upload_data["type"] in ["project", "github"]:
        project_name = upload_data["data"]["project_name"]
        if file_index is not None:
            files = upload_data["data"]["files"]
            file_name = files[file_index]["name"]
            return f"Project file: {file_name} in {project_name}"
        else:
            return f"Entire project: {project_name}"
    
    return "Unknown context"