# Streaming Agent

Same agent setup as `Agent/`, but every step is streamed out of an async
generator with `yield` instead of being printed at the end.
Split into a `backend/` (Python) and a `frontend/` (static UI).

```
Streaming agent/
├── backend/
│   ├── server.py              Flask server (port 5000), SSE endpoint
│   ├── main.py                CLI entry point
│   ├── Custom_Agents/
│   │   ├── all_agent.py       run_main_agent_stream() - the async generator
│   │   └── Custom_tools/      get_recipe, email_sender
│   ├── Custom_loggers/        rotating file + stream logger -> backend/logs/
│   ├── prompts/               agent instruction .md files
│   └── utils/                 azure client, prompt loader, paths
└── frontend/
    ├── index.html
    ├── css/styles.css
    └── js/app.js              reads the SSE stream, renders tokens live
```

## The stream
`run_main_agent_stream()` yields dicts as they happen:

| event | payload |
|---|---|
| `agent` | `name` - agent started / handoff target |
| `tool` | `name` - tool call started |
| `tool_output` | `output` - tool result |
| `token` | `text` - a streamed text delta |
| `done` | `output` - final answer |
| `error` | `message` |

The CLI prints them; `server.py` re-yields the exact same dicts as SSE
(the async generator is bridged onto a background thread + queue for Flask).

## Run

**Terminal 1 - start the backend:**

```
cd c:\Users\KhushChadha\Desktop\Azure_Agentic_AI\Streaming agent\backend
pip install flask flask-cors
python server.py
```

You should see `Running on http://127.0.0.1:5000`

**Terminal 2 - open the frontend:**

```
start "c:\Users\KhushChadha\Desktop\Azure_Agentic_AI\Streaming agent\frontend\index.html"
```

CORS is enabled, so opening the HTML straight from disk (`file://`) works.

**Terminal only, no UI:**

```
python backend/main.py "give me a recipe for omelette"
```

Both entry points work from any working directory. Azure OpenAI credentials
come from the `.env` in the repo root.
