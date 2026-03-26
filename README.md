<<<<<<< HEAD
# interviewPrepADK
=======
# interview-agent

Local, voice-interactive interview preparation assistant built with a planner-executor architecture, ADK-style tool registration, local Ollama (`llama3.1:70b`), local Whisper transcription, and local sentence-transformers retrieval.

No external API calls are required in the runtime flow.

## What this project does

- Loads a resume from a plain text file at runtime.
- Accepts pasted job description text at runtime.
- Generates tailored interview questions across:
  - technical
  - behavioral
  - role-specific
- Captures spoken answers from the microphone and transcribes locally with Whisper.
- Evaluates each answer on:
  - relevance
  - specificity
  - STAR format
- Provides a model answer on demand.
- Produces end-of-session readiness scoring with top improvement areas.

## Architecture

### Planner-executor flow

- `planner.py` decides the next action from current conversation/session state.
- `executor.py` invokes tools and state transitions for that action.
- `session.py` connects planner and executor behind a simple `step()` method.

This keeps decision logic separate from tool execution, which makes iteration and testing easier.

### Tooling model (ADK-style)

- `adk_runtime.py` contains the tool registry and decorator (`@adk_tool`).
- Tools are implemented in `tools/` and registered by name:
  - `generate_questions`
  - `evaluate_answer`
  - `provide_model_answer`
  - `score_readiness`

This gives a clean place to adapt to official Google ADK tool wrappers as APIs evolve, while preserving the same planner-executor contract.

### Retrieval (RAG) model

- `rag.py`:
  - Reads `.txt` files from `context/`
  - Chunks text in-memory
  - Embeds chunks via sentence-transformers
  - Retrieves top chunks by cosine similarity at runtime

No external vector DB is used.

### Voice model

- `voice/listener.py`: microphone recording + local Whisper transcription.
- `voice/speaker.py`: optional local TTS via Piper CLI.

## Project structure

```text
interview-agent/
├── main.py
├── session.py
├── planner.py
├── executor.py
├── adk_runtime.py
├── llm_client.py
├── rag.py
├── models.py
├── config.py
├── requirements.txt
├── .env.example
├── .gitignore
├── prompts/
│   ├── planner_system.txt
│   ├── question_generation.txt
│   ├── answer_evaluation.txt
│   ├── model_answer.txt
│   └── readiness_scorer.txt
├── tools/
│   ├── __init__.py
│   ├── question_generator.py
│   ├── answer_evaluator.py
│   ├── model_answer.py
│   └── readiness_scorer.py
├── voice/
│   ├── __init__.py
│   ├── listener.py
│   └── speaker.py
└── context/
    └── README.txt
```

## Local setup

### 1) System prerequisites

- Python 3.10+
- [Ollama](https://ollama.com/)
- Whisper runtime dependencies (PyTorch and audio stack)
- Optional: Piper installed in PATH for TTS

### 2) Pull the local model in Ollama

```bash
ollama pull llama3.1:70b
```

### 3) Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

### 4) Install dependencies

```bash
pip install -r requirements.txt
```

### 5) Configure environment

```bash
cp .env.example .env
```

Then edit `.env` if needed (model names, sample rate, optional Piper path).

### 6) Add optional context docs

Drop extra `.txt` documents into `context/` for retrieval augmentation.

### 7) Run

```bash
python main.py
```

## Runtime usage

During the interview loop:

- `/record` → capture spoken answer with Whisper
- type normal text → treat as answer transcript and evaluate
- `/model` → generate model answer for current question
- `/next` → skip to next question
- `/end` → run readiness scorer and finish

## Notes on local-only execution

- LLM generation uses local Ollama via `ollama` Python client.
- Speech-to-text uses local Whisper model files.
- Retrieval is in-process with local embeddings.
- No cloud API keys are required.

## Extending the project

- Swap deterministic planner rules in `planner.py` with an ADK planner agent.
- Add persistence (SQLite/JSON) for session history.
- Add richer rubric logic in evaluator prompt/tool.
- Add streaming ASR or VAD for better voice UX.
>>>>>>> 2ba0d9c (intitial commit of working in terminal)
