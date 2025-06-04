# CalorieCountingBot

A Discord bot designed to help users track their daily calorie intake and nutritional information.

## Features

- 🍎 Track calories for different food items
- 📊 View nutritional information
- 💬 Interactive Discord commands
- 🎯 Easy-to-use command system

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- Discord account
- Discord server where you have permission to add bots

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
   ```
   DISCORD_TOKEN=your_actual_bot_token_here
   COMMAND_PREFIX=!
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

- `!ping` - Check if bot is responsive
- `!info` - Display bot information
- `!addcalories <calories> [food_name]` - Add calories for a food item
- `!calorie-help` - Show all calorie tracking commands
- `!help` - Show all available commands

## Example Usage

```
!addcalories 250 Apple
!addcalories 150 Banana
!ping
!info
```

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
