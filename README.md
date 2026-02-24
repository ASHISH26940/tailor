# 🚢 Titanic Dataset Chat Agent

An AI-powered chatbot that lets you explore the Titanic dataset through natural language. Ask questions in plain English and get text answers, statistics, and auto-generated visualizations.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?logo=langchain&logoColor=white)

## Features

- **Natural language queries** — ask anything about the Titanic dataset
- **Auto-generated charts** — request histograms, bar charts, scatter plots, etc.
- **Conversational UI** — chat interface with full message history
- **Real-time analysis** — powered by a LangChain ReAct agent that writes and executes Python code on the fly
- **Redis caching** — repeated questions return instantly from cache (1-hour TTL, graceful fallback if Redis unavailable)

## Architecture

```
┌─────────────────────┐         ┌──────────────────────────────┐
│   Streamlit (8501)  │  POST   │       FastAPI (8000)         │
│                     │ ──────► │                              │
│  • Chat UI          │ /chat   │  • Redis cache check         │
│  • Message history  │ ◄────── │  • LangChain ReAct Agent     │
│  • Image rendering  │  JSON   │  • Plot generation → static/ │
│                     │         │  • OpenRouter LLM            │
└─────────────────────┘         └──────────────────────────────┘
```

## Quick Start

### 1. Clone & install dependencies

```bash
git clone <repo-url>
cd tailortalk
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
```

### 2. Configure environment

Copy the example env file and add your API key:

```bash
cp .example.env .env
```

Edit `.env` and set your OpenRouter API key:

```env
OPENAI_API_KEY=sk-or-v1-your-key-here
```

### 3. Start the backend

```bash
uvicorn backend.main:app --reload
```

The API will be available at `http://localhost:8000`.

### 4. Start the frontend

In a separate terminal:

```bash
streamlit run frontend/app.py
```

The UI will open at `http://localhost:8501`.

## Example Queries

| Query                                          | Expected Output                |
| ---------------------------------------------- | ------------------------------ |
| "What percentage of passengers were male?"     | Text answer with percentage    |
| "Show me a histogram of passenger ages"        | Age distribution chart         |
| "What was the average ticket fare?"            | Text answer with fare value    |
| "How many passengers embarked from each port?" | Count breakdown or bar chart   |
| "What was the survival rate by gender?"        | Comparison statistics or chart |

## Project Structure

```
tailortalk/
├── backend/
│   ├── agent.py          # LangChain agent setup & LLM config
│   └── main.py           # FastAPI app & /chat endpoint
├── frontend/
│   └── app.py            # Streamlit chat interface
├── titanic/
│   └── train.csv         # Titanic dataset
├── static/               # Auto-generated plot images
├── .streamlit/
│   └── config.toml       # Streamlit theme config
├── .env                  # API keys (not committed)
├── .example.env          # Example env template
├── requirements.txt      # Python dependencies
└── README.md
```

## Tech Stack

- **Backend**: [FastAPI](https://fastapi.tiangolo.com/) + [Uvicorn](https://www.uvicorn.org/)
- **AI Agent**: [LangChain](https://www.langchain.com/) ReAct Agent with `PythonAstREPLTool`
- **LLM**: `openai/gpt-oss-120b` via [OpenRouter](https://openrouter.ai/)
- **Caching**: [Redis](https://redis.io/) with graceful fallback
- **Visualization**: [Matplotlib](https://matplotlib.org/) + [Seaborn](https://seaborn.pydata.org/)
- **Frontend**: [Streamlit](https://streamlit.io/) with custom CSS theming

## How It Works

1. User types a question in the Streamlit chat interface
2. Streamlit sends a `POST` request to the FastAPI `/chat` endpoint
3. FastAPI checks Redis for a cached response — if found, returns it instantly
4. On cache miss, the LangChain ReAct agent interprets the question, writes Python/Pandas code, and executes it
5. If a visualization is requested, the agent saves the plot to `static/` with a unique filename
6. Text-only responses are cached in Redis (1-hour TTL); plot responses are not cached
7. FastAPI parses the agent's response, extracts any image paths, and returns a clean JSON response
8. Streamlit renders the text answer and any generated charts in the chat

## License

MIT
