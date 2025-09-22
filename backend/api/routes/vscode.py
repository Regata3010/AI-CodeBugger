from fastapi import APIRouter, HTTPException
from typing import Optional, List
import hashlib
import os
import time
from google.cloud import firestore
from langchain_openai import ChatOpenAI
from langchain_google_firestore import FirestoreChatMessageHistory
from core.chains.conversational import conversational_agent

# Import existing analysis functions
from ..routes.analysis import analyze_bugs, explain_code, optimize_code, edge_case, unit_test
from ..routes.chat import conversational

# Import request/response models
from ..models.requests import (
    VSCodeChatRequest, BugAnalysisRequest, ExplanationRequest,
    OptimizationRequest, EdgeCaseRequest, UnitTestRequest,
    ConversationalRequest,ConversationalVSCodeChatRequest
)
from ..models.responses import VSCodeChatResponse,ConversationalVSCodeChatResponse

router = APIRouter()


@router.post("/vscode/analyze", response_model=VSCodeChatResponse)
async def vscode_analysis_wrapper(request: VSCodeChatRequest):
    """
    Analysis wrapper - User explicitly selects analysis type
    Reuses your existing FastAPI endpoints directly
    """
    try:
        start_time = time.time()
        
        
        analysis_type = request.analysis_type  # Frontend sends this explicitly
        
      
        if analysis_type == "bugs":
            backend_request = BugAnalysisRequest(
                code=request.file_content,
                model_choice=request.model_choice
            )
            result = await analyze_bugs(backend_request)
            response = f"**Bug Analysis:**\n\n{result.result}"
            
        elif analysis_type == "explain":
            backend_request = ExplanationRequest(
                code=request.file_content,
                model_choice=request.model_choice
            )
            result = await explain_code(backend_request)
            response = f"**Code Explanation:**\n\n{result.explanation}"
            
        elif analysis_type == "optimize":
            backend_request = OptimizationRequest(
                code=request.file_content,
                model_choice=request.model_choice
            )
            result = await optimize_code(backend_request)
            response = f"**Optimized Code:**\n\n```python\n{result.optimized_code}\n```"
            
        elif analysis_type == "unittest":
            backend_request = UnitTestRequest(
                code=request.file_content,
                model_choice=request.model_choice
            )
            result = await unit_test(backend_request)
            response = f"**Unit Tests:**\n\n```python\n{result.unit_tests}\n```"
            
        elif analysis_type == "edgecase":
            backend_request = EdgeCaseRequest(
                code=request.file_content,
                model_choice=request.model_choice
            )
            result = await edge_case(backend_request)
            response = f"**Edge Cases:**\n\n{result.edge_case_analysis}"
            
        else:
            # Fallback to conversational for any other request
            session_id = f"vscode_{hashlib.md5(request.file_name.encode()).hexdigest()[:8]}"
            conversational_request = ConversationalRequest(
                code=request.file_content,
                question=request.message or "Analyze this code",
                session_id=session_id,
                model_choice=request.model_choice
            )
            result = await conversational(conversational_request)
            response = result.response
            analysis_type = "conversational"
        
        execution_time = time.time() - start_time
        
        return VSCodeChatResponse(
            status=result.status,
            response=response,
            analysis_type=analysis_type,
            execution_time=execution_time,
            model_used=result.model_used,
            # suggestions=[
            #     "Ask me questions about this analysis",
            #     "Request a different type of analysis",
            #     "Get more details on specific parts"
            # ]
        )
        
    except Exception as e:
        return VSCodeChatResponse(
            status="error",
            response=f"Analysis failed: {str(e)}",
            analysis_type="error",
            execution_time=0.0,
            model_used=request.model_choice
        )


@router.post("/vscode/chat", response_model=ConversationalVSCodeChatResponse)
async def vscode_chat_wrapper(request: ConversationalVSCodeChatRequest):
    """
    Chat wrapper - Direct conversation with context of uploaded files
    Uses Firestore for persistent memory across sessions
    """
    
    try:
        if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/app/credentials/google-credentials.json"
        # os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/AI Bugger/backend/regata-2ca53-df75398184a5.json"
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
        
        return ConversationalVSCodeChatResponse(
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


@router.get("/vscode/analysis-options")
async def get_analysis_options():
    """
    Returns available analysis types for frontend dropdown/buttons
    """
    return {
        "options": [
            {
                "value": "bugs",
                "label": "Bug Analysis",
                "description": "Find bugs and issues in your code"
            },
            {
                "value": "explain",
                "label": "Explain Code",
                "description": "Get detailed explanation of your code"
            },
            {
                "value": "optimize",
                "label": "Optimize",
                "description": "Get performance optimized version"
            },
            {
                "value": "unittest",
                "label": "Generate Tests",
                "description": "Create unit tests for your code"
            },
            {
                "value": "edgecase",
                "label": "Edge Cases",
                "description": "Identify edge cases and failures"
            }
        ]
    }


@router.get("/vscode/health")
async def health_check():
    """Simple health check"""
    return {"status": "healthy", "endpoints": ["/vscode/analyze", "/vscode/chat"]}