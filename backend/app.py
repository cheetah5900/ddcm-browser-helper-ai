import os
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse

from .logging_bus import LogBus, heartbeat_every, sse_format
from .static import mount_react_dist
from .browser import browser_manager
from .workflow import (
    step10_create_preview_sheet,
    step11_canva_export_all_bot,
    step11_canva_export_bot,
    step15_etsy_listing_bot,
    step12_unzip_downloads,
    step13_download_to_local,
    step14_local_to_remote,
    step2_create_folders,
    step3_gemini_gen_full_bot,
    step4_download_images_bot,
    step6_classify_resolution,
    step8_downloads_images_to_local,
    step9_elements_to_local,
)


app = FastAPI()
log_bus = LogBus()


CONFIG_FILE = "config_win.json" if os.name == "nt" else "config_mac.json"


def _default_config() -> dict[str, Any]:
    if os.name == "nt":
        return {
            "folder_name": "",
            "element_name": "Songkran",
            "element_path": r"C:\Files\Project\local DDCM\Elements",
            "local_path": r"C:\Files\Project\local DDCM",
            "remote_path": r"G:\My Drive\Projects\DDCM\Cliparts DDCM",
            "watermark_path": r"C:\Files\Project\local DDCM\Watermark.png",
            "first_preview_watermark_path": "",
            "single_count": "12",
            "companion_count": "12",
            "elements_count": "5",
            "png_pages": "1-4",
            "jpg_pages": "6-9",
            "pdf_pages": "10",
            "primary_color": "Red",
            "secondary_color": "Gray",
            "focus_browser_tabs": False,
            "canva_design_url_part": "",
        }

    h = os.path.expanduser("~")
    return {
        "folder_name": "",
        "element_name": "Songkran",
        "element_path": os.path.join(h, "Documents/DDCM/Elements"),
        "local_path": os.path.join(h, "Documents/DDCM"),
        "remote_path": "/Users/litarcopperkaikem/Library/CloudStorage/GoogleDrive-cheetah6541@gmail.com/My Drive/Projects/DDCM/Cliparts DDCM",
        "watermark_path": os.path.join(h, "Documents/DDCM/Watermark.png"),
        "first_preview_watermark_path": "",
        "single_count": "12",
        "companion_count": "12",
        "elements_count": "5",
        "png_pages": "1-4",
        "jpg_pages": "6-9",
        "pdf_pages": "10",
        "primary_color": "Red",
        "secondary_color": "Gray",
        "focus_browser_tabs": False,
        "canva_design_url_part": "",
    }


def log(msg: str) -> None:
    log_bus.publish(msg)


def _should_focus_tabs() -> bool:
    try:
        import json

        if not os.path.exists(CONFIG_FILE):
            return False
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f) or {}
        return bool(data.get("focus_browser_tabs"))
    except Exception:
        return False


def _get_config_value(key: str, default: Any = None) -> Any:
    try:
        import json

        if not os.path.exists(CONFIG_FILE):
            return default
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f) or {}
        return data.get(key, default)
    except Exception:
        return default


@app.get("/")
def index() -> HTMLResponse:
    dist_index = os.path.join(os.path.dirname(__file__), "..", "web", "dist", "index.html")
    if os.path.exists(dist_index):
        return FileResponse(dist_index)

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


@app.get("/api/config")
def get_config() -> dict[str, Any]:
    defaults = _default_config()
    if not os.path.exists(CONFIG_FILE):
        return defaults
    try:
        import json

        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f) or {}
            # Fill missing keys with defaults so new fields appear in the UI.
            return {**defaults, **data}
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


@app.post("/api/config/set-default")
def set_default(payload: dict[str, Any]) -> dict[str, Any]:
    key = str(payload.get("key") or "").strip()
    if not key:
        raise HTTPException(status_code=400, detail="key required")
    value = payload.get("value")
    try:
        import json

        data: dict[str, Any] = {}
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f) or {}
            except Exception:
                data = {}
        data[key] = value
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
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


