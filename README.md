# CalorieCountingBot

A Discord bot designed to help users track their daily calorie intake and nutritional information.

## Features

- 🍎 Track calories for different food items
- 📊 View nutritional information
- 📸 **AI-powered image recognition** for food calorie estimation
- 🔍 **Enhanced analysis** with text descriptions for better accuracy
- 📝 **Text-only estimation** for foods without images
- 🤖 **Google Gemini Vision** integration for accurate food analysis
- 💬 Interactive Discord commands
- 🎯 Easy-to-use command system

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- Discord account
- Discord server where you have permission to add bots
- **Google AI Studio account** (for image recognition features)

### Installation

1. **Clone/Download this repository**

2. **Set up Python virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   # source venv/bin/activate  # On macOS/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create a Discord Bot**
   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Click "New Application"
   - Give your bot a name
   - Go to "Bot" section
   - Copy the bot token

5. **Configure environment variables**
   - Edit the `.env` file
   - Replace `your_bot_token_here` with your actual bot token
   - Get a Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Replace `your_gemini_api_key_here` with your actual Gemini API key
   ```
   DISCORD_TOKEN=your_actual_bot_token_here
   COMMAND_PREFIX=!
   GEMINI_API_KEY=your_actual_gemini_api_key_here
   ```

6. **Invite bot to your server**
   - In Discord Developer Portal, go to "OAuth2" > "URL Generator"
   - Select "bot" scope
   - Select necessary permissions (Send Messages, Read Message History, etc.)
   - Use the generated URL to invite the bot to your server

7. **Run the bot**
   ```bash
   python main.py
   ```

## Available Commands

### Basic Commands
- `!ping` - Check if bot is responsive
- `!info` - Display bot information
- `!addcalories <calories> [food_name]` - Add calories for a food item
- `!calorie-help` - Show all calorie tracking commands
- `!help` - Show all available commands

### AI-Powered Food Analysis
- `!analyzeimage` - Analyze food image for calorie estimation (attach image)
- `!analyzefood [description]` - **Enhanced analysis** with measurements (e.g., "350g chicken and salad")
- `!estimate <description>` - **Text-only** calorie estimation (no image needed)
- `!testapi` - Test if Gemini AI is working properly

### Advanced Food Analysis Features

#### 1. **Image-Only Analysis** (`!analyzeimage`)
Upload any food image to get:
- 🔥 **Calorie estimation** based on visible portion
- 📊 **Nutritional breakdown** (protein, carbs, fat, etc.)
- 🎯 **Confidence score** for the analysis
- 📏 **Portion size** estimation
- 💡 **Health notes** and nutritional insights

#### 2. **Enhanced Image + Description Analysis** (`!analyzefood`)
Get **more accurate results** by combining images with descriptions:
- Upload an image **and** provide measurements
- Example: `!analyzefood 350g grilled chicken breast with 2 cups rice`
- Higher confidence scores due to specific measurements
- Better portion size accuracy

#### 3. **Text-Only Estimation** (`!estimate`)
Get calorie estimates without images:
- Perfect for homemade meals or when you can't take photos
- Example: `!estimate 1 cup oatmeal with banana and honey`
- Includes nutritional breakdown and health insights

## Example Usage

### Basic Calorie Tracking
```
!addcalories 250 Apple
!addcalories 150 Banana
!ping
!info
```

### AI Food Analysis Examples

#### Image Analysis
1. **Upload a photo of your meal** → `!analyzeimage`
2. **Get instant calorie estimate** → "Grilled chicken breast: ~300 calories"
3. **View nutritional breakdown** → Protein: 45g, Carbs: 0g, Fat: 8g
4. **Add to your log** → React with ✅ to add calories automatically

#### Enhanced Analysis (Image + Description)
1. **Upload photo + description** → `!analyzefood 350g salmon with vegetables`
2. **Get enhanced accuracy** → Higher confidence due to specific measurements
3. **Better nutritional info** → More precise calculations based on weight

#### Text-Only Analysis
1. **Describe your food** → `!estimate 2 slices whole wheat toast with peanut butter`
2. **Get instant estimate** → "Whole wheat toast with peanut butter: ~320 calories"
3. **No image needed** → Perfect for quick logging

## Project Structure

```
CalorieCountingBot/
├── main.py              # Main bot file
├── config.py            # Configuration settings
├── requirements.txt     # Python dependencies
├── .env                # Environment variables (keep private!)
├── .gitignore          # Git ignore file
├── README.md           # This file
└── venv/               # Virtual environment
```

## Development

To extend the bot with more features:

1. Add new commands in `main.py`
2. Update configuration in `config.py`
3. Install additional dependencies in `requirements.txt`

## Security Notes

- Never commit your `.env` file to version control
- Keep your Discord bot token private
- Regularly rotate your bot token if needed

## Troubleshooting

### Common Issues

1. **Bot doesn't respond**
   - Check if bot token is correct in `.env`
   - Ensure bot has necessary permissions in Discord server
   - Check if bot is online in Discord

2. **Import errors**
   - Make sure virtual environment is activated
   - Install all dependencies: `pip install -r requirements.txt`

3. **Permission errors**
   - Ensure bot has "Send Messages" and "Read Message History" permissions
   - Check channel-specific permissions

## Contributing

Feel free to contribute by:
- Adding new features
- Fixing bugs
- Improving documentation
- Suggesting enhancements

## License

This project is open source and available under the MIT License.
