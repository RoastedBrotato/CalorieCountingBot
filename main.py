import discord
from discord.ext import commands
import asyncio
import logging
import json
import os
from datetime import datetime, date
from config import DISCORD_TOKEN, COMMAND_PREFIX, BOT_NAME, BOT_DESCRIPTION
from image_analysis import analyze_food_image, analyze_food_with_description, is_image_analysis_available, test_gemini_api

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simple in-memory calorie tracking (you could enhance this with a database)
user_calories = {}
CALORIES_FILE = "user_calories.json"

def load_calories_data():
    """Load calorie data from file"""
    global user_calories
    try:
        if os.path.exists(CALORIES_FILE):
            with open(CALORIES_FILE, 'r') as f:
                user_calories = json.load(f)
    except Exception as e:
        logger.error(f"Error loading calories data: {e}")
        user_calories = {}

def save_calories_data():
    """Save calorie data to file"""
    try:
        with open(CALORIES_FILE, 'w') as f:
            json.dump(user_calories, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving calories data: {e}")

def add_user_calories(user_id: int, calories: int, food_name: str):
    """Add calories for a user"""
    user_id_str = str(user_id)
    today = str(date.today())
    
    if user_id_str not in user_calories:
        user_calories[user_id_str] = {}
    
    if today not in user_calories[user_id_str]:
        user_calories[user_id_str][today] = {
            "total_calories": 0,  
            "foods": []
        }
    
    user_calories[user_id_str][today]["total_calories"] += calories
    user_calories[user_id_str][today]["foods"].append({
        "name": food_name,
        "calories": calories,
        "timestamp": datetime.now().isoformat()
    })
    
    save_calories_data()
    return user_calories[user_id_str][today]["total_calories"]

def get_user_daily_calories(user_id: int):
    """Get user's calories for today"""
    user_id_str = str(user_id)
    today = str(date.today())
    
    if user_id_str in user_calories and today in user_calories[user_id_str]:
        return user_calories[user_id_str][today]
    return {"total_calories": 0, "foods": []}

# Bot setup with intents
intents = discord.Intents.default()
intents.message_content = True  # Required for reading message content
intents.guilds = True
intents.reactions = True  # Required for reaction events

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
    
    # Load calorie data
    load_calories_data()
    
    # Set bot status
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="your calories 🍎"
        )
    )

@bot.event
async def on_reaction_add(ctx, user):
    """Handle when users react to messages"""
    # Ignore reactions from the bot itself
    if user == bot.user:
        return
    
    # Check if the reaction is on a message from the bot
    if ctx.message.author != bot.user:
        return
    
    # Check if it's a calorie analysis message (has an embed with "Food Analysis Results" in title)
    if not ctx.message.embeds:
        return
    
    embed = ctx.message.embeds[0]
    if "Food Analysis Results" not in embed.title:
        return
    
    # Handle the reaction
    if str(ctx.emoji) == "✅":
        await handle_add_calories_reaction(ctx, user, embed)
    elif str(ctx.emoji) == "❌":
        await handle_decline_calories_reaction(ctx, user)

async def handle_add_calories_reaction(ctx, user, embed):
    """Handle when user clicks ✅ to add calories"""
    try:
        # Extract calories from the embed
        calories_field = None
        for field in embed.fields:
            if "Estimated Calories" in field.name:
                calories_field = field.value
                break
        
        if not calories_field:
            return
        
        # Extract the numeric value (e.g., "**450 kcal**" -> 450)
        import re
        calories_match = re.search(r'\*\*(\d+)\s*kcal\*\*', calories_field)
        if not calories_match:
            return
        
        calories = int(calories_match.group(1))
        
        # Extract food name from embed title or description
        food_name = embed.description.strip('**') if embed.description else "Unknown food"
        
        # Add calories to user's daily total
        total_today = add_user_calories(user.id, calories, food_name)
        
        # Send confirmation message
        confirmation_embed = discord.Embed(
            title="✅ Calories Added!",
            description=f"Added **{calories} kcal** for **{food_name}**",
            color=0x00ff00
        )
        confirmation_embed.add_field(
            name="📊 Today's Total",
            value=f"**{total_today} kcal**",
            inline=True
        )
        confirmation_embed.set_footer(text=f"Logged for {user.display_name}")
        
        # Send as a reply to the original message or in the same channel
        await ctx.message.channel.send(embed=confirmation_embed)
        
        logger.info(f"Added {calories} calories for user {user.id} ({user.display_name})")
        
    except Exception as e:
        logger.error(f"Error handling add calories reaction: {e}")
        await ctx.message.channel.send("❌ Error adding calories. Please try using the `!addcalories` command instead.")