@app.post("/api/step/2")
def step2(payload: dict[str, Any]) -> dict[str, Any]:
    folder_name = str(payload.get("folder_name") or "").strip()
    local_path = str(payload.get("local_path") or "").strip()
    remote_path = str(payload.get("remote_path") or "").strip()
    if not all([folder_name, local_path, remote_path]):
        raise HTTPException(status_code=400, detail="folder_name/local_path/remote_path required")
    try:
        step2_create_folders(folder_name, local_path, remote_path, log)
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/step/6")
def step6(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        step6_classify_resolution(log)
        return {"ok": True}
    except FileNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/step/12")
def step12(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        step12_unzip_downloads(log)
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/step/13")
def step13(payload: dict[str, Any]) -> dict[str, Any]:
    folder_name = str(payload.get("folder_name") or "").strip()
    local_path = str(payload.get("local_path") or "").strip()
    if not all([folder_name, local_path]):
        raise HTTPException(status_code=400, detail="folder_name/local_path required")
    try:
        step13_download_to_local(folder_name, local_path, log)
        return {"ok": True}
    except Exception as e:
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
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/step/1")
def step1(payload: dict[str, Any]) -> dict[str, Any]:
    log("Step 1: Config is handled in the UI. Ready.")
    return {"ok": True}


@app.post("/api/step/3")
def step3(payload: dict[str, Any]) -> dict[str, Any]:
    mode = str(payload.get("mode") or "single").strip().lower()
    single_count = payload.get("single_count")
    companion_count = payload.get("companion_count")
    elements_count = payload.get("elements_count")
    try:
        bot = browser_manager.get()
        step3_gemini_gen_full_bot(
            bot,
            mode,
            int(single_count) if single_count is not None else None,
            int(companion_count) if companion_count is not None else None,
            int(elements_count) if elements_count is not None else None,
            log,
        )
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/step/4")
def step4(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        bot = browser_manager.get()
        step4_download_images_bot(bot, log)
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/step/5")
def step5(payload: dict[str, Any]) -> dict[str, Any]:
    log("Step 5: Manual step (external app).")
    return {"ok": True}


@app.post("/api/step/7")
def step7(payload: dict[str, Any]) -> dict[str, Any]:
    log("Step 7: Manual step (external app).")
    return {"ok": True}


@app.post("/api/step/9")
def step9(payload: dict[str, Any]) -> dict[str, Any]:
    element_name = str(payload.get("element_name") or "").strip()
    element_path = str(payload.get("element_path") or "").strip()
    if not element_name or not element_path:
        raise HTTPException(status_code=400, detail="element_name/element_path required")
    try:
        step9_elements_to_local(element_name, element_path, log)
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/step/10")
def step10(payload: dict[str, Any]) -> dict[str, Any]:
    folder_name = str(payload.get("folder_name") or "").strip()
    local_path = str(payload.get("local_path") or "").strip()
    watermark_path = str(payload.get("watermark_path") or "").strip() or None
    first_preview_watermark_path = str(payload.get("first_preview_watermark_path") or "").strip() or None
    element_name = str(payload.get("element_name") or "").strip()
    element_path = str(payload.get("element_path") or "").strip()
    if not folder_name or not local_path:
        raise HTTPException(status_code=400, detail="folder_name/local_path required")
    try:
        step10_create_preview_sheet(
            folder_name,
            local_path,
            watermark_path,
            first_preview_watermark_path,
            element_name,
            element_path,
            log,
        )
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/step/11")
def step11(payload: dict[str, Any]) -> dict[str, Any]:
    mode = str(payload.get("mode") or "all").strip().lower()
    png_pages = str(payload.get("png_pages") or "").strip() or None
    jpg_pages = str(payload.get("jpg_pages") or "").strip() or None
    pdf_pages = str(payload.get("pdf_pages") or "").strip() or None
    try:
        focus_tab = bool(payload.get("focus_tab")) if payload.get("focus_tab") is not None else _should_focus_tabs()
        canva_url_part = (
            str(payload.get("canva_url_part") or "").strip()
            or str(_get_config_value("canva_design_url_part", "") or "").strip()
            or "canva.com/design/"
        )
        bot = browser_manager.get()
        if mode == "png":
            step11_canva_export_bot(bot, "png", png_pages, log, focus_tab=focus_tab, canva_url_part=canva_url_part)
        elif mode == "jpg":
            step11_canva_export_bot(bot, "jpg", jpg_pages, log, focus_tab=focus_tab, canva_url_part=canva_url_part)
        elif mode == "pdf":
            step11_canva_export_bot(bot, "pdf", pdf_pages, log, focus_tab=focus_tab, canva_url_part=canva_url_part)
        else:
            step11_canva_export_all_bot(
                bot,
                png_pages,
                jpg_pages,
                pdf_pages,
                log,
                focus_tab=focus_tab,
                canva_url_part=canva_url_part,
            )
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/step/15")
def step15(payload: dict[str, Any]) -> dict[str, Any]:
    primary_color = str(payload.get("primary_color") or "").strip()
    secondary_color = str(payload.get("secondary_color") or "").strip()
    if not primary_color or not secondary_color:
        raise HTTPException(status_code=400, detail="primary_color/secondary_color required")
    try:
        bot = browser_manager.get()
        step15_etsy_listing_bot(bot, primary_color, secondary_color, log)
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# If web/dist exists, serve it as SPA (must be last to avoid catching /api/*).
mount_react_dist(app, os.path.join(os.path.dirname(__file__), "..", "web", "dist"))
