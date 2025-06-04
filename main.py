import discord
from discord.ext import commands
import asyncio
import logging
from config import DISCORD_TOKEN, COMMAND_PREFIX, BOT_NAME, BOT_DESCRIPTION
from image_analysis import analyze_food_image, is_image_analysis_available

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
        (f"{COMMAND_PREFIX}analyzeimage", "Analyze food image for calories (attach image)"),
        (f"{COMMAND_PREFIX}ping", "Check bot responsiveness"),
        (f"{COMMAND_PREFIX}info", "Show bot information"),
    ]
    
    for command, description in commands_list:
        embed.add_field(name=command, value=description, inline=False)
    
    # Add image analysis status
    if is_image_analysis_available():
        embed.add_field(
            name="🤖 AI Image Analysis", 
            value="✅ Available - Upload an image with `!analyzeimage`", 
            inline=False
        )
    else:
        embed.add_field(
            name="🤖 AI Image Analysis", 
            value="❌ Unavailable - Gemini API key not configured", 
            inline=False
        )
    
    await ctx.send(embed=embed)

# AI Image Analysis Command
@bot.command(name='analyzeimage', aliases=['analyze', 'scan'])
async def analyze_image(ctx):
    """Analyze a food image to estimate calories and nutrition"""
    
    # Check if image analysis is available
    if not is_image_analysis_available():
        await ctx.send("❌ Image analysis is not available. The bot administrator needs to configure the Gemini API key.")
        return
    
    # Check if an image was attached
    if not ctx.message.attachments:
        embed = discord.Embed(
            title="📸 Image Analysis",
            description="Please attach an image of food to analyze!",
            color=0xff9900
        )
        embed.add_field(
            name="How to use:",
            value=f"1. Upload an image of food\n2. Type `{COMMAND_PREFIX}analyzeimage` in the same message\n3. Wait for AI analysis results",
            inline=False
        )
        embed.set_footer(text="Supported formats: JPG, PNG, GIF, WEBP")
        await ctx.send(embed=embed)
        return
    
    # Get the first attachment
    attachment = ctx.message.attachments[0]
    
    # Check if it's an image
    if not any(attachment.filename.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
        await ctx.send("❌ Please attach a valid image file (JPG, PNG, GIF, or WEBP).")
        return
    
    # Check file size (Discord limit is 25MB, but we'll be conservative)
    if attachment.size > 10 * 1024 * 1024:  # 10MB limit
        await ctx.send("❌ Image file is too large. Please use an image smaller than 10MB.")
        return
    
    # Send thinking message
    thinking_msg = await ctx.send("🤔 Analyzing your food image... This may take a few seconds.")
    
    try:
        # Analyze the image
        result = await analyze_food_image(attachment.url)
        
        # Delete thinking message
        await thinking_msg.delete()
        
        if result.get("error"):
            embed = discord.Embed(
                title="❌ Analysis Failed",
                description=result["error"],
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        # Create result embed
        confidence = result.get("confidence", 0)
        
        # Choose color based on confidence
        if confidence >= 80:
            color = 0x00ff00  # Green - high confidence
            confidence_emoji = "🎯"
        elif confidence >= 60:
            color = 0xffff00  # Yellow - medium confidence  
            confidence_emoji = "⚠️"
        else:
            color = 0xff9900  # Orange - low confidence
            confidence_emoji = "❓"
        
        embed = discord.Embed(
            title=f"🍽️ Food Analysis Results",
            description=f"**{result['food_name']}**",
            color=color
        )
        
        # Add calorie information
        embed.add_field(
            name="🔥 Estimated Calories",
            value=f"**{result['calories']} kcal**",
            inline=True
        )
        
        embed.add_field(
            name=f"{confidence_emoji} Confidence",
            value=f"{confidence}%",
            inline=True
        )
        
        embed.add_field(
            name="📏 Portion Size",
            value=result.get('portion_size', 'Unknown'),
            inline=True
        )
        
        # Add nutritional information if available
        nutrition = result.get('nutritional_info', {})
        if nutrition:
            nutrition_text = []
            for nutrient, amount in nutrition.items():
                if amount and str(amount) != "0":
                    nutrition_text.append(f"**{nutrient.title()}:** {amount}")
            
            if nutrition_text:
                embed.add_field(
                    name="📊 Nutritional Info",
                    value="\n".join(nutrition_text),
                    inline=False
                )
        
        # Add health notes if available
        health_notes = result.get('health_notes', '')
        if health_notes:
            embed.add_field(
                name="💡 Health Notes",
                value=health_notes,
                inline=False
            )
        
        # Add footer with disclaimer
        embed.set_footer(
            text=f"Analyzed by {ctx.author.display_name} | Estimates may vary - consult nutritional labels for accuracy"
        )
        
        # Add thumbnail with the analyzed image
        embed.set_thumbnail(url=attachment.url)
        
        await ctx.send(embed=embed)
        
        # Optionally, add quick reaction buttons to log the calories
        message = await ctx.send(f"Would you like to add these **{result['calories']} calories** to your log?")
        await message.add_reaction("✅")  # Yes
        await message.add_reaction("❌")  # No
        
    except Exception as e:
        # Delete thinking message if it still exists
        try:
            await thinking_msg.delete()
        except:
            pass
        
        logger.error(f"Error in analyze_image command: {e}")
        embed = discord.Embed(
            title="❌ Analysis Error",
            description="An unexpected error occurred while analyzing the image. Please try again.",
            color=0xff0000
        )
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
