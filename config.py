import os
from dataclasses import dataclass

@dataclass
class Config:
    # Discord
    DISCORD_TOKEN: str = os.getenv("DISCORD_TOKEN", "")
    GUILD_ID: int = int(os.getenv("GUILD_ID", 0))

    # Download limits
    MAX_DURATION_SECONDS: int = int(os.getenv("MAX_DURATION_SECONDS", 600))
    MAX_FILE_SIZE_BYTES: int = int(os.getenv("MAX_FILE_SIZE_BYTES", 25 * 1024 * 1024))
    BITRATES: list = [int(x) for x in os.getenv("BITRATES", "192,128,96,64").split(",")]

    # yt-dlp
    RETRIES: int = int(os.getenv("RETRIES", 10))
    TIMEOUT: int = int(os.getenv("TIMEOUT", 30))
    COOKIES_FILE: str = os.getenv("COOKIES_FILE", "")

    # Paths
    TEMP_DIR: str = os.getenv("TEMP_DIR", "/tmp/musicbot")

    # Rate limiting
    COOLDOWN_RATE: int = int(os.getenv("COOLDOWN_RATE", 1))
    COOLDOWN_PERIOD: int = int(os.getenv("COOLDOWN_PERIOD", 30))

    # Embed colors
    EMBED_COLOR: int = 0x1DB954

config = Config()
