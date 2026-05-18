import os
import re
import shutil
from typing import Callable

from send2trash import send2trash


def clean_name_from_folder_name(folder_name: str) -> str:
    return folder_name.split(" - ", 1)[1] if " - " in folder_name else folder_name


def trash(path: str, log: Callable[[str], None]) -> None:
    if not path or not os.path.exists(path):
        return
    try:
        send2trash(path)
    except Exception as e:
        log(f"Error moving to Trash: {path} ({e})")
        raise


def step8_downloads_images_to_local(folder_name: str, local_path: str, log: Callable[[str], None]) -> None:
    clean_name = clean_name_from_folder_name(folder_name)
    base = os.path.join(local_path, folder_name)
    downloads = os.path.join(os.path.expanduser("~"), "Downloads")
    img_d = os.path.join(downloads, "images")
    if not os.path.exists(img_d):
        raise FileNotFoundError("No 'images' folder in Downloads")

    d4000 = os.path.join(base, "4000x4000")
    os.makedirs(d4000, exist_ok=True)

    img_files: list[str] = []
    for root, dirs, files in os.walk(img_d):
        for f in files:
            if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                img_files.append(os.path.join(root, f))

    if not img_files:
        log("No images found in Downloads/images")
        return

    for i, fp in enumerate(sorted(img_files)):
        ext = os.path.splitext(fp)[1]
        shutil.copy2(fp, os.path.join(d4000, f"{clean_name} ({i+1}){ext}"))

    trash(img_d, log)
    log("Step 8: Moved & Renamed images to Local.")


def step14_local_to_remote(
    folder_name: str,
    local_path: str,
    remote_path: str,
    element_name: str,
    element_path: str,
    log: Callable[[str], None],
) -> None:
    clean_name = clean_name_from_folder_name(folder_name)

    elements_src = os.path.join(element_path, element_name)
    if not os.path.exists(elements_src):
        raise FileNotFoundError(f"Elements folder not found: {elements_src}")

    total_copied = 0
    for sub in ["4000x4000", "Sticker Set"]:
        src_dir = os.path.join(local_path, folder_name, sub)
        dst_dir = os.path.join(remote_path, folder_name, sub)
        if not os.path.exists(src_dir):
            continue
        os.makedirs(dst_dir, exist_ok=True)
        files = sorted([f for f in os.listdir(src_dir) if os.path.isfile(os.path.join(src_dir, f))])
        for i, it in enumerate(files):
            ext = os.path.splitext(it)[1]
            shutil.copy2(os.path.join(src_dir, it), os.path.join(dst_dir, f"{clean_name} ({i+1}){ext}"))
            total_copied += 1

    # Elements to Remote 4000x4000 (no renaming)
    rd = os.path.join(remote_path, folder_name, "4000x4000")
    os.makedirs(rd, exist_ok=True)
    el_files = sorted([f for f in os.listdir(elements_src) if os.path.isfile(os.path.join(elements_src, f))])
    el_copied = 0
    for it in el_files:
        shutil.copy2(os.path.join(elements_src, it), os.path.join(rd, it))
        el_copied += 1
        total_copied += 1

    log(f"Step 14: Done! Copied {total_copied} files total ({el_copied} elements).")
