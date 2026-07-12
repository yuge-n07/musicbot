import os
import asyncio
from dotenv import load_dotenv

# Set environment variables before importing aioslsk
os.environ["SLSK_PORT"] = "0"
os.environ["SLSK_OBFUSCATED_PORT"] = "0"

from aioslsk.client import SoulSeekClient
from aioslsk.settings import (
    Settings,
    CredentialsSettings,
)

load_dotenv()

class SoulseekClient:

    def __init__(self):
        username = os.getenv("SLSK_USER", "bihi_bihi")
        password = os.getenv("SLSK_PASS", "bihi_bihi")

        self.client = SoulSeekClient(
            Settings(
                credentials=CredentialsSettings(
                    username=username,
                    password=password,
                )
            )
        )
        self.connected = False
        self._reconnect_lock = asyncio.Lock()

    async def _ensure_connected(self):
        async with self._reconnect_lock:
            if self.connected:
                return True

            print("🔄 Connecting to Soulseek (no listening ports)...")
            try:
                await self.client.start()
                await self.client.login()
                self.connected = True
                print("✅ Soulseek connected!")
            except Exception as e:
                # If it fails because of port binding, we can still continue (client may still work)
                if "failed to bind listening port" in str(e):
                    print("⚠️ Port binding failed, but continuing anyway...")
                    self.connected = True
                else:
                    print(f"❌ Soulseek connection failed: {e}")
                    raise

    async def connect(self):
        await self._ensure_connected()

    async def search(self, query: str, wait_time: int = 8):
        await self._ensure_connected()
        print(f"🔍 Searching: {query}")
        request = await self.client.searches.search(query)
        await asyncio.sleep(wait_time)
        results = list(request.results)
        results.sort(key=lambda r: r.avg_speed, reverse=True)
        return results

    async def download(self, file, username: str, target_path: str):
        await self._ensure_connected()
        await self.client.download(file, username, target_path)

    async def close(self):
        if self.connected:
            try:
                await self.client.stop()
            except:
                pass
            self.connected = False
            print("🔌 Soulseek disconnected.")

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
