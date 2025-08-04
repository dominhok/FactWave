# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
FactWave is a multi-agent fact-checking system using CrewAI framework. The system verifies claims through 5 specialized AI agents (Academic, News Verification, Social Intelligence, Logic Verification) plus a Super Agent that synthesizes results into a confidence matrix.

## Architecture Overview
- **Backend**: FastAPI with WebSocket support for real-time streaming
- **AI Framework**: CrewAI for multi-agent orchestration
- **Language Model**: Upstage solar-pro2 or Claude
- **Agent System**: 4 specialized agents + 1 super agent for consensus

## Agent Roles
1. **Academic Agent** (Weight: 0.3)
   - Verifies against academic papers, government statistics
   - APIs: Semantic Scholar, OpenAlex, ArXiv, PubMed

2. **News Verification Agent** (Weight: 0.35)
   - Cross-verifies news sources, checks media bias
   - APIs: Naver News, BigKinds, NewsAPI, Google Fact Check

3. **Social Intelligence Agent** (Weight: 0.15)
   - Analyzes social media trends and public opinion
   - APIs: YouTube Data, Discord, Telegram

4. **Logic Verification Agent** (Weight: 0.2)
   - Checks logical consistency and causal relationships
   - Pure algorithmic analysis

5. **Super Agent**
   - Synthesizes all agent outputs
   - Generates confidence matrix and final verdict

## Key Commands

### Development Setup
```bash
# Install dependencies using uv (Python 3.12+)
uv pip install -e .

# Or if uv is not installed, use pip
pip install -e .
```

### Running the Application
```bash
# Development server with auto-reload
uvicorn app.main:app --reload --ws websockets

# Production server
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Testing & Code Quality
```bash
# Run tests
pytest tests/

# Linting
ruff check .

# Format code
ruff format .

# Run a single test
pytest tests/test_specific.py::test_function_name
```

## Project Structure
```
FactWave/
├── app/
│   ├── api/           # FastAPI endpoints
│   ├── agents/        # CrewAI agent implementations
│   ├── core/          # Core utilities
│   └── services/      # External API integrations
├── tests/             # Test files
├── .env               # Environment variables
└── pyproject.toml     # Project dependencies
```

## Environment Setup
1. Copy `.env.example` to `.env`
2. Configure API keys:
   - UPSTAGE_API_KEY or ANTHROPIC_API_KEY
   - NAVER_CLIENT_ID and NAVER_CLIENT_SECRET
   - Other API keys as needed

## High-Level Architecture

### Multi-Agent System (CrewAI)
The fact-checking system operates through a 3-stage debate process:
1. **Initial Analysis**: All agents independently analyze the statement
2. **Debate Round**: Agents review each other's findings and refine positions
3. **Final Consensus**: Super Agent synthesizes all viewpoints into final verdict

### Agent Weights & Specializations
- **Academic Agent (0.3)**: Scholarly sources, government data, official statistics
- **News Verification Agent (0.35)**: Cross-references news sources, detects media bias
- **Logic Verification Agent (0.2)**: Analyzes logical consistency and causal relationships
- **Social Intelligence Agent (0.15)**: Monitors social media trends and public sentiment
- **Super Agent**: Creates confidence matrix and final verdict

### Real-time Streaming Architecture
- WebSocket connections handle real-time updates
- Each agent result streams as it completes
- Progressive enhancement: users see partial results immediately
- Fallback to REST API for quick checks (10s timeout)

## API Endpoints
- `POST /api/v1/factcheck/quick` - Quick fact check (10s timeout)
- `WS /ws/factcheck` - Real-time fact checking via WebSocket
- `GET /health` - Health check endpoint

## Caching Strategy
- Use Redis for caching search results
- Cache keys based on normalized queries
- Implement cache warming for trending topics

## Error Handling
- Graceful degradation when agents fail
- Timeout handling (10s per agent, 25s total)
- Clear error messages in API responses

## Security Considerations
- Never expose API keys in code
- Implement rate limiting
- Validate all user inputs
- Use HTTPS in production

## External API Integration
The system integrates with multiple APIs for comprehensive fact-checking:

### Academic Sources
- Semantic Scholar API (214M papers, free)
- OpenAlex API (209M papers, free)
- ArXiv, PubMed, Wikipedia APIs
- Korean government APIs (KOSIS, public data portal)

### News Verification
- Naver News API (25k requests/day)
- BigKinds (Korean news archive)
- Google Fact Check Tools API
- Guardian API (free)

### Social Monitoring
- YouTube Data API (10k units/day)
- Community APIs (Discord, Telegram)
- Korean communities via Playwright scraping

## Caching Strategy
- Redis-based caching with varying TTLs:
  - Academic data: 1 hour (papers don't change)
  - News data: 30 minutes (balance freshness/performance)
  - Social data: 15 minutes (rapidly changing)
- Cache warming for trending topics
- Deduplication of similar queries