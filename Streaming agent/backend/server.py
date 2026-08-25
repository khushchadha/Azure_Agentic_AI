"""Flask backend for the Streaming Agent.

Run it:
    cd "c:\\Users\\KhushChadha\\Desktop\\Azure_Agentic_AI\\Streaming agent\\backend"
    pip install flask flask-cors
    python server.py
    -> Running on http://127.0.0.1:5000

Then just open ../frontend/index.html in the browser (file:// is fine,
CORS is enabled).
"""
import asyncio
import json
import os
import queue
import sys
import threading

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, Response, request, stream_with_context
from flask_cors import CORS

from Custom_Agents.all_agent import run_main_agent_stream

app = Flask(__name__)
CORS(app)

_DONE = object()


def iter_agent_events(user_input: str):
    """Bridge the *async* generator into a plain sync generator for Flask.

    The agent runs on its own event loop in a background thread and pushes
    every yielded event onto a queue that this generator drains.
    """
    events = queue.Queue()

    def worker():
        async def pump():
            async for event in run_main_agent_stream(user_input):
                events.put(event)

        try:
            asyncio.run(pump())
        except Exception as exc:  # never leave the reader hanging
            events.put({"type": "error", "message": str(exc)})
        finally:
            events.put(_DONE)

    threading.Thread(target=worker, daemon=True).start()

    while True:
        event = events.get()
        if event is _DONE:
            break
        yield event


@app.route("/health")
def health():
    return {"status": "ok"}


@app.route("/chat/stream", methods=["POST"])
def chat_stream():
    """Stream the agent's events to the frontend as Server-Sent Events."""
    message = (request.get_json(silent=True) or {}).get("message", "")

    @stream_with_context
    def event_source():
        for event in iter_agent_events(message):
            yield f"data: {json.dumps(event)}\n\n"

    return Response(
        event_source(),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


if __name__ == "__main__":
    # threaded=True so the SSE response does not block other requests
    app.run(host="127.0.0.1", port=5000, threaded=True, debug=False)
