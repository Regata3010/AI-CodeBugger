# backend/api/routes/analysis.py
from fastapi import APIRouter, HTTPException
from langchain_openai import ChatOpenAI
import time
import os
from langchain_openai import ChatOpenAI
from google.cloud import firestore
from langchain_google_firestore import FirestoreChatMessageHistory
from core.chains.bug_chains import get_bugchains
from core.chains.explanation_chains import get_explanationchains
from core.chains.optimize_chains import get_optimized_chains
from core.chains.edgecases_chain import get_edge_case_chains
from core.chains.unittest import unittestchains
# from api.routes.projects import get_file_content, projects_storage
from core.chains.conversational import conversational_agent
from api.models.requests import BugAnalysisRequest,ExplanationRequest, OptimizationRequest, EdgeCaseRequest, UnitTestRequest, ConversationalRequest
from api.models.responses import AnalysisResponse, ExplanationResponse, OptimizationResponse, EdgeCaseResponse, UnitTestResponse, ConversationalResponse

router = APIRouter()

#Bug analysis endpoint
@router.post("/analyze/bugs", response_model=AnalysisResponse)
async def analyze_bugs(request: BugAnalysisRequest):
    """Analyze code for bugs using dynamic AI chains"""
    try:
        # Get API key from environment
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise HTTPException(status_code=500, detail="OpenAI API key not configured")
        
        start_time = time.time()
        
        # Use your existing dynamic bug detection
        llm = ChatOpenAI(
            temperature=0, 
            model=request.model_choice,
            openai_api_key=openai_api_key
        )
        bug_chain = get_bugchains(llm, request.code, use_dynamic=True)
        
        # Run analysis
        result = bug_chain.invoke({"code": request.code})
        
        execution_time = time.time() - start_time
        
        return AnalysisResponse(
            status="success",
            result=result,
            execution_time=execution_time,
            model_used=request.model_choice
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Bug analysis failed: {str(e)}"
        )
        

@router.post("/analyze/explaincode", response_model=ExplanationResponse)
async def explain_code(request: ExplanationRequest):
    """Analyze code for Explanation using dynamic AI chains"""
    try:
        # Get API key from environment
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise HTTPException(status_code=500, detail="OpenAI API key not configured")
        
        start_time = time.time()
        
        # Use your existing dynamic explanation chain
        llm = ChatOpenAI(
            temperature=0, 
            model=request.model_choice,
            openai_api_key=openai_api_key
        )
        explanation_chain = get_explanationchains(llm, request.code, use_dynamic=True)
        
        # Run analysis
        result = explanation_chain.invoke({"code": request.code})
        
        execution_time = time.time() - start_time
        
        return ExplanationResponse(
            status="success",
            explanation=result,
            execution_time=execution_time,
            model_used=request.model_choice
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Code Explanation failed: {str(e)}"
        )
        
@router.post("/analyze/optimize", response_model=OptimizationResponse)
async def optimize_code(request: OptimizationRequest):
    """Optimize code for Explanation using dynamic AI chains"""
    try:
        # Get API key from environment
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise HTTPException(status_code=500, detail="OpenAI API key not configured")
        
        start_time = time.time()
        
        # Use your existing dynamic explanation chain
        llm = ChatOpenAI(
            temperature=0, 
            model=request.model_choice,
            openai_api_key=openai_api_key
        )
        optimization_chain= get_optimized_chains(llm, request.code, use_dynamic=True)
        
        # Run analysis
        result = optimization_chain.invoke({"code": request.code})
        
        execution_time = time.time() - start_time
        
        return OptimizationResponse(
            status="success",
            optimized_code=result,
            execution_time=execution_time,
            model_used=request.model_choice
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Code Optimization failed: {str(e)}"
        )
        
@router.post("/analyze/edgecase", response_model=EdgeCaseResponse)
async def edge_case(request: EdgeCaseRequest):
    """Generate Edge Cases That Can Break Code using dynamic AI chains"""
    try:
        # Get API key from environment
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise HTTPException(status_code=500, detail="OpenAI API key not configured")
        
        start_time = time.time()
        
        # Use your existing dynamic explanation chain
        llm = ChatOpenAI(
            temperature=0, 
            model=request.model_choice,
            openai_api_key=openai_api_key
        )
        edgecases_chain = get_edge_case_chains(llm, request.code, use_dynamic=True)
        
        # Run analysis
        result = edgecases_chain.invoke({"code": request.code})
        
        execution_time = time.time() - start_time
        
        return EdgeCaseResponse(
            status="success",
            edge_case_analysis=result,
            execution_time=execution_time,
            model_used=request.model_choice
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Edge_Case failed: {str(e)}"
        )
        
        
@router.post("/analyze/unittest", response_model=UnitTestResponse)
async def unit_test(request: UnitTestRequest):
    """Generate Unit Test for Code using dynamic AI chains"""
    try:
        # Get API key from environment
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise HTTPException(status_code=500, detail="OpenAI API key not configured")
        
        start_time = time.time()
        
        # Use your existing dynamic explanation chain
        llm = ChatOpenAI(
            temperature=0, 
            model=request.model_choice,
            openai_api_key=openai_api_key
        )
        unittest_chain = unittestchains(llm, request.code, use_dynamic=True)
        
        # Run analysis
        result = unittest_chain.invoke({"code": request.code})
        
        execution_time = time.time() - start_time
        
        return UnitTestResponse(
            status="success",
            unit_tests=result,
            execution_time=execution_time,
            model_used=request.model_choice
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Unit_tests failed: {str(e)}"
        )
        
