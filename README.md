# Azure Agentic AI

Hands-on agent projects built on **Azure OpenAI (gpt-4o)** — a multi-agent
handoff system with the OpenAI Agents SDK, a streaming version of the same
system with a web UI, and a set of LangChain / LangGraph notebooks.

```
Azure_Agentic_AI/
├── Agent/                  Multi-agent handoff demo (CLI, non-streaming)
├── Streaming agent/        Same agents, streamed via `yield` + Flask/SSE web UI
├── Langchain_langgraph/    LangChain & LangGraph learning notebooks
├── .env.example            Azure OpenAI settings template
└── requirements.txt
```

---

## Setup

```bash
git clone <your-repo-url>
cd Azure_Agentic_AI

python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux

pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in your Azure OpenAI details:

```
AZURE_OPENAI_GPT_4O_API_KEY=...
AZURE_OPENAI_GPT_4O_API_VERSION=2025-03-01-preview
AZURE_OPENAI_GPT_4O_DEPLOYMENT_NAME=gpt-4o
AZURE_OPENAI_GPT_4O_ENDPOINT=https://your-resource.openai.azure.com/
```

`.env` is git-ignored — never commit it.

---

## 1. `Agent/` — multi-agent handoffs

A **Main Agent** reads the request and hands off to a specialist:

| Agent | Handles | Tool |
|---|---|---|
| Main Agent | general questions, routing | — |
| cook Agent | recipes (replies with lots of emojis) | `get_recipe` |
| email Agent | sending email | `email_sender` |

```
Agent/
├── main.py                          entry point
├── Custom_Agents/
│   ├── all_agent.py                 agent definitions + handoffs
│   └── Custom_tools/                get_recipe, email_sender
├── Custom_loggers/                  rotating daily file + console logger
├── prompts/                         each agent's instructions as .md
└── utils/                           Azure client, prompt loader
```

Run it:

```bash
cd Agent
python main.py
```

The full answer is printed once the run finishes (`Runner.run`).

---

## 2. `Streaming agent/` — the same agents, streamed

Identical agent setup, but the run is an **async generator**: every step is
`yield`ed the moment it happens instead of being printed at the end. A Flask
backend re-yields those events as Server-Sent Events and a small chat UI
renders them live.

```
Streaming agent/
├── backend/
│   ├── server.py                    Flask + CORS, SSE endpoint (port 5000)
│   ├── main.py                      CLI, streams to the terminal
│   ├── Custom_Agents/all_agent.py   run_main_agent_stream() — the generator
│   ├── Custom_Agents/Custom_tools/  get_recipe, email_sender
│   ├── Custom_loggers/  prompts/  utils/
└── frontend/
    ├── index.html
    ├── css/styles.css
    └── js/app.js                    reads the SSE stream, renders tokens live
```

### The event stream

`run_main_agent_stream()` yields plain dicts:

| event | payload | meaning |
|---|---|---|
| `agent` | `name` | an agent started / was handed off to |
| `tool` | `name` | a tool call started |
| `tool_output` | `output` | the tool's result |
| `token` | `text` | one streamed text delta |
| `done` | `output` | the final answer |
| `error` | `message` | the run failed |

The CLI prints them; `server.py` re-yields the exact same dicts as SSE. Since
Flask needs a sync generator, the async one runs on its own event loop in a
background thread and pushes events onto a queue.

### Run it

**Terminal 1 — start the backend:**

```
cd "c:\Users\KhushChadha\Desktop\Azure_Agentic_AI\Streaming agent\backend"
pip install flask flask-cors
python server.py
```

You should see `Running on http://127.0.0.1:5000`

**Terminal 2 — open the frontend:**

```
start "c:\Users\KhushChadha\Desktop\Azure_Agentic_AI\Streaming agent\frontend\index.html"
```

CORS is enabled, so opening the HTML straight from disk (`file://`) works.

**Terminal only, no UI:**

```
python backend/main.py "give me a recipe for omelette"
```

### The UI

Dark chat interface that shows the agent thinking out loud — a blinking caret
on the bubble as tokens arrive, plus pills for each handoff (`🤖 cook Agent`)
and tool call (`🛠 get_recipe`). Enter sends, Shift+Enter adds a newline, and
the suggestion chips fire an example prompt.

---

## 3. `Langchain_langgraph/` — notebooks

| Notebook | Topic |
|---|---|
| `Work_with_Langchain.ipynb` | LangChain basics: prompts, chains, memory, tools, streaming callbacks |
| `Lang_Graph/Lang_Graph_01.ipynb` | first `StateGraph`, nodes and edges |
| `Lang_Graph/Lang_Graph_02.ipynb` | message state and reducers |
| `Lang_Graph/Lang_Graph_03-04.ipynb` | conditional edges and routing |
| `Lang_Graph/Lang_Graph_05.ipynb` | prebuilt ReAct agent + memory checkpointer |

```bash
jupyter notebook Langchain_langgraph
```

---

## Notes

- Every entry point loads credentials from the root `.env` via `python-dotenv`,
  so the scripts work from any working directory.
- Logs are written to a `logs/` folder next to the code, rotated daily, and are
  git-ignored.
- The `email_sender` tool is a stub — it always reports a network failure, which
  is handy for watching how an agent reacts to a failing tool.
