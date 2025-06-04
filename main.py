import discord
from discord.ext import commands
import asyncio
import logging
from config import DISCORD_TOKEN, COMMAND_PREFIX, BOT_NAME, BOT_DESCRIPTION

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot setup with intents
intents = discord.Intents.default()
intents.message_content = True  # Required for reading message content
intents.guilds = True

# Create bot instance
bot = commands.Bot(
    command_prefix=COMMAND_PREFIX,
    description=BOT_DESCRIPTION,
    intents=intents,
    help_command=commands.DefaultHelpCommand()
)

@bot.event
async def on_ready():
    """Event triggered when the bot is ready"""
    logger.info(f'{BOT_NAME} has logged in as {bot.user}!')
    logger.info(f'Bot ID: {bot.user.id}')
    logger.info(f'Connected to {len(bot.guilds)} guilds')
    
    # Set bot status
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="your calories 🍎"
        )
    )

@bot.event
async def on_command_error(ctx, error):
    """Global error handler for commands"""
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Command not found! Use `!help` to see available commands.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Missing required argument: {error.param}")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ Invalid argument provided!")
    else:
        logger.error(f"Unexpected error: {error}")
        await ctx.send("❌ An unexpected error occurred!")

# Basic Commands
@bot.command(name='ping')
async def ping(ctx):
    """Check if the bot is responsive"""
    latency = round(bot.latency * 1000)
    await ctx.send(f'🏓 Pong! Latency: {latency}ms')

@bot.command(name='info')
async def info(ctx):
    """Display bot information"""
    embed = discord.Embed(
        title=f"ℹ️ {BOT_NAME} Information",
        description=BOT_DESCRIPTION,
        color=0x00ff00
    )
    embed.add_field(name="Servers", value=len(bot.guilds), inline=True)
    embed.add_field(name="Users", value=len(bot.users), inline=True)
    embed.add_field(name="Prefix", value=COMMAND_PREFIX, inline=True)
    embed.set_footer(text="Made with discord.py")
    
    await ctx.send(embed=embed)

# Calorie tracking commands (basic examples)
@bot.command(name='addcalories', aliases=['add'])
async def add_calories(ctx, calories: int, *, food_name="Unknown food"):
    """Add calories for a food item"""
    if calories <= 0:
        await ctx.send("❌ Calories must be a positive number!")
        return
    
    embed = discord.Embed(
        title="✅ Calories Added",
        description=f"Added **{calories}** calories for **{food_name}**",
        color=0x00ff00
    )
    embed.set_footer(text=f"Logged by {ctx.author.display_name}")
    
    await ctx.send(embed=embed)

@bot.command(name='calorie-help', aliases=['chelp'])
async def calorie_help(ctx):
    """Show calorie tracking commands"""
    embed = discord.Embed(
        title="🍎 Calorie Tracking Commands",
        description="Here are the available calorie tracking commands:",
        color=0x0099ff
    )
    
    commands_list = [
        (f"{COMMAND_PREFIX}addcalories <calories> [food_name]", "Add calories for a food item"),
        (f"{COMMAND_PREFIX}ping", "Check bot responsiveness"),
        (f"{COMMAND_PREFIX}info", "Show bot information"),
    ]
    
    for command, description in commands_list:
        embed.add_field(name=command, value=description, inline=False)
    
    await ctx.send(embed=embed)

async def main():
    """Main function to run the bot"""
    try:
        await bot.start(DISCORD_TOKEN)
    except discord.LoginFailure:
        logger.error("Invalid bot token! Please check your .env file.")
    except Exception as e:
        logger.error(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())