async def handle_decline_calories_reaction(ctx, user):
    """Handle when user clicks ❌ to decline adding calories"""
    try:
        # Send a simple acknowledgment
        decline_embed = discord.Embed(
            title="❌ Calories Not Added",
            description="No worries! The analysis wasn't added to your daily total.",
            color=0xff6b6b
        )
        decline_embed.set_footer(text=f"Declined by {user.display_name}")
        
        # Send as a reply to the original message or in the same channel  
        await ctx.message.channel.send(embed=decline_embed)
        
        logger.info(f"User {user.id} ({user.display_name}) declined adding calories")
        
    except Exception as e:
        logger.error(f"Error handling decline calories reaction: {e}")

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

# Calorie tracking commands
@bot.command(name='addcalories', aliases=['add'])
async def add_calories(ctx, calories: int, *, food_name="Unknown food"):
    """Add calories for a food item"""
    if calories <= 0:
        await ctx.send("❌ Calories must be a positive number!")
        return
    
    # Add to user's daily total
    total_today = add_user_calories(ctx.author.id, calories, food_name)
    
    embed = discord.Embed(
        title="✅ Calories Added",
        description=f"Added **{calories}** calories for **{food_name}**",
        color=0x00ff00
    )
    embed.add_field(
        name="📊 Today's Total",
        value=f"**{total_today} kcal**", 
        inline=True
    )
    embed.set_footer(text=f"Logged by {ctx.author.display_name}")
    
    await ctx.send(embed=embed)

@bot.command(name='today', aliases=['daily', 'calories'])
async def view_today_calories(ctx):
    """View your calories for today"""
    daily_data = get_user_daily_calories(ctx.author.id)
    total_calories = daily_data["total_calories"]
    foods = daily_data["foods"]
    
    embed = discord.Embed(
        title=f"📊 {ctx.author.display_name}'s Calories Today",
        description=f"**Total: {total_calories} kcal**",
        color=0x0099ff
    )
    
    if foods:
        food_list = []
        # Show last 10 entries with numbers for easy reference
        display_foods = foods[-10:]
        start_index = max(0, len(foods) - 10)
        
        for i, food in enumerate(display_foods, start=start_index + 1):
            time_str = datetime.fromisoformat(food["timestamp"]).strftime("%H:%M")
            food_list.append(f"`{i}.` `{time_str}` **{food['name']}** - {food['calories']} kcal")
        
        embed.add_field(
            name="🍽️ Recent Foods",
            value="\n".join(food_list),
            inline=False
        )
        
        if len(foods) > 10:
            embed.set_footer(text=f"Showing last 10 of {len(foods)} entries • Use !history for all entries • Use !remove <#> to delete entries")
        else:
            embed.set_footer(text="Use !remove <#> to delete entries • Use !history for detailed view")
    else:
        embed.add_field(
            name="🍽️ No foods logged today",
            value="Use `!addcalories` or analyze food images to start tracking!",
            inline=False
        )
    
    await ctx.send(embed=embed)

