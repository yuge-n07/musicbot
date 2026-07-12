import os
from dataclasses import dataclass, field

@dataclass
class Config:
    DISCORD_TOKEN: str = os.getenv("DISCORD_TOKEN", "")
    GUILD_ID: int = int(os.getenv("GUILD_ID", 0))
    MAX_DURATION_SECONDS: int = int(os.getenv("MAX_DURATION_SECONDS", 600))
    MAX_FILE_SIZE_BYTES: int = int(os.getenv("MAX_FILE_SIZE_BYTES", 25 * 1024 * 1024))
    BITRATES: list = field(default_factory=lambda: [192, 128, 96, 64])
    RETRIES: int = int(os.getenv("RETRIES", 10))
    TIMEOUT: int = int(os.getenv("TIMEOUT", 30))
    COOKIES_FILE: str = os.getenv("COOKIES_FILE", "")
    TEMP_DIR: str = os.getenv("TEMP_DIR", "/tmp/musicbot")
    COOLDOWN_RATE: int = int(os.getenv("COOLDOWN_RATE", 1))
    COOLDOWN_PERIOD: int = int(os.getenv("COOLDOWN_PERIOD", 30))
    EMBED_COLOR: int = 0x1DB954

    def __post_init__(self):
        bitrates_env = os.getenv("BITRATES")
        if bitrates_env:
            self.BITRATES = [int(x.strip()) for x in bitrates_env.split(",") if x.strip()]

config = Config()
