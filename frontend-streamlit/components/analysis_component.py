import streamlit as st
from typing import Dict, Any, Optional, List
import time
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from services.api_client import AICodeReviewAPIClient

def create_analysis_section(upload_data: Dict[str, Any], api_client: AICodeReviewAPIClient) -> Optional[Dict[str, Any]]:
    """
    Create analysis interface for uploaded code/projects
    
    Args:
        upload_data: Result from upload component
        api_client: API client for backend communication
    
    Returns:
        Dict with analysis results or None
    """
    
    st.markdown("### 🔍 Analysis Configuration")
    
    # Analysis type selection
    analysis_types = st.multiselect(
        "Choose Analysis Type:",
        [
            'Bug Detection',
            'Code Optimization', 
            'Code Explanation',
            'Unit Test Generation',
            'Edge Case Detection'
        ],
        help="Select one or more analysis types to run on your code"
    )
    
    # Model selection
    model_options = {
        'gpt-4o': 'GPT-4o (Fastest & Smartest)',
        'gpt-3.5-turbo': 'GPT-3.5 Turbo (Cheaper & Fast)', 
        'o3-mini': 'O3-Mini (Reasoning Model)'
    }
    
    model_choice = st.selectbox(
        "Choose AI Model:",
        options=list(model_options.keys()),
        format_func=lambda x: model_options[x]
    )
    
    if not analysis_types:
        st.info("👆 Please select at least one analysis type to continue")
        return None
    
    # Handle different upload types
    if upload_data["type"] == "single_file":
        return _handle_single_file_analysis(upload_data, analysis_types, model_choice, api_client)
    elif upload_data["type"] in ["project", "github"]:
        return _handle_project_analysis(upload_data, analysis_types, model_choice, api_client)
    
    return None

def _handle_single_file_analysis(upload_data: Dict[str, Any], analysis_types: List[str], model_choice: str, api_client: AICodeReviewAPIClient) -> Dict[str, Any]:
    """Handle analysis for single uploaded file"""
    
    code = upload_data["data"]["code"]
    filename = upload_data["data"]["filename"]
    
    # Show what will be analyzed
    st.info(f"🎯 Will analyze: **{filename})")
    
    # Analysis button
    if st.button("🚀 Analyze Code", type="primary"):
        return _run_single_file_analysis(code, analysis_types, model_choice, api_client)
    
    return None

def _handle_project_analysis(upload_data: Dict[str, Any], analysis_types: List[str], model_choice: str, api_client: AICodeReviewAPIClient) -> Dict[str, Any]:
    """Handle analysis for uploaded project (ZIP or GitHub)"""
    
    project_data = upload_data["data"]
    project_name = project_data["project_name"]
    files = project_data["files"]
    
    st.info(f"📁 Project loaded: **{project_name}** ({len(files)} files)")
    
    # File selection
    analysis_scope = st.radio(
        "Choose analysis scope:",
        ["🔍 Analyze Specific File", "📊 Analyze Multiple Files"],
        help="Choose whether to analyze one file or multiple files"
    )
    
    if analysis_scope == "🔍 Analyze Specific File":
        return _handle_single_file_project_analysis(project_data, analysis_types, model_choice, api_client)
    else:
        return _handle_multi_file_project_analysis(project_data, analysis_types, model_choice, api_client)

def _handle_single_file_project_analysis(project_data: Dict[str, Any], analysis_types: List[str], model_choice: str, api_client: AICodeReviewAPIClient) -> Dict[str, Any]:
    """Handle analysis of specific file in project"""
    
    files = project_data["files"]
    
    # File selection dropdown
    selected_file_index = st.selectbox(
        "Select file to analyze:",
        options=range(len(files)),
        format_func=lambda i: f"📄 {files[i]['name']} ({files[i]['size']} bytes)",
        help="Choose which file to analyze from your project"
    )
    
    selected_file = files[selected_file_index]
    st.info(f"🎯 Will analyze: **{selected_file['name']}** from {project_data['project_name']}")
    
    # Analysis button
    if st.button("🚀 Analyze Selected File", type="primary"):
        return _run_project_file_analysis(project_data["project_id"], selected_file_index, analysis_types, model_choice, api_client)
    
    return None

