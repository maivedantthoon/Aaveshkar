import os
import sys
import json
from typing import Optional, Dict, Any
from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from core.task_planner import TaskPlanner
from executors.system_executor import SystemExecutor

# Ensure UTF-8 output across Windows consoles
try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

app = FastAPI(title="Aaveshkar 1.0 AI Assistant & Neural Transformer Engine")

# Mount static folder if it exists
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

def load_app_config() -> Dict[str, Any]:
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8-sig") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

config = load_app_config()

planner = TaskPlanner(
    browser_headless=config.get("browser", {}).get("headless", False),
    voice_enabled=config.get("voice", {}).get("enabled", True)
)

@app.on_event("startup")
async def startup_warmup():
    import threading
    def _warmup():
        try:
            from core.custom_transformer import TransformerEngine
            TransformerEngine.get_instance()
            print("INFO:     Aaveshkar Custom Neural Transformer pre-warmed and ready.")
        except Exception as e:
            print(f"INFO:     Transformer initialization note: {e}")
    threading.Thread(target=_warmup, daemon=True).start()

class TaskRequest(BaseModel):
    command: str

@app.get("/", response_class=HTMLResponse)
async def index():
    template_path = os.path.join(os.path.dirname(__file__), "templates", "index.html")
    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()

@app.post("/api/task")
async def execute_task_endpoint(req: TaskRequest):
    try:
        result = await planner.execute_task(req.command)
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(content={"status": "error", "error": str(e)}, status_code=500)

@app.get("/api/stats")
async def get_system_stats():
    try:
        return JSONResponse(content=SystemExecutor.get_system_stats())
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

class TransformerRequest(BaseModel):
    prompt: str
    use_search_source: Optional[bool] = True

@app.post("/api/transformer")
async def transformer_endpoint(req: TransformerRequest):
    try:
        from core.custom_transformer import TransformerEngine
        engine = TransformerEngine.get_instance()
        res = engine.generate_answer(req.prompt, use_search_source=req.use_search_source)
        return JSONResponse(content=res)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/api/transformer")
async def transformer_get_endpoint(prompt: str = Query(..., description="The query prompt to ask the Transformer")):
    try:
        from core.custom_transformer import TransformerEngine
        engine = TransformerEngine.get_instance()
        res = engine.generate_answer(prompt)
        return JSONResponse(content=res)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

class PipelineRequest(BaseModel):
    query: str
    use_search: Optional[bool] = True

@app.post("/api/pipeline")
async def pipeline_endpoint(req: PipelineRequest):
    """
    Unified 5-Stage AI Search & Transformer Inference Pipeline:
    1. Query Intent Refinement (Topic Grounding)
    2. Multi-Source Web Retrieval (Google CSE, Wikipedia, DuckDuckGo, News)
    3. Disambiguation & Noise Filtering (Songs, Missiles, Commercial Brands)
    4. Neural Transformer Re-ranking (Cross-Attention Embeddings)
    5. Cognitive Synthesis (ChatGPT/Gemini Structure & Citations)
    """
    try:
        from core.ai_pipeline import AIPipeline
        pipeline = AIPipeline()
        res = pipeline.run(req.query, use_search=req.use_search)
        return JSONResponse(content=res)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/api/pipeline")
async def pipeline_get_endpoint(query: str = Query(..., description="User query to process through the 5-stage pipeline")):
    try:
        from core.ai_pipeline import AIPipeline
        pipeline = AIPipeline()
        res = pipeline.run(query, use_search=True)
        return JSONResponse(content=res)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

class QueryImprovementRequest(BaseModel):
    query: str

@app.post("/api/query/improve")
async def improve_query_endpoint(req: QueryImprovementRequest):
    """
    Direct endpoint for Search Query Improvement Pipeline (SQIP):
    1. Lexical Normalization & Contraction Expansion
    2. Typo Detection & Phonetic Spell-Correction
    3. Intent Classification & Entity Extraction
    4. Query Rewriting, Acronym Expansion & Disambiguation
    5. Search Engine Optimization & Engine Adapters
    """
    try:
        from core.query_pipeline import SearchQueryPipeline
        res = SearchQueryPipeline.improve_query(req.query)
        return JSONResponse(content=res)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/api/query/improve")
async def improve_query_get_endpoint(query: str = Query(..., description="Query to improve")):
    try:
        from core.query_pipeline import SearchQueryPipeline
        res = SearchQueryPipeline.improve_query(query)
        return JSONResponse(content=res)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/api/config")
async def get_config_endpoint():
    """Returns application configuration with masked secrets."""
    cfg = load_app_config()
    safe_cfg = json.loads(json.dumps(cfg))
    
    # Mask API keys for security
    google_sec = safe_cfg.get("google", {})
    if google_sec.get("search_api_key"):
        google_sec["search_api_key"] = google_sec["search_api_key"][:4] + "..." + google_sec["search_api_key"][-4:]
    if google_sec.get("api_key"):
        google_sec["api_key"] = google_sec["api_key"][:4] + "..." + google_sec["api_key"][-4:]
    
    safe_cfg["has_google_search_api"] = bool(cfg.get("google", {}).get("search_api_key"))
    safe_cfg["has_google_gemini_api"] = bool(cfg.get("google", {}).get("api_key") or cfg.get("llm", {}).get("google_api_key"))
    return JSONResponse(content=safe_cfg)

class ConfigUpdateRequest(BaseModel):
    google_search_api_key: Optional[str] = None
    google_search_cx: Optional[str] = None
    google_api_key: Optional[str] = None
    voice_enabled: Optional[bool] = None

@app.post("/api/config")
async def update_config_endpoint(req: ConfigUpdateRequest):
    """Allows updating Google API keys and preferences dynamically."""
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    cfg = load_app_config()

    if "google" not in cfg:
        cfg["google"] = {}

    if req.google_search_api_key is not None:
        cfg["google"]["search_api_key"] = req.google_search_api_key
    if req.google_search_cx is not None:
        cfg["google"]["search_cx"] = req.google_search_cx
    if req.google_api_key is not None:
        cfg["google"]["api_key"] = req.google_api_key
        if "llm" in cfg:
            cfg["llm"]["google_api_key"] = req.google_api_key

    if req.voice_enabled is not None:
        if "voice" not in cfg:
            cfg["voice"] = {}
        cfg["voice"]["enabled"] = req.voice_enabled
        if planner:
            planner.voice_enabled = req.voice_enabled

    try:
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=4)
        return JSONResponse(content={"success": True, "message": "Configuration saved successfully."})
    except Exception as e:
        return JSONResponse(content={"success": False, "error": str(e)}, status_code=500)

if __name__ == "__main__":
    import uvicorn
    host = config.get("server", {}).get("host", "127.0.0.1")
    port = config.get("server", {}).get("port", 8765)
    uvicorn.run("main:app", host=host, port=port, reload=False)
