
# TrendLens: Multi-Agent Market Intelligence System

TrendLens is a multi-agent, AI-powered market intelligence platform built using CrewAI. It automates the process of collecting, analyzing, and transforming market data into actionable insights.

The system uses a pipeline of specialized agents to gather news, filter relevant information, generate insights, detect trends, and produce structured reports.

---

## Overview

TrendLens can be used in three ways:

* As a command-line (CLI) pipeline
* As a FastAPI backend service
* Through a Next.js web dashboard

---

## Key Features

* Multi-agent workflow powered by CrewAI
* Automated news collection
* Relevance filtering and deduplication
* Text summarization
* Insight and competitor analysis
* Trend detection and alert generation
* Final report generation
* Full-stack support (CLI, API, frontend)

---

## Architecture

The system follows a sequential pipeline where each agent performs a specific role:

1. Source Collector – Fetches recent news
2. Relevance and Deduplication Specialist – Filters useful content
3. Summarization Specialist – Generates concise summaries
4. Insight Generator – Extracts key signals
5. Trend and Alert Analyst – Identifies patterns and risks
6. Report Delivery Specialist – Produces the final report

---

## Generated Outputs

All outputs are saved inside the backend directory:

```
agentai/
├── collected_sources.csv
├── filtered_sources.csv
├── summary.md
├── insights.json
├── alerts.json
└── final_report.md
```

---

## Tech Stack

Backend:

* Python
* CrewAI
* FastAPI
* OpenAI API
* News API (Massive API)

Frontend:

* Next.js
* React

---

## Environment Setup

Create a `.env` file in the project root:

```
OPENAI_API_KEY=your_openai_api_key
NEWS_API_KEY=your_massive_api_key
```

Note:

* `OPEN_API_KEY` is also supported for backward compatibility.

---

## Running the Project

### Backend Setup

```
python -m venv .venv
.venv\Scripts\activate
pip install crewai fastapi uvicorn pandas requests python-dotenv openai
```

---

### Run via CLI

```
.venv\Scripts\python.exe -m agentai.main --keyword NVDA --competitors AMD,Intel,TSMC --keywords AI,GPU,chip,datacenter
```

If arguments are not provided, the CLI will prompt for inputs.

---

### Run Backend (FastAPI)

```
.venv\Scripts\uvicorn.exe agentai.api:app --reload --host 127.0.0.1 --port 8000
```

Available endpoints:

* GET `/health`
* POST `/run-agent`

Example request:

```
{
  "search_keyword": "NVDA",
  "competitors": "AMD,Intel,TSMC",
  "keywords": "AI,GPU,chip,datacenter"
}
```

---

### Run Frontend

```
cd frontend
npm install
npm run dev
```

If needed, set:

```
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
```

Then open:

* Frontend: [http://localhost:3000](http://localhost:3000)
* Backend docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## Full Workflow

1. Start the FastAPI backend on port 8000
2. Start the Next.js frontend on port 3000
3. Open the dashboard
4. Enter a search keyword (preferably a stock ticker)
5. Add competitors and keywords
6. Run the pipeline and review the report

---

## Project Structure

```
Multi-Agentic-Market-Intelligence-/
│
├── agentai/
│   ├── agents.py
│   ├── tasks.py
│   ├── tools.py
│   ├── cli.py
│   ├── api.py
│   ├── config.py
│   └── main.py
│
└── frontend/
```

---

## How It Works

* `agents.py` defines the agent roles
* `tasks.py` connects agents into a workflow
* `tools.py` handles data processing and logic
* `cli.py` provides command-line execution
* `api.py` exposes the pipeline through FastAPI

---

## Example Input

```
Search keyword: NVDA
Competitors: AMD, Intel, TSMC
Keywords: AI, GPU, datacenter, semiconductor
```

---