def _handle_multi_file_project_analysis(project_data: Dict[str, Any], analysis_types: List[str], model_choice: str, api_client: AICodeReviewAPIClient) -> Dict[str, Any]:
    """Handle analysis of multiple files in project with performance optimization"""
    
    files = project_data["files"]
    
    # Smart file limiting
    max_files = st.slider(
        "Maximum files to analyze:",
        min_value=1,
        max_value=min(len(files), 8),
        value=min(len(files), 3),
        help="⚠️ More files = longer processing time and higher costs"
    )
    
    # Cost estimation and warning
    total_operations = max_files * len(analysis_types)
    estimated_cost = total_operations * 0.02
    estimated_time = total_operations * 8
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🔢 API Calls", total_operations)
    with col2:
        st.metric("💰 Est. Cost", f"${estimated_cost:.2f}")
    with col3:
        st.metric("⏱️ Est. Time", f"{estimated_time/60:.1f} min")
    
    if total_operations > 15:
        st.warning("⚠️ **High Cost Operation** - This will make many expensive API calls")
        confirmed = st.checkbox("I understand the cost and time involved")
        if not confirmed:
            return None
    
    # Show analysis plan
    st.info(f"🎯 Will analyze: **{max_files} files** with **{len(analysis_types)} analysis types**")
    
    if st.button("🚀 Start Multi-File Analysis", type="primary"):
        return _run_optimized_multi_file_analysis(
            project_data["project_id"], 
            max_files, 
            analysis_types, 
            model_choice, 
            api_client
        )
    
    return None

def _run_single_file_analysis(code: str, analysis_types: List[str], model_choice: str, api_client: AICodeReviewAPIClient) -> Dict[str, Any]:
    """Execute analysis for single file via API"""
    
    analysis_results = {}
    
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, analysis_type in enumerate(analysis_types):
        status_text.text(f"Running {analysis_type}...")
        progress_bar.progress((i + 0.5) / len(analysis_types))
        
        try:
            # Map analysis type to API call
            api_response = _make_analysis_api_call(analysis_type, code, model_choice, api_client)
            
            if api_response["status"] == "success":
                analysis_results[analysis_type] = api_response
                _display_analysis_result(analysis_type, api_response)
            else:
                st.error(f"❌ {analysis_type} failed: {api_response.get('message', 'Unknown error')}")
        
        except Exception as e:
            st.error(f"❌ {analysis_type} error: {str(e)}")
        
        progress_bar.progress((i + 1) / len(analysis_types))
    
    status_text.text("✅ Analysis complete!")
    
    # Store results in session state
    st.session_state['analysis_results'] = analysis_results
    
    return analysis_results

def _run_project_file_analysis(project_id: str, file_index: int, analysis_types: List[str], model_choice: str, api_client: AICodeReviewAPIClient) -> Dict[str, Any]:
    """Execute analysis for specific project file"""
    
    analysis_results = {}
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, analysis_type in enumerate(analysis_types):
        status_text.text(f"Running {analysis_type} on selected file...")
        progress_bar.progress((i + 0.5) / len(analysis_types))
        
        try:
            api_type = _map_analysis_type_to_api(analysis_type)
            api_response = api_client.analyze_project_file(
                project_id, 
                file_index, 
                api_type, 
                model_choice
            )
            
            if api_response["status"] == "success":
                analysis_results[analysis_type] = api_response
                _display_project_analysis_result(analysis_type, api_response)
            else:
                st.error(f"❌ {analysis_type} failed: {api_response.get('message', 'Unknown error')}")
        
        except Exception as e:
            st.error(f"❌ {analysis_type} error: {str(e)}")
        
        progress_bar.progress((i + 1) / len(analysis_types))
    
    status_text.text("✅ Analysis complete!")
    
    # Store results with project context
    st.session_state['project_analysis_results'] = analysis_results
    
    return analysis_results

def _run_optimized_multi_file_analysis(project_id: str, max_files: int, analysis_types: List[str], model_choice: str, api_client: AICodeReviewAPIClient) -> Dict[str, Any]:
    """Execute optimized multi-file analysis"""
    
    multi_file_results = {}
    total_operations = max_files * len(analysis_types)
    
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    operation_count = 0
    start_time = time.time()
    
    for file_index in range(max_files):
        for analysis_type in analysis_types:
            status_text.text(f"🔄 File {file_index + 1}/{max_files}: {analysis_type}")
            
            try:
                api_type = _map_analysis_type_to_api(analysis_type)
                api_response = api_client.analyze_project_file(
                    project_id,
                    file_index,
                    api_type,
                    model_choice
                )
                
                if api_response["status"] == "success":
                    file_key = f"file_{file_index}"
                    if file_key not in multi_file_results:
                        multi_file_results[file_key] = {}
                    
                    multi_file_results[file_key][analysis_type] = api_response
                    
                    # Show progress result
                    st.success(f"✅ {api_response['file_name']} - {analysis_type} complete")
                
            except Exception as e:
                st.warning(f"⚠️ Skipping file {file_index} {analysis_type}: {str(e)}")
            
            operation_count += 1
            progress_bar.progress(operation_count / total_operations)
    
    total_time = time.time() - start_time
    status_text.text(f"✅ Multi-file analysis complete! ({total_time/60:.1f} minutes)")
    
    # Store and summarize results
    st.session_state['multi_file_analysis_results'] = multi_file_results
    _display_analysis_summary(multi_file_results, max_files, len(analysis_types))
    
    return multi_file_results

