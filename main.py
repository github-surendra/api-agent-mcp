"""
Web API - FastAPI server exposing the MCP Agent via HTTP endpoints
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from mcp_agent import run_agent
import asyncio

app = FastAPI(
    title="MCP Agent API",
    description="Web API that exposes an AI agent powered by MCP tools",
    version="1.0.0",
)


# ── Request / Response Models ─────────────────────────────────────────────────

class QueryRequest(BaseModel):
    query: str
    context: str | None = None   # optional extra context


class AnalyzeResponse(BaseModel):
    query: str
    answer: str
    status: str


class HealthResponse(BaseModel):
    status: str
    message: str


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/", response_model=HealthResponse)
async def root():
    return HealthResponse(status="ok", message="MCP Agent API is running")


@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(status="healthy", message="All systems operational")


@app.post("/ai/analyze", response_model=AnalyzeResponse)
async def analyze(request: QueryRequest):
    """
    Send a natural-language query to the MCP Agent.
    The agent will reason over the query, call MCP tools as needed,
    and return a synthesized answer.
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    # Optionally prepend context to the query
    full_query = request.query
    if request.context:
        full_query = f"Context: {request.context}\n\nQuestion: {request.query}"

    try:
        answer = await run_agent(full_query)
        return AnalyzeResponse(
            query=request.query,
            answer=answer,
            status="success",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")


@app.post("/ai/weather")
async def get_weather(city: str):
    """Convenience endpoint — get weather for a city via the agent."""
    try:
        answer = await run_agent(f"What is the current weather in {city}?")
        return {"city": city, "answer": answer, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ai/calculate")
async def calculate(expression: str):
    """Convenience endpoint — evaluate a math expression via the agent."""
    try:
        answer = await run_agent(f"Calculate: {expression}")
        return {"expression": expression, "answer": answer, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("web_api:app", host="0.0.0.0", port=8000, reload=True)