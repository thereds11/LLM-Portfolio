import time
import logging
import asyncio
from typing import List

from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from llama_index.core.llms import ChatMessage
from llama_index.llms.ollama import Ollama

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Local LLM Chat Backend")

# Allow the SPA (likely served from file:// or localhost) to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://192.168.9.220:5173",
        ],
    allow_origin_regex=".*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve SPA static files from ./frontend
app.mount("/static", StaticFiles(directory="frontend"), name="static")




class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    model: str
    messages: List[Message]


class ChatResponse(BaseModel):
    response: str
    duration: float


@app.get("/health")
async def health():
    return {"status": "ok"}


async def _call_ollama(model: str, messages: List[ChatMessage]) -> str:
    """Run the Ollama chat stream in a thread and collect the full response."""

    def run():
        try:
            llm = Ollama(model=model, request_timeout=120.0)
            resp = llm.stream_chat(messages)
            response = ""
            for r in resp:
                # each r is expected to have a `delta` attribute
                response += getattr(r, "delta", "")
            logging.info(f"Model: {model}, Response length: {len(response)}")
            return response
        except Exception as e:
            logging.exception("Error calling Ollama")
            raise

    return await asyncio.to_thread(run)


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    start = time.time()
    try:
        messages = [ChatMessage(role=m.role, content=m.content) for m in req.messages]
        response = await _call_ollama(req.model, messages)
        duration = time.time() - start
        return ChatResponse(response=response, duration=duration)
    except Exception as e:
        logging.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Serve index at root (must be defined at import time so Uvicorn sees it)
@app.get("/", include_in_schema=False)
async def root():
    """Return the SPA index file."""
    return FileResponse("frontend/dist/index.html")


@app.websocket("/ws/chat")
async def websocket_chat(ws: WebSocket):
    """WebSocket endpoint for streaming LLM tokens to the browser.

    Client should first send a JSON message: { model: str, messages: [{role,content}, ...] }
    Then server streams JSON messages { type: 'token', token: '...' } and finally { type: 'done', duration: float }.
    Client may send { action: 'cancel' } to request cancellation.
    """
    await ws.accept()
    import threading, json

    cancel_event = threading.Event()
    queue: asyncio.Queue = asyncio.Queue()

    try:
        init_text = await ws.receive_text()
    except Exception:
        await ws.close()
        return

    try:
        init = json.loads(init_text)
        model = init.get("model")
        msgs = init.get("messages", [])
        messages = [ChatMessage(role=m.get("role"), content=m.get("content")) for m in msgs]
    except Exception as e:
        await ws.send_json({"type": "error", "message": f"Invalid init payload: {e}"})
        await ws.close()
        return

    def llm_worker():
        try:
            llm = Ollama(model=model, request_timeout=120.0)
            resp = llm.stream_chat(messages)
            for r in resp:
                if cancel_event.is_set():
                    break
                token = getattr(r, "delta", "")
                try:
                    asyncio.run_coroutine_threadsafe(queue.put({"type": "token", "token": token}), asyncio.get_event_loop())
                except Exception:
                    break
            try:
                asyncio.run_coroutine_threadsafe(queue.put({"type": "done"}), asyncio.get_event_loop())
            except Exception:
                pass
        except Exception as e:
            try:
                asyncio.run_coroutine_threadsafe(queue.put({"type": "error", "message": str(e)}), asyncio.get_event_loop())
            except Exception:
                pass

    worker = threading.Thread(target=llm_worker, daemon=True)
    worker.start()

    start = time.time()

    try:
        while True:
            send_task = asyncio.create_task(queue.get())
            recv_task = asyncio.create_task(ws.receive_text())
            done, pending = await asyncio.wait([send_task, recv_task], return_when=asyncio.FIRST_COMPLETED)

            if send_task in done:
                msg = send_task.result()
                if not recv_task.done():
                    recv_task.cancel()
                if msg.get("type") == "token":
                    await ws.send_json({"type": "token", "token": msg.get("token", "")})
                elif msg.get("type") == "done":
                    duration = time.time() - start
                    await ws.send_json({"type": "done", "duration": duration})
                    break
                elif msg.get("type") == "error":
                    await ws.send_json({"type": "error", "message": msg.get("message")})
                    break
            elif recv_task in done:
                recv_text = recv_task.result()
                try:
                    ctrl = json.loads(recv_text)
                    if ctrl.get("action") == "cancel":
                        cancel_event.set()
                        await ws.send_json({"type": "error", "message": "cancelled by client"})
                        break
                except Exception:
                    pass

            for t in pending:
                t.cancel()

    except Exception:
        cancel_event.set()
    finally:
        cancel_event.set()
        try:
            await ws.close()
        except Exception:
            pass


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)