def _make_analysis_api_call(analysis_type: str, code: str, model_choice: str, api_client: AICodeReviewAPIClient) -> Dict[str, Any]:
    """Map analysis type to appropriate API call"""
    
    api_mapping = {
        "Bug Detection": api_client.analyze_bugs,
        "Code Optimization": api_client.optimize_code,
        "Code Explanation": api_client.explain_code,
        "Unit Test Generation": api_client.generate_tests,
        "Edge Case Detection": api_client.generate_edge_cases
    }
    
    api_function = api_mapping.get(analysis_type)
    if not api_function:
        raise ValueError(f"Unknown analysis type: {analysis_type}")
    
    return api_function(code, model_choice)

def _map_analysis_type_to_api(analysis_type: str) -> str:
    """Map UI analysis type to API analysis type"""
    
    mapping = {
        "Bug Detection": "bugs",
        "Code Optimization": "optimize", 
        "Code Explanation": "explain",
        "Unit Test Generation": "tests",
        "Edge Case Detection": "edge-cases"
    }
    
    return mapping.get(analysis_type, "bugs")

def _display_analysis_result(analysis_type: str, api_response: Dict[str, Any]):
    """Display single analysis result with proper formatting"""
    
    result = api_response["result"]
    execution_time = api_response["execution_time"]
    model_used = api_response["model_used"]
    
    # Create expandable section for each analysis
    with st.expander(f"📋 {analysis_type} Results", expanded=True):
        
        # Analysis metadata
        col1, col2 = st.columns(2)
        with col1:
            st.caption(f"⏱️ Completed in {execution_time:.2f} seconds")
        with col2:
            st.caption(f"🤖 Model: {model_used}")
        
        # Result display based on analysis type
        if analysis_type in ["Bug Detection", "Unit Test Generation", "Edge Case Detection"]:
            st.code(result, language='python')
        else:
            st.markdown(result)
        
        # Download option
        file_extension = "py" if analysis_type in ["Unit Test Generation", "Edge Case Detection"] else "md"
        filename = f"{analysis_type.lower().replace(' ', '_')}_result.{file_extension}"
        
        st.download_button(
            f"📄 Download {analysis_type} Results",
            result,
            filename,
            f"text/{'x-python' if file_extension == 'py' else 'markdown'}"
        )

def _display_project_analysis_result(analysis_type: str, api_response: Dict[str, Any]):
    """Display project file analysis result"""
    
    result = api_response["result"]
    file_name = api_response["file_name"]
    execution_time = api_response["execution_time"]
    
    st.subheader(f"📋 {analysis_type} - {file_name}")
    
    # Metadata
    col1, col2, col3 = st.columns(3)
    with col1:
        st.caption(f"📄 File: {file_name}")
    with col2:
        st.caption(f"⏱️ Time: {execution_time:.2f}s")
    with col3:
        st.caption(f"🤖 Model: {api_response['model_used']}")
    
    # Result display
    if analysis_type in ["Bug Detection", "Unit Test Generation", "Edge Case Detection"]:
        st.code(result, language='python')
    else:
        st.markdown(result)
    
    # Download with file context
    filename = f"{file_name}_{analysis_type.lower().replace(' ', '_')}.{'py' if analysis_type in ['Unit Test Generation', 'Edge Case Detection'] else 'md'}"
    st.download_button(
        f"📄 Download Results",
        result,
        filename
    )

