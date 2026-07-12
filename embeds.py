import discord
from config import config
from utils import format_duration

def build_music_embed(info: dict, bitrate: int, file_size: int) -> discord.Embed:
    embed = discord.Embed(
        title=info.get('title', 'Unknown')[:256],
        description=(
            f"👤 **{info.get('uploader', 'Unknown')}**\n"
            f"⏱ {format_duration(info.get('duration', 0))}"
        ),
        color=config.EMBED_COLOR,
    )
    if info.get('webpage_url'):
        embed.url = info['webpage_url']
    if info.get('thumbnail'):
        embed.set_thumbnail(url=info['thumbnail'])
    embed.add_field(name="Bitrate", value=f"{bitrate} kbps", inline=True)
    embed.add_field(name="Size", value=f"{file_size/1024/1024:.2f} MB", inline=True)
    embed.set_footer(text=f"📺 {info.get('view_count', 0):,} views")
    return embed
