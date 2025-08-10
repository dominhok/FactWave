# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**FactWave** is a Multi-Agent-Based Fact-check Solution that uses multiple AI agents to verify information from different perspectives and logic. The system consists of a React frontend (Chrome Extension), FastAPI backend with WebSocket support, and a Python-based AI system using CrewAI framework.

### Core Concept
- Users input statements to fact-check
- 5 specialized AI agents analyze from different angles
- Real-time WebSocket communication provides streaming results
- Transparent verification process with sources and confidence scores
- Chrome Extension for easy accessibility

## System Architecture

### Frontend (React + Vite)
- **Framework**: React 19 + Vite
- **Target**: Chrome Extension implementation
- **Features**: Real-time results display, WebSocket integration
- **Design**: Located in `src/assets/frontend_design/` (input_screen.png, init_screen.png)

### Backend 
- **Framework**: FastAPI with WebSocket support
- **Role**: Bridge between frontend and AI system
- **Communication**: WebSocket for real-time streaming of agent results

### AI System (`FactWave-AI/`)
- **Framework**: CrewAI with Solar-pro2 LLM
- **Agents**: 5 specialized fact-checking agents
- **Process**: 3-phase analysis (Initial → Debate → Synthesis)

## AI Agent System

### Agent Roles & Weights
1. **Academic Agent (30%)**: Academic papers, government statistics, official data
2. **News Agent (35%)**: News verification, media bias analysis, cross-referencing
3. **Logic Agent (20%)**: Logical consistency, causal relationships
4. **Social Agent (15%)**: Social media trends, community discussions
5. **Super Agent**: Final synthesis and confidence scoring

### Processing Flow
1. **Initial Analysis**: All 4 agents analyze the statement independently
2. **Debate Phase**: Agents review and discuss each other's findings
3. **Final Synthesis**: Super Agent combines results with confidence matrix

## Common Commands

### Frontend Development
- `npm run dev` - Start React development server
- `npm run build` - Build for production
- `npm run lint` - Run ESLint

### AI System (FactWave-AI/)
- `python factwave_prototype.py` - Run the fact-checking prototype
- Setup requires: UPSTAGE_API_KEY environment variable

### Project Management
- `npm install` - Install frontend dependencies
- Configuration files: `agents_config.yaml` for AI agent settings

## Key Files & Structure

```
factwave/
├── src/                          # React frontend
│   ├── App.jsx                   # Main component
│   └── assets/frontend_design/   # UI mockups
├── FactWave-AI/                  # AI system
│   ├── factwave_prototype.py     # Main AI orchestrator
│   ├── agents_config.yaml        # Agent configurations
│   └── PRD.md                    # Detailed technical specs
├── project_description.txt       # Project specifications
└── CLAUDE.md                     # This file
```

## Development Context

### Current State
- Basic React + Vite setup for Chrome Extension
- Complete AI prototype with 5-agent system
- WebSocket architecture planned for real-time communication

### Implementation Goals
- Chrome Extension for easy access while browsing
- Real-time streaming of fact-check results
- Visual representation of agent analysis process
- Support for Korean language fact-checking

### Technical Stack
- **Frontend**: React 19, Vite, Chrome Extension APIs
- **Backend**: FastAPI, WebSocket, Python
- **AI**: CrewAI, Solar-pro2 LLM, Upstage API
- **Data Sources**: Academic APIs, News APIs, Social media analysis

## Development Notes

- Project uses ES modules (`"type": "module"`)
- AI system requires UPSTAGE_API_KEY for Solar-pro2 access
- Frontend designed for Chrome Extension deployment
- Real-time communication architecture for streaming results
- Multi-language support (Korean primary, English secondary)