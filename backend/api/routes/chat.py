from fastapi import APIRouter, HTTPException
from langchain_openai import ChatOpenAI
import time
from google.cloud import firestore
from langchain_google_firestore import FirestoreChatMessageHistory
from core.chains.conversational import conversational_agent
from api.models.requests import ConversationalRequest, ProjectChatRequest
from api.models.responses import ConversationalResponse,ProjectChatResponse
import os
from core.storage import projects_storage,get_project, get_file_content

router = APIRouter()

@router.post("/conversational/chat", response_model=ConversationalResponse)
async def conversational(request: ConversationalRequest):
    """Ask Doubts about Code using dynamic AI chains"""
    try:
        # Get API key from environment
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/nuclearreactor3010/AI-CodeBugger/backend/regata-2ca53-df75398184a5.json"
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise HTTPException(status_code=500, detail="OpenAI API key not configured")
        
        start_time = time.time()
        
        PROJECT_ID = "regata-2ca53"
        COLLECTION_NAME = "chat_history_chains"
        
        client = firestore.Client(project=PROJECT_ID)
        chat_memory = FirestoreChatMessageHistory(
            session_id=request.session_id,
            collection=COLLECTION_NAME,
            client=client,
        )
        
        # Use your existing dynamic explanation chain
        llm = ChatOpenAI(
            temperature=0, 
            model=request.model_choice,
            openai_api_key=openai_api_key
        )
        conversational_chain = conversational_agent(llm, chat_memory,request.code, use_dynamic=True)
        
        # Run analysis
        result = conversational_chain.invoke(
            {"code": request.code, "question": request.question},
            config={"configurable": {"session_id": request.session_id}}
        )
        
        execution_time = time.time() - start_time
        
        return ConversationalResponse(
            status="success",
            response=result,
            session_id=request.session_id,
            execution_time=execution_time,
            model_used=request.model_choice
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Chat Failed {str(e)}"
        )

  
@router.post("/conversational/{project_id}/chat", response_model=ProjectChatResponse)
async def chat_about_project_file(project_id: str, request: ProjectChatRequest):
    """Chat about specific file or entire project"""
    try:
        if project_id not in projects_storage:
            raise HTTPException(status_code=404, detail="Project not found")
        
        start_time = time.time()
        project = projects_storage[project_id]
        
        def get_combined_project_code(project):
            """Combine multiple project files for chat context"""
            combined_code = []
            
            for file_info in project["python_files"]:
                try:
                    with open(file_info["full_path"], 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        
                        if len(content) > 2000:
                            content = content[:2000] + "\n# ... (file truncated)"
                        
                        combined_code.append(f"""
# ========== {file_info['path']} ==========
{content}
""")
                except Exception as e:
                    continue
            
            return "\n".join(combined_code)
        
        # Get context based on file_index
        if request.file_index is not None:
            # Validate file index
            if request.file_index >= len(project["python_files"]):
                raise HTTPException(status_code=400, detail=f"File index {request.file_index} out of range")
            
            # Chat about specific file
            target_file = project["python_files"][request.file_index]
            with open(target_file["full_path"], 'r', encoding='utf-8', errors='ignore') as f:
                context_code = f.read()
            context_info = f"File: {target_file['name']}"
        else:
            # Chat about entire project
            context_code = get_combined_project_code(project)
            context_info = f"Project: {project['name']}"
            
        # Setup Firestore chat
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/AI Bugger/regata-2ca53-df75398184a5.json"
        
        PROJECT_ID = "regata-2ca53"
        COLLECTION_NAME = "chat_history_chains"
        
        client = firestore.Client(project=PROJECT_ID)
        chat_memory = FirestoreChatMessageHistory(
            session_id=f"{project_id}_{request.session_id}",
            collection=COLLECTION_NAME,
            client=client,
        )
        
        # Dynamic conversational agent
        llm = ChatOpenAI(temperature=0, openai_api_key=os.getenv("OPENAI_API_KEY"))
        conversational_chain = conversational_agent(llm, chat_memory, context_code, use_dynamic=True)
        
        response = conversational_chain.invoke(
            {"code": context_code, "question": request.question},
            config={"configurable": {"session_id": f"{project_id}_{request.session_id}"}}
        )
        
        execution_time = time.time() - start_time
        
        return ProjectChatResponse(
            status="success",
            response=response,
            context_info=context_info,
            session_id=f"{project_id}_{request.session_id}",
            execution_time=execution_time,
            project_id=project_id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Project chat failed: {str(e)}")