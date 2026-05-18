import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles


def mount_react_dist(app: FastAPI, web_dist_dir: str) -> None:
    dist = Path(web_dist_dir)
    if not dist.exists():
        return

    app.mount("/assets", StaticFiles(directory=str(dist / "assets")), name="assets")

    index_file = dist / "index.html"
    if not index_file.exists():
        return

    @app.get("/{path:path}")
    def spa_fallback(path: str):
        # Serve index for client-side routes.
        return FileResponse(str(index_file))
