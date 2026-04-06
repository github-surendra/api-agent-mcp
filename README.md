# MCP Project — Web API + Agent + MCP Server

A complete Python project demonstrating how to wire together:
- **MCP Server** — exposes tools (search, weather, calculate)
- **Agent** — uses Claude + MCP to reason and call tools
- **Web API** — FastAPI HTTP layer on top of the agent

---

## Project Structure

```
mcp_project/
├── mcp_server.py   # MCP server with tools
├── mcp_agent.py        # Agentic loop (Claude + MCP)
├── main.py      # FastAPI endpoints
├── requirements.txt
└── README.md
```

---

## Setup

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your_key_here
```

---

## Run

### 1. Start the Web API (launches agent + MCP server automatically)
```bash
python web_api.py
```
API available at: http://localhost:8000

### 2. Test the endpoints

**Analyze any query:**
```bash
curl -X POST http://localhost:8000/ai/analyze \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the weather in Tokyo and what is 12 * 15?"}'
```

**Weather shortcut:**
```bash
curl -X POST "http://localhost:8000/ai/weather?city=London"
```

**Calculate shortcut:**
```bash
curl -X POST "http://localhost:8000/ai/calculate?expression=100%20*%2025%20/%204"
```

### 3. Run agent standalone
```bash
python mcp_agent.py
```

### 4. Run MCP server standalone (stdio mode)
```bash
python mcp_server.py
```

---

## API Docs
FastAPI auto-generates docs at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## Available MCP Tools

| Tool | Description |
|------|-------------|
| `search_web` | Search the web for a query |
| `get_weather` | Get weather for a city |
| `calculate` | Evaluate a math expression |

# Start MCP Server :
uvicorn main:app --reload

# Find PID and delete of the port 8000
lsof -i :8000
kill -9 13791(PID)
 