@bot.command(name='reset', aliases=['clear'])
async def reset_today_calories(ctx):
    """Reset your calories for today (with confirmation)"""
    daily_data = get_user_daily_calories(ctx.author.id)
    
    if daily_data["total_calories"] == 0:
        await ctx.send("❌ You have no calories logged for today!")
        return
    
    embed = discord.Embed(
        title="⚠️ Reset Today's Calories?",
        description=f"Are you sure you want to reset your **{daily_data['total_calories']} kcal** for today?",
        color=0xff9900
    )
    embed.add_field(
        name="⚡ This action cannot be undone",
        value="React with ✅ to confirm or ❌ to cancel",
        inline=False
    )
    
    message = await ctx.send(embed=embed)
    await message.add_reaction("✅")
    await message.add_reaction("❌")
    
    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in ["✅", "❌"] and reaction.message.id == message.id
    
    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=check)
        
        if str(reaction.emoji) == "✅":
            # Reset user's data for today
            user_id_str = str(ctx.author.id)
            today = str(date.today())
            
            if user_id_str in user_calories and today in user_calories[user_id_str]:
                del user_calories[user_id_str][today]
                save_calories_data()
            
            embed = discord.Embed(
                title="✅ Calories Reset",
                description="Your calories for today have been reset to 0.",
                color=0x00ff00
            )
            await message.edit(embed=embed)
            await message.clear_reactions()
        else:
            embed = discord.Embed(
                title="❌ Reset Cancelled",
                description="Your calories were not reset.",
                color=0xff6b6b
            )
            await message.edit(embed=embed)
            await message.clear_reactions()
            
    except asyncio.TimeoutError:
        embed = discord.Embed(
            title="⏰ Reset Timed Out",
            description="Reset cancelled due to timeout.",
            color=0x666666
        )
        await message.edit(embed=embed)
        await message.clear_reactions()

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
        (f"{COMMAND_PREFIX}today", "View your calories for today"),
        (f"{COMMAND_PREFIX}history", "View all your calorie entries for today"),
        (f"{COMMAND_PREFIX}remove <#>", "Remove a specific calorie entry by number"),
        (f"{COMMAND_PREFIX}edit <#> <calories> [new_name]", "Edit a calorie entry"),
        (f"{COMMAND_PREFIX}reset", "Reset your calories for today (with confirmation)"),
        (f"{COMMAND_PREFIX}analyzeimage", "Analyze food image for calories (attach image)"),
        (f"{COMMAND_PREFIX}analyzefood [description]", "Enhanced analysis with measurements (e.g., '350g chicken')"),
        (f"{COMMAND_PREFIX}estimate <description>", "Text-only calorie estimation (no image needed)"),
        (f"{COMMAND_PREFIX}testapi", "Test if Gemini AI is working properly"),
        (f"{COMMAND_PREFIX}ping", "Check bot responsiveness"),
        (f"{COMMAND_PREFIX}info", "Show bot information"),
    ]
    
    for command, description in commands_list:
        embed.add_field(name=command, value=description, inline=False)
        
    # Add reaction instructions
    embed.add_field(
        name="🔥 Quick Logging",
        value="After AI analysis, react with ✅ to add calories or ❌ to decline",
        inline=False
    )
        
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

# API Test Command
@bot.command(name='testapi', aliases=['test'])
async def test_api(ctx):
    """Test if the Gemini API is working properly"""
    thinking_msg = await ctx.send("🧪 Testing Gemini API connection...")
    
    try:
        result = await test_gemini_api()
        await thinking_msg.delete()
        
        if result["status"] == "success":
            embed = discord.Embed(
                title="✅ API Test Successful",
                description="Gemini AI is working correctly!",
                color=0x00ff00
            )
            embed.add_field(
                name="Response",
                value=result.get("response", "API responded successfully"),
                inline=False
            )
            embed.add_field(
                name="Status",
                value="🟢 Ready for image analysis",
                inline=False
            )
        else:
            embed = discord.Embed(
                title="❌ API Test Failed",
                description=result["message"],
                color=0xff0000
            )
            if "help_url" in result:
                embed.add_field(
                    name="🔑 Get API Key",
                    value=f"[Google AI Studio]({result['help_url']})",
                    inline=False
                )
            embed.add_field(
                name="💡 Next Steps",
                value="1. Get a new API key from Google AI Studio\n2. Update your `.env` file\n3. Restart the bot\n4. Run `!testapi` again",
                inline=False
            )
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        try:
            await thinking_msg.delete()
        except:
            pass
        
        embed = discord.Embed(
            title="❌ Test Error",
            description=f"An error occurred while testing: {str(e)}",
            color=0xff0000
        )
        await ctx.send(embed=embed)

