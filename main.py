from src.music.MusicBot import music_cog
import discord
from discord.ext import commands
import asyncio
import load_dotenv
import os

intents = discord.Intents.default()
intents.message_content = True

load_dotenv.load_dotenv()
Token = os.getenv("DISCORD_TOKEN")

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or("!"),
    intents=intents,
)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} - {bot.user.id}')
    print('------')
@bot.event
async def CheckError(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Command not found")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Missing arguments")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have the required permissions to use this command")
    elif isinstance(error, commands.NotOwner):
        await ctx.send("You don't have the required permissions to use this command")
    elif isinstance(error, commands.MissingRole):
        await ctx.send("You don't have the required permissions to use this command")
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send("I don't have the required permissions to use this command")
    elif isinstance(error, commands.NoPrivateMessage):
        await ctx.send("This command can't be used in DMs")
    elif isinstance(error, commands.PrivateMessageOnly):
        await ctx.send("This command can only be used in DMs")
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send("This command is on cooldown, please retry in a few seconds")
    elif isinstance(error, commands.DisabledCommand):
        await ctx.send("This command is disabled and can't be used")
    elif isinstance(error, commands.TooManyArguments):
        await ctx.send("Too many arguments")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Bad argument")
    elif isinstance(error, commands.CommandInvokeError):
        await ctx.send("An error occured while executing the command")
    elif isinstance(error, commands.CheckFailure):
        await ctx.send("You don't have the required permissions to use this command")
    elif isinstance(error, commands.CommandError):
        await ctx.send("An error occured while executing the command")
    else:
        await ctx.send("An error occured while executing the command")

async def main():
    async with bot:
        await bot.add_cog(music_cog(bot))
        await bot.start(Token)


asyncio.run(main())