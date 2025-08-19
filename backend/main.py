from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from api.routes import analysis, chat, projects  # Importing the analysis route

# # Import route modules (we'll create these next)
# from backend.api.routes import analysis, auth, projects

# Create FastAPI app
app = FastAPI(
    title="AI Code Review API",
    description="Advanced AI-powered code analysis platform",
    version="1.0.0"
)
# "http://localhost:3000"
# Add CORS middleware (allows frontend to call backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501","http://localhost:3000/style-test","http://localhost:3000","http://35.202.213.228:3000","http://35.202.213.228:8501"],  # Streamlit default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include route modules
app.include_router(analysis.router, prefix="/api/v1", tags=["analysis"])
app.include_router(chat.router, prefix="/api/v1", tags=["conversational"])
app.include_router(projects.router, prefix="/api/v1", tags=["projects"])
# app.include_router(auth.router, prefix="/api/v1", tags=["auth"])
# app.include_router(projects.router, prefix="/api/v1", tags=["projects"])

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "AI Code Review API is running"}

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to AI Code Review API", "docs": "/docs"}

# Run the app
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)