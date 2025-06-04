import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Bot configuration
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
COMMAND_PREFIX = os.getenv('COMMAND_PREFIX', '!')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Bot settings
BOT_NAME = "CalorieCountingBot"
BOT_VERSION = "1.0.0"
BOT_DESCRIPTION = "A Discord bot to help track calories and nutrition with AI image recognition"

# Validate required environment variables
if not DISCORD_TOKEN:
    raise ValueError("DISCORD_TOKEN environment variable is not set. Please check your .env file.")

if not GEMINI_API_KEY:
    print("Warning: GEMINI_API_KEY not set. Image recognition features will be disabled.")
