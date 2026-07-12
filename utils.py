import re
import uuid
import tempfile
import os
import shutil

def sanitize_filename(filename: str) -> str:
    filename = re.sub(r'[\\/*?:"<>|]', "", filename)
    filename = filename.strip()
    if not filename:
        filename = "audio"
    return filename

def create_temp_dir() -> str:
    temp_dir = tempfile.mkdtemp(prefix="musicbot_")
    return temp_dir

def cleanup_temp_dir(path: str):
    try:
        if os.path.exists(path) and os.path.isdir(path):
            shutil.rmtree(path, ignore_errors=True)
    except Exception:
        pass

def format_duration(seconds: int) -> str:
    if seconds < 3600:
        return f"{seconds//60:02d}:{seconds%60:02d}"
    else:
        return f"{seconds//3600:02d}:{(seconds%3600)//60:02d}:{seconds%60:02d}"
