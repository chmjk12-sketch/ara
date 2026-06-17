"""
ARA - Adaptive Reality Agent
FastAPI Application Entry Point
"""
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from src.config import settings
from src.api.v1.router import router as v1_router
from src.models.schemas import HealthResponse, MetricsResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print(f"ARA (Adaptive Reality Agent) starting on port {settings.APP_PORT}")
    yield
    # Shutdown
    print("ARA shutting down")


app = FastAPI(
    title="ARA - Adaptive Reality Agent",
    description="自适应深度的现象分析Agent",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(v1_router)


# Health check
@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(status="ok")


# Metrics
@app.get("/metrics", response_model=MetricsResponse)
async def metrics_endpoint():
    from src.api.v1.endpoints import metrics
    total = metrics["total_requests"]
    times = metrics["response_times"]
    avg_time = sum(times) / len(times) if times else 0.0
    return MetricsResponse(
        total_requests=total,
        active_conversations=len(
            __import__("src.api.v1.endpoints", fromlist=["conversations"]).conversations
        ),
        avg_response_time_ms=round(avg_time * 1000, 2),
    )


# MCP Tools
@app.get("/mcp/tools")
async def list_tools():
    return {
        "tools": [
            {
                "name": "analyze_reality",
                "description": "分析现实世界现象，自适应深度输出",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "question": {"type": "string", "description": "用户问题"},
                        "depth": {
                            "type": "string",
                            "enum": ["Level0", "Level1", "Level2", "Level3"],
                            "description": "分析深度",
                        },
                    },
                    "required": ["question"],
                },
            }
        ]
    }


# Serve frontend
@app.get("/")
async def serve_frontend():
    return FileResponse("/app/frontend/index.html")


# Mount static files
app.mount("/static", StaticFiles(directory="/app/frontend"), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.APP_PORT)
