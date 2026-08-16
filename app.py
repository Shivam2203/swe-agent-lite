"""
FastAPI Backend for SWE Agent
Provides REST API endpoints for the agent
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import sys
import os
import tempfile
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agents.state import AgentState
from agents.graph import build_graph
from utils.tools import write_file, read_file, get_file_path

app = FastAPI(
    title="SWE Agent API",
    description="Autonomous Multi-Agent Bug Fixer",
    version="1.0.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class BugRequest(BaseModel):
    issue: str
    code: str
    max_iterations: Optional[int] = 3

class BugResponse(BaseModel):
    success: bool
    score: float
    iterations: int
    feedback: str
    fixed_code: str
    timestamp: str

@app.get("/")
async def root():
    return {
        "message": "SWE Agent API is running!",
        "docs": "/docs",
        "status": "healthy"
    }

@app.post("/fix-bug", response_model=BugResponse)
async def fix_bug(request: BugRequest):
    """
    Fix a bug in the provided code.
    """
    try:
        # Create temporary file with buggy code
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(request.code)
            temp_path = f.name
        
        # Initial state
        initial_state = {
            "issue": request.issue,
            "file_content": request.code,
            "file_path": temp_path,
            "proposed_patch": "",
            "score": 0.0,
            "feedback": "",
            "iteration": 0,
            "history": []
        }
        
        # Build and run agent
        agent = build_graph()
        final_state = agent.invoke(initial_state)
        
        # Clean up
        os.unlink(temp_path)
        
        return BugResponse(
            success=final_state['score'] >= 0.8,
            score=final_state['score'],
            iterations=final_state['iteration'],
            feedback=final_state['feedback'],
            fixed_code=final_state.get('proposed_patch', request.code),
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}