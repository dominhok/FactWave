# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FactWave is an AI-powered multi-agent fact-checking system using CrewAI orchestration with 5 specialized agents that verify information through a 3-stage collaborative process. Primary language is Korean with multilingual support.

## Common Development Commands

### Setup and Run
```bash
# Install backend dependencies
cd backend && uv pip install -e .  # or pip install -e .

# Configure environment
cp backend/.env.example backend/.env  # Add required API keys

# Run backend applications
cd backend && uv run python main.py              # Main CLI interface
cd backend && uv run python -m app.api.server    # FastAPI WebSocket server (port 8000)
cd backend && uv run python test_websocket_client.py  # Test WebSocket connectivity

# Frontend development
cd frontend && npm install          # Install frontend dependencies
cd frontend && npm run dev           # Vite dev server (port 5173)
cd frontend && npm run build         # Build for production
cd frontend && npm run build:watch   # Build with watch mode

# Code quality
cd backend && ruff check .    # Run linting
cd backend && ruff format .   # Format code
```

### Testing Commands
```bash
# Test WebSocket client
cd backend && python test_websocket_client.py

# Test specific tools individually
cd backend && python test_tavily.py
cd backend && python test_tool_usage.py

# Run unit tests
cd backend && python -m pytest tests/
```

## High-Level Architecture

### 3-Stage Fact-Checking Process

1. **Stage 1: Independent Analysis** - 5 agents analyze the statement using specialized tools:
   - Academic Agent (25% weight): Scholarly sources via OpenAlex, ArXiv, Wikipedia, Tavily
   - News Agent (30% weight): Media verification via Naver News, NewsAPI, Google Fact Check
   - Statistics Agent (20% weight): Government data via KOSIS, FRED, World Bank, OWID RAG
   - Logic Agent (15% weight): Logical consistency analysis (no external tools)
   - Social Agent (10% weight): Social trends via Twitter API (twscrape)

2. **Stage 2: Structured Debate** - Agents review findings and debate without tool access

3. **Stage 3: Final Synthesis** - Super Agent creates weighted confidence matrix and final verdict

### Key Architectural Components

**Centralized Prompt Management (`app/config/prompts.yaml`)**
- All agent prompts managed in single YAML file
- Step-specific templates with minimal markdown formatting
- Verdict options and agent weights centrally configured
- PromptLoader class for dynamic prompt generation without restart

**Agent System (`app/agents/`)**
- All agents inherit from `FactWaveAgent` base class
- Step-specific LLM configuration via `llm_config.py` (GPT-4.1-mini for all steps)
- Task-level callbacks for real-time progress tracking
- Structured output formats optimized for frontend display

**Research Tools (`app/services/tools/`)**
- 10+ specialized research tools organized by domain:
  - `academic/`: ArXiv, OpenAlex, Wikipedia, Tavily
  - `news/`: Naver News, NewsAPI, Google Fact Check
  - `statistics/`: KOSIS, FRED, World Bank, OWID RAG
  - `community/`: Twitter integration (twscrape)
- Tool-specific caching strategies: academic (72hrs), news (1hr), social (30min)
- HTTP retry logic with exponential backoff
- All tools extend `EnhancedBaseTool` with caching and retry mechanisms

**RAG System (`owid_enhanced_vectordb/`)**
- ChromaDB vector database with 40+ pre-indexed OWID datasets
- Hybrid retrieval: vector similarity + BM25 ranking
- Metadata filtering for precise data retrieval
- Rebuild with `cd backend && python -m build_owid_index`

**Real-Time Streaming (`app/api/`, `app/core/streaming_crew.py`)**
- FastAPI WebSocket server at `ws://localhost:8000/ws/{session_id}`
- Event-based task tracking using CrewAI Task `callback` field (not `callbacks`)
- Async/sync callback bridging through complex threading pattern
- Message types: `task_started`, `task_completed`, `agent_analysis`, `tool_call`, `final_result`
- Real-time progress updates with Rich console integration

**Frontend (`frontend/src/`)**
- React 19.1.0 + Vite Chrome Extension (450x600px side panel)
- Manifest V3 with service worker architecture
- Real-time WebSocket connection to backend API
- Tab-based UI: 토론 (Discussion), 결과보기 (Results), 라이브러리 (Library)
- Components: `Discussion.jsx`, `Results.jsx`, `Library.jsx`

