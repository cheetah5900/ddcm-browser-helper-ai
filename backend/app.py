import os
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse

from .logging_bus import LogBus, heartbeat_every, sse_format
from .static import mount_react_dist
from .workflow import step14_local_to_remote, step8_downloads_images_to_local


app = FastAPI()
log_bus = LogBus()


CONFIG_FILE = "config_win.json" if os.name == "nt" else "config_mac.json"


def log(msg: str) -> None:
    log_bus.publish(msg)


@app.get("/")
def index() -> HTMLResponse:
    # Placeholder until React UI is wired in (dist build).
    html = """<!doctype html>
<html>
  <head>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width,initial-scale=1\" />
    <title>DDCM Browser Helper</title>
  </head>
  <body style=\"font-family: system-ui, -apple-system, sans-serif; padding: 24px\">
    <h1>DDCM Browser Helper</h1>
    <p>Backend is running. React UI will replace this page.</p>
    <p><a href=\"/logs\">Open logs stream</a></p>
  </body>
</html>"""
    return HTMLResponse(html)


# If web/dist exists, serve it as SPA.
mount_react_dist(app, os.path.join(os.path.dirname(__file__), "..", "web", "dist"))


@app.get("/api/config")
def get_config() -> dict[str, Any]:
    if not os.path.exists(CONFIG_FILE):
        return {}
    try:
        import json

        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed reading config: {e}")


@app.post("/api/config")
def set_config(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        import json

        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=4)
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed writing config: {e}")


@app.get("/logs")
def logs() -> StreamingResponse:
    sid, q = log_bus.subscribe()

    def gen():
        try:
            yield sse_format("connected", event="status")
            heartbeats = heartbeat_every(15.0)
            while True:
                try:
                    msg = q.get(timeout=0.25)
                    yield sse_format(msg, event="log")
                except Exception:
                    if next(heartbeats):
                        yield sse_format("hb", event="ping")
        finally:
            log_bus.unsubscribe(sid)

    return StreamingResponse(gen(), media_type="text/event-stream")


@app.post("/api/step/8")
def step8(payload: dict[str, Any]) -> dict[str, Any]:
    folder_name = str(payload.get("folder_name") or "").strip()
    local_path = str(payload.get("local_path") or "").strip()
    if not folder_name or not local_path:
        raise HTTPException(status_code=400, detail="folder_name and local_path are required")
    try:
        step8_downloads_images_to_local(folder_name, local_path, log)
        return {"ok": True}
    except FileNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/step/14")
def step14(payload: dict[str, Any]) -> dict[str, Any]:
    folder_name = str(payload.get("folder_name") or "").strip()
    local_path = str(payload.get("local_path") or "").strip()
    remote_path = str(payload.get("remote_path") or "").strip()
    element_name = str(payload.get("element_name") or "").strip()
    element_path = str(payload.get("element_path") or "").strip()
    if not all([folder_name, local_path, remote_path, element_name, element_path]):
        raise HTTPException(status_code=400, detail="folder_name/local_path/remote_path/element_name/element_path required")
    try:
        step14_local_to_remote(folder_name, local_path, remote_path, element_name, element_path, log)
        return {"ok": True}
    except FileNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))