# AI Image Analysis Command
@bot.command(name='analyzeimage', aliases=['analyze', 'scan'])
async def analyze_image(ctx):
    """Analyze a food image to estimate calories and nutrition"""
    
    logger.info(f"analyzeimage command called by {ctx.author.display_name} ({ctx.author.id})")
    
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
        logger.info(f"Starting analysis for image: {attachment.filename}")
        
        # Analyze the image
        result = await analyze_food_image(attachment.url)
        
        logger.info(f"Analysis completed, deleting thinking message")
        
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
        
        logger.info(f"Creating result embed for {result.get('food_name', 'Unknown')} - {result.get('calories', 0)} kcal")
        
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
          # Add footer with disclaimer and reaction instructions
        embed.set_footer(
            text=f"Analyzed by {ctx.author.display_name} • React with ✅ to log calories • Estimates may vary - consult nutritional labels for accuracy"
        )
        
        # Add thumbnail with the analyzed image
        embed.set_thumbnail(url=attachment.url)
        
        logger.info(f"Sending result message...")
        
        # Send the main result with embedded reactions
        result_message = await ctx.send(embed=embed)
        
        logger.info(f"Result message sent, adding reactions...")
        
        # Add reaction buttons to the main message instead of creating a separate one
        await result_message.add_reaction("✅")  # Yes, add calories
        await result_message.add_reaction("❌")  # No, don't add
        
        logger.info(f"Reactions added successfully")
        
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