### API Configuration

Required in `.env`:
- `UPSTAGE_API_KEY` - Primary LLM (Solar-pro2)
- `NAVER_CLIENT_ID` and `NAVER_CLIENT_SECRET` - Korean news search

Optional APIs for enhanced functionality:
- `NEWSAPI_KEY` - International news
- `GOOGLE_API_KEY` - Google Fact Check
- `FRED_API_KEY` - Federal Reserve Economic Data
- `KOSIS_API_KEY` - Korean Statistical Information Service
- `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` - Fallback LLMs

### Important Patterns

**Hybrid Async/Sync Pattern**: Complex bridging between CrewAI's synchronous execution and WebSocket's asynchronous requirements through thread management in `streaming_crew.py`.

**Domain-Driven Tool Organization**: Tools organized by expertise domain (`academic/`, `news/`, `statistics/`, `community/`) rather than technical implementation.

**Prompt Hot-Reloading**: Prompts can be modified in YAML without system restart. PromptLoader dynamically loads changes.

**Graceful Degradation**: Tool failures don't crash the system. Each tool has error handling with fallback strategies.

**Task Callback Management**: Use `callback` field (singular) on CrewAI Tasks. StreamingFactWaveCrew handles async/sync bridging.

**Tool Caching Strategy**: MD5-based cache keys with tool-specific TTL. Cache stored in `.cache/` directory.

**WebSocket Protocol**:
```javascript
// Client -> Server
{"action": "start", "statement": "검증할 문장"}

// Server -> Client
{
  "type": "task_started|task_completed|agent_analysis|tool_call|final_result",
  "step": "step1|step2|step3",
  "agent": "academic|news|logic|social|statistics|super",
  "content": {...},
  "timestamp": "ISO 8601"
}
```

### Development Workflow

**Backend Development**:
1. Start server: `cd backend && uv run python -m app.api.server`
2. Monitor logs with Rich console output
3. Test WebSocket: `cd backend && python test_websocket_client.py`

**Frontend Development**:
1. Start backend first (port 8000)
2. Start frontend: `cd frontend && npm run dev` (port 5173)
3. Load extension in Chrome: chrome://extensions/ → Load unpacked → Select `frontend/dist`

**Prompt Modification**:
1. Edit `backend/app/config/prompts.yaml`
2. Changes take effect immediately (no restart)
3. Test with WebSocket client or frontend

**Tool Development**:
1. Create new tool in appropriate domain directory
2. Extend `EnhancedBaseTool` from `base_tool.py`
3. Implement `_run` method with Pydantic schemas
4. Add caching strategy and error handling

## Critical Implementation Details

**LLM Configuration**: All agents use GPT-4.1-mini via `app/utils/llm_config.py`. Step-specific configuration with temperature and max_tokens settings.

**CrewAI Task Dependencies**: Step 2 agents receive Step 1 outputs as context. Step 3 synthesizes all previous outputs with weighted scoring.

**Rich Console Integration**: Beautiful terminal output with progress bars, tool usage tracking, and real-time status updates.

**Thread Safety**: WebSocket callbacks use thread-local storage and queue management for safe async/sync communication.

**Rate Limiting**: Decorator-based rate limiting for APIs with configurable intervals (e.g., Semantic Scholar: 1 req/sec).

**Testing Strategy**: Individual tool tests (`test_tavily.py`, `test_tool_usage.py`) and WebSocket client testing for integration validation.

## Development Notes

- Python 3.12+ required for AI system
- Node.js 18+ required for frontend development  
- Use UV package manager for Python dependencies (faster than pip)
- All agents follow structured output format from YAML templates
- Tool failures gracefully degrade without crashing the system
- Korean language processing is primary, English secondary
- Markdown headers (###) disabled in agent responses for cleaner UI
- Task completion detection uses CrewAI's `callback` field for immediate updates
- Cache directory (`.cache/`) can be safely deleted to force fresh API calls
- ChromaDB persistence in `owid_enhanced_vectordb/` for RAG system