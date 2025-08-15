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
uv run python test_integrated.py tools  # Test individual tools
uv run python test_integrated.py crew   # Test full system

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
   - Academic Agent (25% weight): Scholarly sources via Semantic Scholar, ArXiv, Wikipedia
   - News Agent (30% weight): Media verification via Naver News, NewsAPI
   - Statistics Agent (20% weight): Government data via KOSIS, FRED, World Bank
   - Logic Agent (15% weight): Logical consistency analysis (no external tools)
   - Social Agent (10% weight): Social trends via YouTube Data API

2. **Stage 2: Structured Debate** - Agents review findings and debate without tool access

3. **Stage 3: Final Synthesis** - Super Agent creates weighted confidence matrix and final verdict

### Key Architectural Components

**Agent System (`app/agents/`)**
- All agents inherit from `FactWaveAgent` base class
- Lazy initialization after tool injection
- Structured output formats for consistency

**Research Tools (`app/services/tools/`)**
- 14+ specialized research tools with error handling and rate limiting
- Caching: academic (1hr), news (30min), social (15min)
- API keys managed via environment variables

**RAG System (`owid_enhanced_vectordb/`)**
- ChromaDB vector database with 40+ pre-indexed OWID datasets
- Hybrid retrieval: vector similarity + BM25 ranking
- Metadata filtering for precise data retrieval

**Real-Time Streaming**
- WebSocket support for progressive results
- Tool call tracking and progress updates
- REST API fallback with 10-second timeout

### API Configuration

Required in `.env`:
- `UPSTAGE_API_KEY` - Primary LLM (Solar-pro2)
- `NAVER_CLIENT_ID` and `NAVER_CLIENT_SECRET` - News search

Optional APIs for enhanced functionality:
- NewsAPI, Google Fact Check, FRED, KOSIS, YouTube Data API
- Anthropic/OpenAI as fallback LLMs

### Important Patterns

**Tool Integration**: Each tool extends base classes with comprehensive error handling. Check `app/services/tools/base_tool.py` for the interface.

**Agent Communication**: Agents communicate through structured CrewAI tasks. Stage outputs are strictly typed dictionaries.

**Vector Database**: Pre-built index in `owid_enhanced_vectordb/`. Rebuild with `python -m app.services.tools.owid_enhanced_rag --rebuild` if needed.

**Caching**: Redis-based caching configured in `.env`. Falls back to in-memory if Redis unavailable.

## Development Notes

- Primary development on `AI` branch, frontend on `FrontEnd` branch
- Python 3.12+ required for AI system
- Use UV package manager for faster dependency resolution
- All agents must implement `analyze()`, `debate()`, and return structured outputs
- Tool failures should gracefully degrade, not crash the system
- Korean language processing is primary, English secondary