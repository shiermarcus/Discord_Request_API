import os
from dotenv import load_dotenv
import requests
import discord
from discord.ext import commands
import logging 

load_dotenv()
TOKEN = os.getenv("TOKEN")

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')


intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='?', intents=intents)


def get_discord_user(user_id: int | str):
    """Fetch user profile details from Discord API."""
    url = f"https://discord.com/api/v10/users/{user_id}"
    headers = {
        "Authorization": f"Bot {TOKEN}"
    }
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        return res.json()
    return None


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    print("Bot is online! Type '?profile <username>' in Discord.")


@bot.command(name="profile")
async def profile(ctx: commands.Context, *, username: str = None):
    """Usage in Discord: ?profile <username>"""
    if not username:
        await ctx.send("Please provide a username! Example: `?profile sicheezeo`")
        return

    target = username.strip().lstrip("@").lower()
    await ctx.send(f"Searching for **{username}**...")

    found_member = None
    for guild in bot.guilds:
        async for member in guild.fetch_members(limit=None):
            if member.name.lower() == target:
                found_member = member
                break
        if found_member:
            break

    if found_member:
        embed = discord.Embed(
            title=f"Profile: {found_member.name}",
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url=found_member.display_avatar.url)
        embed.add_field(name="Username", value=found_member.name, inline=True)
        embed.add_field(name="Display Name", value=found_member.global_name or found_member.display_name, inline=True)
        embed.add_field(name="User ID", value=str(found_member.id), inline=False)
        embed.add_field(name="Mention", value=found_member.mention, inline=True)
        embed.add_field(name="Tag", value=found_member.discriminator, inline=True)

        user_data = get_discord_user(found_member.id)
        if user_data and user_data.get("banner"):
            banner_hash = user_data["banner"]
            ext = "gif" if banner_hash.startswith("a_") else "png"
            embed.set_image(url=f"https://cdn.discordapp.com/banners/{found_member.id}/{banner_hash}.{ext}?size=1024")

        await ctx.send(embed=embed)
    else:
        await ctx.send(f"User `{username}` was not found in any servers the bot can see.")


bot.run(TOKEN, log_handler=handler, log_level=logging.DEBUG)