def _display_analysis_summary(results: Dict[str, Any], files_analyzed: int, analysis_types_count: int):
    """Display analysis summary with performance metrics"""
    
    st.markdown("---")
    st.markdown("### 📊 Analysis Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📁 Files Analyzed", files_analyzed)
    with col2:
        st.metric("🔍 Analysis Types", analysis_types_count)
    with col3:
        total_operations = files_analyzed * analysis_types_count
        st.metric("⚡ API Calls Made", total_operations)
    with col4:
        if results:
            # Calculate average execution time
            total_time = 0
            total_calls = 0
            for file_results in results.values():
                for result in file_results.values():
                    total_time += result.get("execution_time", 0)
                    total_calls += 1
            
            if total_calls > 0:
                avg_time = total_time / total_calls
                st.metric("⏱️ Avg Time/Call", f"{avg_time:.1f}s")
    
    # Performance insights
    if total_operations > 10:
        st.info(f"💡 **Performance Note:** Completed {total_operations} operations successfully.")
    
    if total_operations > 20:
        st.warning(f"⚠️ **Resource Usage:** This analysis used significant API resources.")

# In analysis_component.py - Replace the display_previous_results() function

def display_previous_results():
    """Display previous analysis results in collapsible sections"""
    
    # Single file results
    if 'analysis_results' in st.session_state and st.session_state['analysis_results']:
        results = st.session_state['analysis_results']
        
        # FIXED: Use expander instead of always showing
        with st.expander("📋 Previous Analysis Results", expanded=False):
            result_tabs = list(results.keys())
            
            if result_tabs:
                tabs = st.tabs(result_tabs)
                
                for i, analysis_type in enumerate(result_tabs):
                    with tabs[i]:
                        api_response = results[analysis_type]
                        
                        # Show metadata
                        col1, col2 = st.columns(2)
                        with col1:
                            st.caption(f"⏱️ {api_response['execution_time']:.2f}s")
                        with col2:
                            st.caption(f"🤖 {api_response['model_used']}")
                        
                        # Show result
                        if analysis_type in ["Bug Detection", "Unit Test Generation", "Edge Case Detection"]:
                            st.code(api_response["result"], language='python')
                        else:
                            st.markdown(api_response["result"])
                
                # Clear results option inside expander
                if st.button("🗑️ Clear Previous Results", key="clear_single_results"):
                    st.session_state['analysis_results'] = {}
                    st.rerun()
    
    # Project analysis results
    if 'project_analysis_results' in st.session_state and st.session_state['project_analysis_results']:
        project_results = st.session_state['project_analysis_results']
        
        # FIXED: Use expander for project results too
        with st.expander("📁 Previous Project Analysis Results", expanded=False):
            for analysis_type, api_response in project_results.items():
                with st.container():
                    st.subheader(f"📋 {analysis_type} - {api_response['file_name']}")
                    
                    # Show metadata
                    col1, col2 = st.columns(2)
                    with col1:
                        st.caption(f"⏱️ {api_response['execution_time']:.2f}s")
                    with col2:
                        st.caption(f"🤖 {api_response['model_used']}")
                    
                    st.markdown(api_response["result"])
                    st.markdown("---")
            
            # Clear project results
            if st.button("🗑️ Clear Project Results", key="clear_project_results"):
                st.session_state['project_analysis_results'] = {}
                st.rerun()
    
    # Multi-file results
    if 'multi_file_analysis_results' in st.session_state and st.session_state['multi_file_analysis_results']:
        multi_results = st.session_state['multi_file_analysis_results']
        
        # FIXED: Use expander for multi-file results
        with st.expander("📊 Multi-File Analysis Results", expanded=False):
            for file_key, file_results in multi_results.items():
                st.markdown(f"#### 📄 {file_key}")
                for analysis_type, result in file_results.items():
                    with st.expander(f"{analysis_type} - {result['file_name']}", expanded=False):
                        st.caption(f"⏱️ {result['execution_time']:.2f}s | 🤖 {result['model_used']}")
                        # Show truncated result
                        result_text = result["result"]
                        if len(result_text) > 500:
                            st.markdown(result_text[:500] + "...")
                            if st.button(f"Show Full Result", key=f"show_full_{file_key}_{analysis_type}"):
                                st.markdown(result_text)
                        else:
                            st.markdown(result_text)
            
            # Clear multi-file results
            if st.button("🗑️ Clear Multi-File Results", key="clear_multi_results"):
                st.session_state['multi_file_analysis_results'] = {}
                st.rerun()

def get_analysis_summary(analysis_results: Dict[str, Any]) -> Dict[str, Any]:
    """Generate summary statistics from analysis results"""
    
    if not analysis_results:
        return {}
    
    summary = {
        "total_analyses": len(analysis_results),
        "avg_execution_time": sum(r["execution_time"] for r in analysis_results.values()) / len(analysis_results),
        "models_used": list(set(r["model_used"] for r in analysis_results.values())),
        "analysis_types": list(analysis_results.keys())
    }
    
    return summary