# Enhanced AI Image Analysis Command with Description
@bot.command(name='analyzefood', aliases=['afood', 'describe'])
async def analyze_food_with_desc(ctx, *, description: str = None):
    """Analyze a food image with optional description for enhanced accuracy (e.g., '350g chicken and salad')"""
    
    # Check if image analysis is available
    if not is_image_analysis_available():
        await ctx.send("❌ Image analysis is not available. The bot administrator needs to configure the Gemini API key.")
        return
    
    # Check if an image was attached
    if not ctx.message.attachments:
        embed = discord.Embed(
            title="📸 Enhanced Food Analysis",
            description="Please attach an image of food to analyze!",
            color=0xff9900
        )
        embed.add_field(
            name="How to use:",
            value=f"1. Upload an image of food\n2. Type `{COMMAND_PREFIX}analyzefood [description]` in the same message\n3. Include measurements like '350g chicken' for better accuracy\n4. Wait for AI analysis results",
            inline=False
        )
        embed.add_field(
            name="Example:",
            value=f"`{COMMAND_PREFIX}analyzefood 2 cups of rice with 150g grilled salmon`",
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
    
    # Import the enhanced analysis function
    from image_analysis import analyze_food_with_description
    
    # Create status message based on whether description was provided
    status_msg = f"🤔 Analyzing your food image"
    if description:
        status_msg += f" with description: '{description[:50]}{'...' if len(description) > 50 else ''}'"
    status_msg += "... This may take a few seconds."
    
    thinking_msg = await ctx.send(status_msg)
    
    try:
        # Analyze the image with optional description
        result = await analyze_food_with_description(attachment.url, description)
        
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
        
        # Create enhanced result embed
        confidence = result.get("confidence", 0)
        
        # Choose color based on confidence (enhanced accuracy should have higher confidence)
        if confidence >= 85:
            color = 0x00aa00  # Darker green - very high confidence
            confidence_emoji = "🎯"
        elif confidence >= 70:
            color = 0x00ff00  # Green - high confidence
            confidence_emoji = "✅"
        elif confidence >= 50:
            color = 0xffff00  # Yellow - medium confidence  
            confidence_emoji = "⚠️"
        else:
            color = 0xff9900  # Orange - low confidence
            confidence_emoji = "❓"
        
        # Title changes based on whether description was used
        title = "🍽️ Enhanced Food Analysis Results" if result.get("user_description_used") else "🍽️ Food Analysis Results"
        
        embed = discord.Embed(
            title=title,
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
        
        # Show if user description was used and accuracy
        if result.get("user_description_used"):
            description_accuracy = result.get("description_accuracy", "")
            accuracy_emoji = {
                "good": "✅",
                "partial": "⚠️", 
                "poor": "❌"
            }.get(description_accuracy.lower(), "ℹ️")
            
            embed.add_field(
                name="📝 Description Used",
                value=f"{accuracy_emoji} {description_accuracy.title() if description_accuracy else 'Yes'} match with image",
                inline=True
            )
            
            embed.add_field(
                name="💬 Your Description",
                value=f"*{result.get('original_description', 'N/A')}*",
                inline=False
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
          # Enhanced footer with reaction instructions
        footer_text = f"Analyzed by {ctx.author.display_name}"
        if result.get("user_description_used"):
            footer_text += " • Enhanced with description"
        footer_text += " • React with ✅ to log calories • Estimates may vary - consult nutritional labels for accuracy"
        embed.set_footer(text=footer_text)
        
        # Add thumbnail with the analyzed image
        embed.set_thumbnail(url=attachment.url)
        
        # Send the main result with embedded reactions
        result_message = await ctx.send(embed=embed)
        
        # Add reaction buttons to the main message instead of creating a separate one
        await result_message.add_reaction("✅")  # Yes, add calories
        await result_message.add_reaction("❌")  # No, don't add
        
    except Exception as e:
        # Delete thinking message if it still exists
        try:
            await thinking_msg.delete()
        except:
            pass
        
        logger.error(f"Error in analyze_food_with_desc command: {e}")
        embed = discord.Embed(
            title="❌ Analysis Error",
            description="An unexpected error occurred while analyzing the image. Please try again.",
            color=0xff0000
        )
        await ctx.send(embed=embed)

# Text-only food analysis command
@bot.command(name='estimate', aliases=['calc'])
async def estimate_calories(ctx, *, description: str):
    """Estimate calories from text description only (e.g., '2 cups rice, 150g chicken breast')"""
    
    logger.info(f"Estimate command called by {ctx.author} with description: '{description[:50]}...'")
    
    # Check if image analysis is available (we use the same API)
    if not is_image_analysis_available():
        await ctx.send("❌ Calorie estimation is not available. The bot administrator needs to configure the Gemini API key.")
        return
    
    if not description.strip():
        embed = discord.Embed(
            title="📝 Text-based Calorie Estimation",
            description="Please provide a description of the food!",
            color=0xff9900
        )
        embed.add_field(
            name="How to use:",
            value=f"`{COMMAND_PREFIX}estimate 2 cups of rice with 150g grilled chicken`",
            inline=False
        )
        embed.add_field(
            name="Tips for accuracy:",
            value="• Include measurements (grams, cups, pieces)\n• Specify cooking method (grilled, fried, etc.)\n• Mention any sauces or additions",
            inline=False
        )
        await ctx.send(embed=embed)
        return
    
    thinking_msg = await ctx.send(f"🤔 Analyzing food description: '{description[:100]}{'...' if len(description) > 100 else ''}'")
    
    try:
        # Use Gemini for text-only analysis
        import google.generativeai as genai
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
        Analyze this food description and provide nutritional breakdown: "{description}"

        Please respond in this exact JSON format:

        {{
            "food_name": "summary of the food items mentioned",
            "estimated_calories": number (total calories for all items described),
            "confidence": number between 0-100 (confidence in text-based estimation),
            "portion_size": "summary of portions mentioned",
            "analysis_method": "text-only",
            "nutritional_info": {{
                "protein": "amount in grams",
                "carbohydrates": "amount in grams", 
                "fat": "amount in grams",
                "fiber": "amount in grams",
                "sugar": "amount in grams"
            }},
            "health_notes": "brief nutritional assessment",
            "interpretation": "how you interpreted the user's description"
        }}

        Guidelines:
        - Base calculations on standard nutritional databases (USDA, etc.)
        - If measurements are vague, estimate standard portions
        - Consider cooking methods for calorie adjustments
        - Be conservative with confidence if description is unclear
        - Note any assumptions made in the interpretation field
        """
        
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Delete thinking message
        await thinking_msg.delete()
        
        # Parse JSON response
        import json
        try:
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            elif "{" in response_text and "}" in response_text:
                json_start = response_text.find("{")
                json_end = response_text.rfind("}") + 1
                json_text = response_text[json_start:json_end]
            else:
                json_text = response_text
            
            result = json.loads(json_text)
            
            # Create result embed
            confidence = result.get("confidence", 0)
            
            # Color based on confidence
            if confidence >= 75:
                color = 0x00ff00  # Green
                confidence_emoji = "✅"
            elif confidence >= 50:
                color = 0xffff00  # Yellow
                confidence_emoji = "⚠️"
            else:
                color = 0xff9900  # Orange
                confidence_emoji = "❓"
            
            embed = discord.Embed(
                title="📝 Text-based Calorie Estimation",
                description=f"**{result['food_name']}**",
                color=color
            )
            
            embed.add_field(
                name="🔥 Estimated Calories",
                value=f"**{result['estimated_calories']} kcal**",
                inline=True
            )
            
            embed.add_field(
                name=f"{confidence_emoji} Confidence",
                value=f"{confidence}%",
                inline=True
            )
            
            embed.add_field(
                name="📏 Portion Summary",
                value=result.get('portion_size', 'See description'),
                inline=True
            )
            
            embed.add_field(
                name="💭 Your Description",
                value=f"*{description}*",
                inline=False
            )
            
            # Add interpretation if available
            interpretation = result.get('interpretation', '')
            if interpretation:
                embed.add_field(
                    name="🧠 AI Interpretation",
                    value=interpretation,
                    inline=False
                )
            
            # Add nutritional info
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
              # Add health notes
            health_notes = result.get('health_notes', '')
            if health_notes:
                embed.add_field(
                    name="💡 Health Notes",
                    value=health_notes,
                    inline=False
                )
            
            embed.set_footer(text=f"Text-based analysis by {ctx.author.display_name} • React with ✅ to log calories • For better accuracy, use !analyzefood with an image")
            
            # Send the main result
            result_message = await ctx.send(embed=embed)
            
            # Add reaction buttons to the main message instead of creating a separate one
            await result_message.add_reaction("✅")  # Yes, add calories
            await result_message.add_reaction("❌")  # No, don't add
            
        except json.JSONDecodeError:
            embed = discord.Embed(
                title="❌ Analysis Error",
                description="Could not parse the analysis results. Please try rephrasing your description.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            
    except Exception as e:
        try:
            await thinking_msg.delete()
        except:
            pass
        
        logger.error(f"Error in estimate_calories command: {e}")
        embed = discord.Embed(
            title="❌ Estimation Error",
            description="An error occurred while analyzing your description. Please try again.",
            color=0xff0000
        )
        await ctx.send(embed=embed)

@bot.command(name='remove', aliases=['delete', 'del'])
async def remove_calorie_entry(ctx, entry_number: int):
    """Remove a specific calorie entry by number (use !today to see numbers)"""
    user_id_str = str(ctx.author.id)
    today = str(date.today())
    
    # Check if user has any entries today
    if user_id_str not in user_calories or today not in user_calories[user_id_str]:
        await ctx.send("❌ You have no calorie entries for today!")
        return
    
    foods = user_calories[user_id_str][today]["foods"]
    
    # Check if entry number is valid
    if entry_number < 1 or entry_number > len(foods):
        await ctx.send(f"❌ Invalid entry number! You have {len(foods)} entries. Use `!today` to see them.")
        return
    
    # Get the entry to remove (convert to 0-based index)
    entry_to_remove = foods[entry_number - 1]
    removed_calories = entry_to_remove["calories"]
    removed_food = entry_to_remove["name"]
    
    # Remove the entry
    foods.pop(entry_number - 1)
    
    # Update total calories
    user_calories[user_id_str][today]["total_calories"] -= removed_calories
    
    # Save changes
    save_calories_data()
    
    # Send confirmation
    new_total = user_calories[user_id_str][today]["total_calories"]
    embed = discord.Embed(
        title="🗑️ Entry Removed",
        description=f"Removed **{removed_food}** ({removed_calories} kcal)",
        color=0xff6b6b
    )
    embed.add_field(
        name="📊 Updated Total",
        value=f"**{new_total} kcal**",
        inline=True
    )
    embed.set_footer(text=f"Removed by {ctx.author.display_name}")
    
    await ctx.send(embed=embed)

@bot.command(name='history', aliases=['all', 'full'])
async def view_full_history(ctx):
    """View all your calorie entries for today"""
    daily_data = get_user_daily_calories(ctx.author.id)
    total_calories = daily_data["total_calories"]
    foods = daily_data["foods"]
    
    embed = discord.Embed(
        title=f"📈 {ctx.author.display_name}'s Full History Today",
        description=f"**Total: {total_calories} kcal**",
        color=0x9932cc
    )
    
    if foods:
        # Group foods into chunks to avoid Discord message limits
        food_chunks = []
        current_chunk = []
        
        for i, food in enumerate(foods, 1):
            time_str = datetime.fromisoformat(food["timestamp"]).strftime("%H:%M")
            entry = f"`{i}.` `{time_str}` **{food['name']}** - {food['calories']} kcal"
            
            # Check if adding this entry would exceed Discord's field limit
            if len('\n'.join(current_chunk + [entry])) > 1000:
                food_chunks.append(current_chunk)
                current_chunk = [entry]
            else:
                current_chunk.append(entry)
        
        if current_chunk:
            food_chunks.append(current_chunk)
        
        # Add fields for each chunk
        for i, chunk in enumerate(food_chunks):
            field_name = f"🍽️ Foods" if i == 0 else f"🍽️ Foods (continued {i+1})"
            embed.add_field(
                name=field_name,
                value="\n".join(chunk),
                inline=False
            )
        
        embed.set_footer(text=f"Total: {len(foods)} entries • Use !remove <#> to delete entries")
    else:
        embed.add_field(
            name="🍽️ No foods logged today",
            value="Use `!addcalories` or analyze food images to start tracking!",
            inline=False
        )
    
    await ctx.send(embed=embed)

@bot.command(name='edit', aliases=['modify'])
async def edit_calorie_entry(ctx, entry_number: int, new_calories: int, *, new_food_name: str = None):
    """Edit a calorie entry (use !today to see numbers)"""
    user_id_str = str(ctx.author.id)
    today = str(date.today())
    
    # Validate new calories
    if new_calories <= 0:
        await ctx.send("❌ Calories must be a positive number!")
        return
    
    # Check if user has any entries today
    if user_id_str not in user_calories or today not in user_calories[user_id_str]:
        await ctx.send("❌ You have no calorie entries for today!")
        return
    
    foods = user_calories[user_id_str][today]["foods"]
    
    # Check if entry number is valid
    if entry_number < 1 or entry_number > len(foods):
        await ctx.send(f"❌ Invalid entry number! You have {len(foods)} entries. Use `!today` to see them.")
        return
    
    # Get the entry to edit (convert to 0-based index)
    entry_to_edit = foods[entry_number - 1]
    old_calories = entry_to_edit["calories"]
    old_food_name = entry_to_edit["name"]
    
    # Update the entry
    entry_to_edit["calories"] = new_calories
    if new_food_name:
        entry_to_edit["name"] = new_food_name
    entry_to_edit["timestamp"] = datetime.now().isoformat()  # Update timestamp
    
    # Update total calories
    calorie_difference = new_calories - old_calories
    user_calories[user_id_str][today]["total_calories"] += calorie_difference
    
    # Save changes
    save_calories_data()
    
    # Send confirmation
    new_total = user_calories[user_id_str][today]["total_calories"]
    embed = discord.Embed(
        title="✏️ Entry Updated",
        description=f"**Entry #{entry_number}** has been updated",
        color=0x00ff00
    )
    
    changes = []
    if new_food_name and new_food_name != old_food_name:
        changes.append(f"**Food:** {old_food_name} → {new_food_name}")
    if new_calories != old_calories:
        changes.append(f"**Calories:** {old_calories} → {new_calories} kcal")
    
    if changes:
        embed.add_field(
            name="📝 Changes Made",
            value="\n".join(changes),
            inline=False
        )
    
    embed.add_field(
        name="📊 Updated Total",
        value=f"**{new_total} kcal**",
        inline=True
    )
    
    if calorie_difference != 0:
        difference_text = f"+{calorie_difference}" if calorie_difference > 0 else str(calorie_difference)
        embed.add_field(
            name="📈 Change",
            value=f"**{difference_text} kcal**",
            inline=True
        )
    
    embed.set_footer(text=f"Edited by {ctx.author.display_name}")
    
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
