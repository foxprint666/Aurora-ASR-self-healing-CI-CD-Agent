import os
import json
import time
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import gradio as gr
from environment.asr_env import ASREnvironment
from environment.models import ASRAction, ASRObservation
from app import demo # Import the Gradio demo we already built

# Aurora ASR: OpenEnv-v4 Compliant FastAPI Server
app = FastAPI(
    title="Aurora ASR Self-Healing Agent",
    description="OpenEnv-v4 compliant ASR environment for autonomous code repair.",
    version="1.0.0"
)

# Global environment instance (in a real app, this might be session-based)
# For the hackathon grader, we assume one active episode at a time.
_env = None

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/metadata")
async def metadata():
    return {
        "name": "Aurora ASR",
        "description": "Self-healing CI/CD agent for autonomous code repair.",
        "version": "1.0.0",
        "submission_type": "openenv-v4"
    }

@app.get("/schema")
async def schema():
    # Return the Pydantic schemas for the grader
    return {
        "action": ASRAction.model_json_schema(),
        "observation": ASRObservation.model_json_schema(),
        "state": {"type": "object", "properties": {"episode_id": {"type": "string"}}} 
    }

@app.post("/reset")
async def reset(request: Request):
    global _env
    try:
        # Grader might send a task_id or repo_path
        body = await request.json() if await request.body() else {}
        task_id = body.get("task_id", "easy")
        repo_path = body.get("repo_path", f"tasks/{task_id}")
        
        _env = ASREnvironment(repo_template=repo_path)
        observation = _env.reset()
        
        return observation.model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/step")
async def step(request: Request):
    global _env
    if _env is None:
        raise HTTPException(status_code=400, detail="Environment not initialized. Call /reset first.")
    
    try:
        body = await request.json()
        action = ASRAction(**body)
        observation = _env.step(action)
        return observation.model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/state")
async def state():
    global _env
    if _env is None:
        return {"status": "uninitialized"}
    return _env.state.model_dump()

# Mount the Gradio Dashboard on the root
# This allows users to see the UI while the grader hits the API endpoints
app = gr.mount_gradio_app(app, demo, path="/")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
