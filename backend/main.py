import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.database.session import init_db
from backend.api import upload, query, analysis, comparison, reports, analytics

# Ensure data folders exist
for folder in ["./data/documents", "./data/processed", "./data/chroma", "./data/reports", "./data/sample_hld"]:
    Path(folder).mkdir(parents=True, exist_ok=True)

# Initialize SQLite database schema
init_db()

app = FastAPI(
    title="AutoHLD-AI API",
    description="GenAI-Powered AUTOSAR HLD Document Analysis & Traceability Assistant Backend",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for Streamlit & external clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(upload.router)
app.include_router(query.router)
app.include_router(analysis.router)
app.include_router(comparison.router)
app.include_router(reports.router)
app.include_router(analytics.router)


@app.get("/")
def root():
    return {
        "system": "AutoHLD-AI",
        "description": "GenAI-Powered AUTOSAR HLD Document Analysis & Traceability Assistant",
        "status": "online",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": [
            "POST /api/documents/upload",
            "GET  /api/documents",
            "POST /api/query",
            "GET  /api/analysis/document/{id}",
            "GET  /api/analysis/document/{id}/graph",
            "GET  /api/analysis/findings",
            "PUT  /api/analysis/findings/{id}",
            "POST /api/compare",
            "POST /api/export",
            "GET  /api/audit-logs"
        ]
    }


@app.get("/api/health")
def health_check():
    return {"status": "healthy", "database": "connected", "vector_store": "ready"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
