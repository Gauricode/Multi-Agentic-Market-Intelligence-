from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .cli import run_pipeline


class RunAgentRequest(BaseModel):
    search_keyword: str
    competitors: str
    keywords: str


def _read_text_if_exists(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8").strip()


app = FastAPI(title="AgentAI Market Intelligence API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/run-agent")
def run_agent(payload: RunAgentRequest) -> dict[str, Any]:
    base_dir = Path(__file__).resolve().parent

    try:
        result = run_pipeline(
            payload.search_keyword.strip(),
            payload.competitors.strip(),
            payload.keywords.strip(),
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {
        "message": result,
        "report": _read_text_if_exists(base_dir / "final_report.md"),
        "summary": _read_text_if_exists(base_dir / "summary.md"),
        "alerts": _read_text_if_exists(base_dir / "alerts.json"),
        "insights": _read_text_if_exists(base_dir / "insights.json"),
    }
