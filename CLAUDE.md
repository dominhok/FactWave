# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FactWave is an AI-powered multi-agent fact-checking system using CrewAI orchestration with 5 specialized agents that verify information through a 3-stage collaborative process. Primary language is Korean with multilingual support.

## Common Development Commands

### Setup and Run
```bash
# Install dependencies
uv pip install -e .  # or pip install -e .

# Configure environment
cp .env.example .env  # Add required API keys

# Run applications
uv run python main.py              # Main CLI interface
uv run python -m app.api.server    # FastAPI WebSocket server (port 8000)
uv run python test_integrated.py tools  # Test individual tools
uv run python test_integrated.py crew   # Test full system

# Frontend development
npm run dev                         # Vite dev server (port 5173)
npm run build                       # Build for production

# Code quality
ruff check .    # Run linting
ruff format .   # Format code
```

### Testing Individual Components
```bash
# Test specific tools
uv run python test_integrated.py tools wikipedia
uv run python test_integrated.py tools arxiv
uv run python test_integrated.py tools naver_news

# Test agent system
uv run python test_integrated.py crew "Your fact-check statement here"
```

## High-Level Architecture

### 3-Stage Fact-Checking Process

1. **Stage 1: Independent Analysis** - 5 agents analyze the statement using specialized tools:
   - Academic Agent (25% weight): Scholarly sources via OpenAlex, ArXiv, Wikipedia
   - News Agent (30% weight): Media verification via Naver News, NewsAPI, Google Fact Check
   - Statistics Agent (20% weight): Government data via KOSIS, FRED, World Bank, OWID RAG
   - Logic Agent (15% weight): Logical consistency analysis (no external tools)
   - Social Agent (10% weight): Social trends via Twitter API

2. **Stage 2: Structured Debate** - Agents review findings and debate without tool access

3. **Stage 3: Final Synthesis** - Super Agent creates weighted confidence matrix and final verdict

### Key Architectural Components

**Centralized Prompt Management (`app/config/prompts.yaml`)**
- All agent prompts managed in single YAML file
- Step-specific templates with minimal markdown formatting
- Verdict options and agent weights centrally configured
- PromptLoader class for dynamic prompt generation

**Agent System (`app/agents/`)**
- All agents inherit from `FactWaveAgent` base class
- Streamlined backstories focused on tool usage and response principles
- Task-level callbacks for real-time progress tracking
- Structured output formats optimized for frontend display

**Research Tools (`app/services/tools/`)**
- 10+ specialized research tools organized by domain:
  - `academic/`: ArXiv, OpenAlex, Wikipedia
  - `news/`: Naver News, NewsAPI, Google Fact Check
  - `statistics/`: KOSIS, FRED, World Bank, OWID RAG
  - `community/`: Twitter integration
- All tools preserve original metadata without rule-based transformations
- Error handling and rate limiting with graceful degradation

**RAG System (`owid_enhanced_vectordb/`)**
- ChromaDB vector database with 40+ pre-indexed OWID datasets
- Hybrid retrieval: vector similarity + BM25 ranking
- Metadata filtering for precise data retrieval
- Rebuild with `python -m app.services.tools.owid_enhanced_rag --rebuild`

**Real-Time Streaming (`app/api/`, `app/core/streaming_crew.py`)**
- FastAPI WebSocket server at `ws://localhost:8000/ws/{session_id}`
- Event-based task tracking using CrewAI Task `callback` field (not `callbacks`)
- Progressive agent results and tool call tracking
- Message types: `task_started`, `task_completed`, `agent_start`, `tool_call`, `final_result`
- Async/sync callback bridging for CrewAI integration

**Frontend (`src/`)**
- React 19.1.0 + Vite Chrome Extension (450x600px popup)
- Real-time WebSocket connection to backend API
- Agent cards with streamlined content display
- Tab-based UI: 토론, 결과보기, 라이브러리

### API Configuration

Required in `.env`:
- `UPSTAGE_API_KEY` - Primary LLM (Solar-pro2)
- `NAVER_CLIENT_ID` and `NAVER_CLIENT_SECRET` - News search

Optional APIs for enhanced functionality:
- NewsAPI, Google Fact Check, FRED, KOSIS, YouTube Data API
- Anthropic/OpenAI as fallback LLMs

### Important Patterns

**Prompt Engineering**: All prompts are centrally managed in `app/config/prompts.yaml`. Use `PromptLoader` class to access and modify prompts. Markdown formatting is disabled for cleaner frontend display.

**Tool Integration**: Each tool extends `base_tool.py` interface. All tools preserve original API metadata without transformations. LLM performs all analysis and formatting.

**Task Callbacks**: Use `callback` field (singular) on CrewAI Tasks for real-time updates. StreamingFactWaveCrew handles async/sync bridging.

**Agent Communication**: Agents communicate through structured CrewAI tasks. Stage outputs use simplified templates from YAML configuration.

**Vector Database**: Pre-built OWID index in `owid_enhanced_vectordb/`. Contains 40+ datasets with CSV and metadata.

**Frontend-Backend Integration**: WebSocket messages use event-based architecture. Backend sends task status events immediately when tasks start/complete.

### Development Workflow

**Backend Development**:
1. Start server: `uv run python -m app.api.server`
2. Test tools: `uv run python test_integrated.py tools`
3. Test full system: `uv run python test_integrated.py crew "test statement"`

**Frontend Development**:
1. Start backend first (port 8000)
2. Start frontend: `npm run dev` (port 5173)
3. Test WebSocket: Use `test_websocket_client.py`

**Prompt Modification**:
1. Edit `app/config/prompts.yaml`
2. Test with `crew.py` or `streaming_crew.py`
3. No restart required - prompts loaded dynamically

## Development Notes

- Python 3.12+ required for AI system
- Node.js required for frontend development  
- Use UV package manager for Python dependencies
- All agents follow structured output format from YAML templates
- Tool failures gracefully degrade without crashing the system
- Korean language processing is primary, English secondary
- Markdown headers (###) are disabled in agent responses for cleaner UI
- Task completion detection uses CrewAI's `callback` field for immediate updates