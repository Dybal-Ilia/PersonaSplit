# 🎭 PersonaSplit - AI Multi-Persona Debate Platform

[![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![LangGraph](https://img.shields.io/badge/LangGraph-1.0+-orange.svg)](https://github.com/langchain-ai/langgraph)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)

**PersonaSplit** is an advanced AI-powered Telegram bot that orchestrates multi-agent debates using distinct AI personas. Built with LangGraph and powered by Groq's LLaMA models, it creates dynamic, context-aware conversations where different AI personalities discuss topics from various perspectives.

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Personas & Presets](#-personas--presets)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Development](#-development)
- [Project Structure](#-project-structure)
- [Technologies](#-technologies)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🌟 Overview

PersonaSplit transforms single-perspective AI conversations into rich, multi-viewpoint debates. Each persona represents a distinct thinking style (rational, empathetic, skeptical, pragmatic, etc.) and engages in structured discussions moderated by an intelligent orchestrator and concluded by an impartial judge.

### What Makes PersonaSplit Unique?

- **🧠 Multi-Agent Architecture**: Powered by LangGraph state machines
- **💾 Contextual Memory**: PostgreSQL + pgvector for semantic conversation history
- **🎯 Preset Configurations**: Pre-configured persona combinations for different debate contexts
- **🔄 Dynamic Orchestration**: Smart turn-taking and debate flow management
- **⚡ Real-time Streaming**: Live debate updates via Telegram
- **🐳 Production Ready**: Fully containerized with Docker Compose

---

## ✨ Key Features

### Core Capabilities

- **Multiple AI Personas**: 13 distinct personalities (Rationalist, Humanist, Cynic, Scientist, Philosopher, etc.)
- **Preset Debate Modes**: 8 pre-configured debate scenarios (Scientific, Moral, Social, Future, Eco, Philosophical, Creative, Classic)
- **Intelligent Orchestration**: AI-powered moderator manages turn-taking and debate flow
- **Semantic Memory**: Vector-based memory storage for contextual argument tracking
- **Judge System**: Impartial AI judge evaluates arguments and provides summaries
- **Multilingual Support**: Responds in the user's query language
- **Concurrency Safe**: Async-first design with proper state management

### Technical Features

- **State Machine Design**: Built on LangGraph's StateGraph framework
- **Vector Search**: pgvector + HuggingFace embeddings for semantic similarity
- **Streaming Responses**: Real-time debate updates via Aiogram
- **Docker Deployment**: Complete containerization with health checks
- **Configuration-Driven**: YAML-based persona and preset definitions
- **Extensible**: Easy to add new personas and debate modes

---

### Agent Types

1. **Orchestrator**: Analyzes conversation flow and selects next speaker
2. **Personas**: Individual debate participants with unique perspectives
3. **Judge**: Evaluates all arguments and provides final summary

### State Management

```python
class ChatState(BaseModel):
    topic: str                    # Debate topic
    debators: list[str]           # Active persona names
    session_id: str               # Unique conversation ID
    history_patch: AIMessage      # Latest message
    last_speaker: str             # Previous speaker name
    next_speaker: str             # Next speaker to engage
    judge_decision: AIMessage     # Final verdict
    replices_counter: int         # Turn counter (max 10)
```

---

## 🎭 Personas & Presets

### Available Personas

| Persona | Description | Style |
|---------|-------------|-------|
| **Rationalist** | Logic and data-driven analyst | Formal, precise, evidence-based |
| **Humanist** | Empathetic advocate for human values | Warm, compassionate, ethical |
| **Pragmatic** | Practical realist focused on feasibility | Businesslike, results-oriented |
| **Cynic** | Skeptical critic of assumptions | Witty, ironic, sharp |
| **Scientist** | Empirical researcher | Neutral, data-driven, methodical |
| **Philosopher** | Abstract conceptual thinker | Reflective, deep, introspective |
| **Populist** | Voice of common people | Charismatic, relatable, plain-spoken |
| **Visionary** | Future-oriented innovator | Inspiring, optimistic, bold |
| **Lawyer** | Legal and logical arguer | Assertive, structured, precise |
| **Ecologist** | Environmental advocate | Passionate, sustainability-focused |
| **Provocateur** | Convention challenger | Bold, contrarian, creative |
| **Artist** | Creative and expressive voice | Poetic, metaphorical, emotional |

### Debate Presets

| Preset | Personas | Best For |
|--------|----------|----------|
| **classic** | rationalist, humanist, pragmatic | General balanced debates |
| **scientific** | scientist, rationalist, lawyer, pragmatic | Technical and research topics |
| **moral** | humanist, lawyer, philosopher, cynic | Ethical dilemmas |
| **social** | populist, rationalist, cynic, pragmatic | Social issues and policy |
| **future** | visionary, scientist, rationalist, cynic | Technology and innovation |
| **eco** | ecologist, pragmatic, scientist, humanist | Environmental topics |
| **philosophical** | philosopher, humanist, cynic, artist | Abstract concepts |
| **creative** | artist, provocateur, rationalist, humanist | Creative and cultural topics |

---

## 🚀 Installation

### Prerequisites

- Python 3.12 or higher
- Docker and Docker Compose (for containerized deployment)
- PostgreSQL 16 with pgvector extension (or use provided Docker setup)
- Telegram Bot Token ([create via BotFather](https://t.me/botfather))
- Groq API Key ([get from Groq](https://console.groq.com/))

### Option 1: Docker Compose (Recommended)

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/PersonaSplit.git
cd PersonaSplit
```

2. **Create environment file**
```bash
# Create .env file in project root
cat > .env << EOF
# Telegram Bot Configuration
BOT_TOKEN=your_telegram_bot_token_here

# Groq API Configuration
GROQ_API_KEY=your_groq_api_key_here

# PostgreSQL Configuration
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=personasplit
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# Memory Configuration
TABLE_NAME=memory
VECTOR_SIZE=384

# Paths (automatically set in Docker)
PROMPTS_PATH=/app/src/core/prompts/prompts.yaml
PRESETS_PATH=/app/src/core/presets/presets.yaml
EOF
```

3. **Launch with Docker Compose**
```bash
# Development mode (with hot reload)
docker-compose up -d

# Production mode
docker-compose -f docker-compose.prod.yml up -d
```

4. **Verify deployment**
```bash
docker-compose ps
docker-compose logs -f bot
```

### Option 2: Local Development

1. **Install uv (Python package manager)**
```bash
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. **Setup Python environment**
```bash
# Create virtual environment and install dependencies
uv venv
uv sync

# Activate environment
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

3. **Setup PostgreSQL with pgvector**
```bash
# Using Docker for database only
docker run -d \
  --name personasplit-db \
  -e POSTGRES_PASSWORD=yourpassword \
  -e POSTGRES_DB=personasplit \
  -p 5432:5432 \
  pgvector/pgvector:pg16
```

4. **Configure environment**
```bash
# Copy and edit .env file
cp .env.example .env
# Edit .env with your values
```

5. **Run the bot**
```bash
python -m src.app.main
```

---

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `BOT_TOKEN` | Telegram bot token from BotFather | - | ✅ |
| `GROQ_API_KEY` | Groq API key for LLaMA models | - | ✅ |
| `POSTGRES_USER` | PostgreSQL username | `postgres` | ✅ |
| `POSTGRES_PASSWORD` | PostgreSQL password | - | ✅ |
| `POSTGRES_HOST` | Database host | `localhost` | ✅ |
| `POSTGRES_PORT` | Database port | `5432` | ✅ |
| `POSTGRES_DB` | Database name | `postgres` | ✅ |
| `TABLE_NAME` | Vector store table name | `memory` | ❌ |
| `VECTOR_SIZE` | Embedding vector dimensions | `384` | ❌ |
| `PROMPTS_PATH` | Path to prompts YAML | auto-detected | ❌ |
| `PRESETS_PATH` | Path to presets YAML | auto-detected | ❌ |

### Customizing Personas

Edit [src/core/prompts/prompts.yaml](src/core/prompts/prompts.yaml):

```yaml
your_persona:
  system_prompt: |
    "You are **Your Custom Persona**, description here.
    The topic is: *{topic}*
    
    ### Role & Objective
    - Your role details
    
    ### Debate Strategy
    - Your strategy
    
    ### Tone & Style
    - Your style
    
    ### Input Context
    - You are given: {context}
    
    ### Output Format
    - Generate concise response
    - Answer in user query language
    
    ### COMMUNICATION RULES
    1. BE CONCISE (1-2 paragraphs)
    2. Complete your thought"
```

### Creating Custom Presets

Edit [src/core/presets/presets.yaml](src/core/presets/presets.yaml):

```yaml
your_preset:
  agents: [persona1, persona2, persona3, persona4]
```

---

## 📖 Usage

### Basic Commands

#### Starting a Debate

**Method 1: Command with topic**
```
/debate Should AI replace human creativity?
```

**Method 2: Interactive preset selection**
1. Send any message (your debate topic)
2. Bot presents preset buttons
3. Select desired preset
4. Debate begins automatically

### Debate Flow

1. **Topic Submission**: User sends topic or uses `/debate` command
2. **Preset Selection**: Choose debate preset (or use default)
3. **Orchestration**: AI moderator initiates discussion
4. **Debate Rounds**: Personas exchange arguments (max 10 turns)
5. **Judgment**: Judge provides analysis and summary
6. **Completion**: Final verdict delivered to user

### Example Interaction

```
User:
"Is artificial general intelligence a threat to humanity?"

Bot:
[Presents preset buttons: scientific, moral, social, future, eco, philosophical, creative, classic]

User: [Clicks "future"]

Bot:
"Starting debate on: Is artificial general intelligence a threat to humanity? (preset: future)"

**Visionary**
Artificial general intelligence represents humanity's next evolutionary leap. Rather than viewing 
AGI as a threat, we should recognize it as a tool that amplifies human potential...

**Scientist**
From an empirical standpoint, the development of AGI requires rigorous safety frameworks. 
Current research in alignment shows that controlled development pathways exist...

**Rationalist**
Examining the probability distributions, the risk assessment must account for both existential 
threats and transformative benefits. Historical precedent suggests...

**Cynic**
How convenient that every technological revolution is sold as "amplifying human potential" until 
it automates half the workforce and concentrates power in fewer hands...

[Continues for up to 10 turns]

**Judge's Verdict**
After careful analysis of all perspectives, the strongest arguments emerge from the Scientist's 
emphasis on safety frameworks combined with the Rationalist's probability-based analysis...
```

---

## 📚 API Documentation

### Core Components

#### GraphFactory

Creates and manages the LangGraph state machine for debate orchestration.

```python
from src.core.agents.orchestration import GraphFactory
from src.core.schemas.state import ChatState

# Initialize graph with personas
graph = GraphFactory(agents_list=["rationalist", "humanist", "cynic"])
app = graph.build_graph()

# Create initial state
initial_state = ChatState(
    topic="Your debate topic",
    debators=["rationalist", "humanist", "cynic"],
    session_id="unique-session-id"
)

# Stream debate events
async for event in app.astream(initial_state, config={"recursion_limit": 100}):
    node_name, patch = list(event.items())[0]
    # Process debate updates
```

#### Agent Classes

**BaseAgent**: Abstract base class for all agents

```python
from src.core.agents.agent import BaseAgent

class BaseAgent(ABC):
    def __init__(self, name: str, model: str = "llama-3.3-70b-versatile", max_tokens: int = 300):
        self.name = name
        self.llm = ChatGroq(model=model, max_tokens=max_tokens)
        self.memory = memory_client
        
    @abstractmethod
    async def run(self, state: ChatState):
        raise NotImplementedError
```

**Persona**: Individual debate participant

```python
from src.core.agents.agent import Persona

persona = Persona(name="rationalist", model="llama-3.3-70b-versatile", max_tokens=300)
result = await persona.run(state)
# Returns: {"history_patch": AIMessage, "last_speaker": str, "replices_counter": int}
```

**Orchestrator**: Debate flow manager

```python
from src.core.agents.agent import Orchestrator

orchestrator = Orchestrator(name="orchestrator")
result = await orchestrator.run(state)
# Returns: {"next_speaker": str}  # One of: persona names or "judge"
```

**Judge**: Final evaluator

```python
from src.core.agents.agent import Judge

judge = Judge(name="judge", max_tokens=500)
result = await judge.run(state)
# Returns: {"judge_decision": AIMessage}
```

#### Memory Client

Vector-based conversation memory with semantic search.

```python
from src.core.memory_client import memory_client
from langchain_core.documents import Document

# Add to memory
await memory_client.add(
    Document(page_content="Argument text", metadata={"agent_name": "rationalist"}),
    session_id="session-123",
    agent_name="rationalist"
)

# Search memory
results = await memory_client.search(
    query="What was said about ethics?",
    session_id="session-123",
    k=5
)
# Returns: list[str] of relevant past arguments
```

### Utility Functions

#### YAML Loaders

```python
from src.utils.loaders import load_yaml

prompts = load_yaml("src/core/prompts/prompts.yaml")
presets = load_yaml("src/core/presets/presets.yaml")
```

#### Logging

```python
from src.utils.logger import logger

logger.info("Information message")
logger.warning("Warning message")
logger.error("Error message")
```

---

## 🛠️ Development

### Project Setup for Development

```bash
# Clone repository
git clone https://github.com/yourusername/PersonaSplit.git
cd PersonaSplit

# Install development dependencies
uv sync --group dev

# Activate environment
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows
```

### Code Quality Tools

```bash
# Run linter
ruff check src/

# Auto-fix issues
ruff check --fix src/

# Type checking
mypy src/

# Format code
ruff format src/
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_basic.py

# Run with verbose output
pytest -v
```

### Adding New Personas

1. **Add persona prompt** in [src/core/prompts/prompts.yaml](src/core/prompts/prompts.yaml)
2. **Update presets** in [src/core/presets/presets.yaml](src/core/presets/presets.yaml)
3. **No code changes needed** - system automatically loads new personas

### Debugging

```python
# Enable debug logging
import logging
logging.getLogger("src").setLevel(logging.DEBUG)

# Check memory contents
from src.core.memory_client import memory_client
results = await memory_client.search(query="", session_id="your-session", k=100)
```

---

## 📁 Project Structure

```
PersonaSplit/
├── src/
│   ├── __init__.py
│   ├── app/
│   │   ├── __init__.py
│   │   └── main.py                    # Telegram bot entry point
│   ├── core/
│   │   ├── __init__.py
│   │   ├── memory_client.py           # Vector memory management
│   │   ├── agents/
│   │   │   ├── __init__.py
│   │   │   ├── agent.py               # Agent base classes & implementations
│   │   │   └── orchestration.py       # LangGraph state machine
│   │   ├── presets/
│   │   │   └── presets.yaml           # Persona combination presets
│   │   ├── prompts/
│   │   │   └── prompts.yaml           # Persona system prompts
│   │   └── schemas/
│   │       ├── __init__.py
│   │       └── state.py               # Pydantic state models
│   └── utils/
│       ├── __init__.py
│       ├── loaders.py                 # YAML configuration loaders
│       └── logger.py                  # Logging configuration
├── tests/
│   ├── __init__.py
│   └── test_basic.py                  # Test suite
├── docker-compose.yml                 # Development Docker setup
├── docker-compose.prod.yml            # Production Docker setup
├── Dockerfile                         # Multi-stage container build
├── pyproject.toml                     # Python project configuration
├── uv.lock                            # Locked dependencies
├── .env                               # Environment variables (create this)
└── README.md                          # This file
```

### Key Directories

- **`src/app/`**: Telegram bot interface and user interaction
- **`src/core/agents/`**: AI agent implementations and orchestration
- **`src/core/prompts/`**: Persona definitions and system prompts
- **`src/core/presets/`**: Pre-configured debate scenarios
- **`src/core/schemas/`**: Data models and type definitions
- **`src/utils/`**: Helper functions and utilities

---

## 🔧 Technologies

### Core Framework
- **[Python 3.12+](https://www.python.org/)** - Modern Python with enhanced type hints
- **[LangGraph 1.0+](https://github.com/langchain-ai/langgraph)** - State machine orchestration
- **[LangChain 1.0+](https://github.com/langchain-ai/langchain)** - LLM application framework

### AI & ML
- **[Groq](https://groq.com/)** - Ultra-fast LLM inference
- **[LLaMA 3.3 70B](https://ai.meta.com/llama/)** - Meta's large language model
- **[HuggingFace Transformers](https://huggingface.co/docs/transformers/)** - Model loading
- **[Sentence Transformers](https://www.sbert.net/)** - Text embeddings (all-MiniLM-L6-v2)

### Data & Storage
- **[PostgreSQL 16](https://www.postgresql.org/)** - Relational database
- **[pgvector](https://github.com/pgvector/pgvector)** - Vector similarity search
- **[SQLAlchemy 2.0](https://www.sqlalchemy.org/)** - Database ORM

### Bot Framework
- **[Aiogram 3.x](https://docs.aiogram.dev/)** - Async Telegram Bot API framework

### Development Tools
- **[uv](https://github.com/astral-sh/uv)** - Fast Python package manager
- **[Ruff](https://github.com/astral-sh/ruff)** - Lightning-fast linter & formatter
- **[mypy](https://mypy.readthedocs.io/)** - Static type checker
- **[pytest](https://pytest.org/)** - Testing framework
- **[Docker](https://www.docker.com/)** - Containerization
- **[Pydantic 2.x](https://docs.pydantic.dev/)** - Data validation

---

## 🐛 Troubleshooting

### Common Issues

#### Bot Not Responding

**Problem**: Bot doesn't reply to messages

**Solutions**:
```bash
# Check bot logs
docker-compose logs -f bot

# Verify bot token
echo $BOT_TOKEN

# Test bot connectivity
curl https://api.telegram.org/bot${BOT_TOKEN}/getMe

# Restart bot
docker-compose restart bot
```

#### Database Connection Errors

**Problem**: `connection to server failed`

**Solutions**:
```bash
# Check PostgreSQL status
docker-compose ps postgres

# View database logs
docker-compose logs postgres

# Verify connection string
echo $POSTGRES_HOST $POSTGRES_PORT

# Wait for database health check
docker-compose up -d --wait
```

#### Memory Search Failures

**Problem**: `Memory search failed` warnings in logs

**Solutions**:
```bash
# Check pgvector extension
docker-compose exec postgres psql -U postgres -d personasplit -c "SELECT * FROM pg_extension WHERE extname='vector';"

# Verify table exists
docker-compose exec postgres psql -U postgres -d personasplit -c "\dt"

# Check vector store initialization
docker-compose logs bot | grep "vectorstore"
```

#### Groq API Errors

**Problem**: `API key not found` or rate limit errors

**Solutions**:
```bash
# Verify API key is set
echo $GROQ_API_KEY

# Check API quota
# Visit: https://console.groq.com/

# Test API directly
curl https://api.groq.com/openai/v1/models \
  -H "Authorization: Bearer $GROQ_API_KEY"
```

#### Docker Build Issues

**Problem**: Build fails or takes too long

**Solutions**:
```bash
# Clean build
docker-compose down -v
docker-compose build --no-cache

# Check disk space
docker system df

# Prune unused resources
docker system prune -a
```

### Debug Mode

Enable detailed logging:

```yaml
# docker-compose.yml
services:
  bot:
    environment:
      - LOG_LEVEL=DEBUG
```

---

## 🤝 Contributing

Contributions are welcome! Here's how to contribute:

### Getting Started

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```

3. **Make your changes**
   - Follow existing code style
   - Add tests for new features
   - Update documentation

4. **Run quality checks**
   ```bash
   ruff check src/
   ruff format src/
   mypy src/
   pytest
   ```

5. **Commit your changes**
   ```bash
   git commit -m "Add amazing feature"
   ```

6. **Push to your fork**
   ```bash
   git push origin feature/amazing-feature
   ```

7. **Open a Pull Request**

### Contribution Guidelines

- **Code Style**: Follow PEP 8 and use Ruff for formatting
- **Type Hints**: Add type hints to all functions
- **Documentation**: Update README and docstrings
- **Tests**: Write tests for new functionality
- **Commits**: Use clear, descriptive commit messages

### Ideas for Contributions

- 🎭 New persona types
- 🌍 Multi-language support improvements
- 📊 Analytics and debate statistics
- 🎨 Enhanced UI/UX for Telegram
- 🔌 Alternative LLM provider support
- 📝 More debate presets
- 🧪 Additional test coverage

---

## 🙏 Acknowledgments

- **[LangChain](https://github.com/langchain-ai/langchain)** for the amazing LLM framework
- **[Groq](https://groq.com/)** for ultra-fast LLM inference
- **[Meta AI](https://ai.meta.com/)** for the LLaMA models
- **[Aiogram](https://github.com/aiogram/aiogram)** for the excellent Telegram bot framework
- All contributors and users of PersonaSplit

---


## 🗺️ Roadmap

### Version 1.0 (Current)
- ✅ Multi-agent debate system
- ✅ 13 distinct personas
- ✅ 8 debate presets
- ✅ Vector memory integration
- ✅ Docker deployment

### Version 1.1 (Planned)
- [ ] Web interface
- [ ] Debate analytics dashboard
- [ ] Custom persona builder
- [ ] Export debate transcripts
- [ ] Voice message support

### Version 2.0 (Future)
- [ ] Multi-platform support (Discord, Slack)
- [ ] Real-time collaboration
- [ ] Advanced memory strategies
- [ ] Fine-tuned persona models
- [ ] API for external integrations

---

<div align="center">

**Built with ❤️ using LangGraph and LLaMA**

⭐ Star this repo if you find it useful!

[Report Bug](https://github.com/Dybal-Ilia/PersonaSplit/issues) · [Request Feature](https://github.com/Dybal-Ilia/PersonaSplit/issues) · [Documentation](https://github.com/Dybal-Ilia/PersonaSplit/wiki)

</div>