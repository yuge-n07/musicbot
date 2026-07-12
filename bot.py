import discord
from discord import app_commands
from discord.ext import commands
import logging
from config import config
from downloader import Downloader, DownloadError
from embeds import build_music_embed
from utils import cleanup_temp_dir
import os

logger = logging.getLogger(__name__)

class MusicBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)
        self.downloader = Downloader()

    async def setup_hook(self):
        # Sync slash commands globally (or to a specific guild if set)
        if config.GUILD_ID:
            guild = discord.Object(id=config.GUILD_ID)
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
        else:
            await self.tree.sync()

bot = MusicBot()

@bot.tree.command(name="music", description="Download audio from YouTube or search for a song.")
@app_commands.describe(query="Song name, artist, or YouTube URL")
@app_commands.checks.cooldown(config.COOLDOWN_RATE, config.COOLDOWN_PERIOD, key=lambda i: i.user.id)
async def music_slash(interaction: discord.Interaction, query: str):
    await interaction.response.defer(thinking=True)

    try:
        # Use the downloader
        result = await bot.downloader.download(query)
        filepath = result['filepath']
        file_size = result['file_size']
        bitrate = result['bitrate']
        info = result['info']

        # Build embed
        embed = build_music_embed(info, bitrate, file_size)

        # Upload file
        with open(filepath, 'rb') as f:
            discord_file = discord.File(f, filename=os.path.basename(filepath))
            await interaction.followup.send(embed=embed, file=discord_file)

        # Cleanup
        await bot.downloader.cleanup(filepath)

    except DownloadError as e:
        await interaction.followup.send(f"❌ {str(e)}")
    except discord.HTTPException as e:
        if e.status == 413:
            await interaction.followup.send("❌ File too large even after compression. Try a shorter song.")
        else:
            logger.error(f"Discord HTTP error: {e}")
            await interaction.followup.send("❌ An error occurred while uploading.")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        await interaction.followup.send("❌ An unexpected error occurred. Please try again later.")

# Optional fallback prefix command
@bot.command(name="music")
@commands.cooldown(1, config.COOLDOWN_PERIOD, commands.BucketType.user)
async def music_prefix(ctx, *, query):
    # Convert to slash command equivalent by simulating interaction? Better to instruct user to use slash.
    await ctx.send("Please use `/music` instead!")

# Run
if __name__ == "__main__":
    if not config.DISCORD_TOKEN:
        raise ValueError("DISCORD_TOKEN environment variable is not set.")
    bot.run(config.DISCORD_TOKEN)
