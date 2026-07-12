import asyncio
import os
import logging
import yt_dlp
from typing import Optional, Dict, Any
from config import config
from utils import create_temp_dir, cleanup_temp_dir, sanitize_filename

logger = logging.getLogger(__name__)

class DownloadError(Exception):
    pass

class Downloader:
    def __init__(self):
        self.semaphore = asyncio.Semaphore(2)

    async def download(self, query: str) -> Dict[str, Any]:
        async with self.semaphore:
            return await self._download_with_retry(query)

    async def _download_with_retry(self, query: str) -> Dict[str, Any]:
        info = await self._extract_info(query)
        if not info:
            raise DownloadError("Could not extract video information.")

        duration = info.get('duration', 0)
        if duration > config.MAX_DURATION_SECONDS:
            raise DownloadError(f"Video exceeds max duration of {config.MAX_DURATION_SECONDS}s.")

        last_error = None
        for quality in config.BITRATES:
            try:
                result = await self._download_with_quality(query, quality, info)
                if result:
                    return result
            except Exception as e:
                last_error = e
                logger.warning(f"Failed with quality {quality}kbps: {e}")
                continue

        if last_error:
            raise DownloadError(f"All quality levels failed: {last_error}")

        raise DownloadError("Failed to download after all attempts.")

    async def _extract_info(self, query: str) -> Optional[Dict]:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'skip_download': True,
            'cookiefile': config.COOKIES_FILE if config.COOKIES_FILE else None,
            'retries': config.RETRIES,
            'timeout': config.TIMEOUT,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                return await asyncio.to_thread(ydl.extract_info, query, download=False)
            except Exception as e:
                logger.error(f"Info extraction failed: {e}")
                return None

    async def _download_with_quality(self, query: str, bitrate: int, info: Dict) -> Optional[Dict]:
        temp_dir = create_temp_dir()
        out_template = os.path.join(temp_dir, "%(title)s.%(ext)s")
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': str(bitrate),
            }],
            'outtmpl': out_template,
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'cookiefile': config.COOKIES_FILE if config.COOKIES_FILE else None,
            'retries': config.RETRIES,
            'timeout': config.TIMEOUT,
        }

        try:
            def download_sync():
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([query])
                    for f in os.listdir(temp_dir):
                        if f.endswith('.mp3'):
                            return os.path.join(temp_dir, f)
                    return None

            filepath = await asyncio.to_thread(download_sync)
            if not filepath:
                raise DownloadError("No MP3 file produced.")

            file_size = os.path.getsize(filepath)
            if file_size <= config.MAX_FILE_SIZE_BYTES:
                return {
                    'filepath': filepath,
                    'file_size': file_size,
                    'bitrate': bitrate,
                    'info': info,
                    'temp_dir': temp_dir
                }
            else:
                os.remove(filepath)
                cleanup_temp_dir(temp_dir)
                return None
        except Exception as e:
            logger.error(f"Download failed for bitrate {bitrate}: {e}")
            cleanup_temp_dir(temp_dir)
            raise

    async def cleanup(self, filepath: str):
        if filepath and os.path.exists(filepath):
            try:
                os.remove(filepath)
                parent = os.path.dirname(filepath)
                cleanup_temp_dir(parent)
            except Exception as e:
                logger.warning(f"Cleanup failed for {filepath}: {e}")
