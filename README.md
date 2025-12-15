# OSINT Telegram Bot

A powerful Telegram bot for OSINT (Open Source Intelligence) operations with phone number and vehicle number lookup capabilities.

## Features

- 🔥 Animated hacker-style interface with progress bar
- 📱 Phone number OSINT using `/num` command
- 🚗 Vehicle number OSINT using `/veh` command
- 📊 Daily search limit (50 searches per user)
- 🔐 Channel join verification system
- 📢 Owner broadcast functionality (text and media)
- 💾 User data storage in JSON format

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure the Bot

Edit `osint_bot.py` and update the following variables:

```python
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # Get from @BotFather
OWNER_ID = YOUR_OWNER_ID_HERE  # Your Telegram user ID
CHANNEL_1 = "@channel1"  # First channel username
CHANNEL_2 = "@channel2"  # Second channel username
```

### 3. Get Bot Token

1. Open Telegram and search for `@BotFather`
2. Send `/newbot` command
3. Follow the instructions to create your bot
4. Copy the bot token and paste it in `BOT_TOKEN`

### 4. Get Your User ID

1. Search for `@userinfobot` on Telegram
2. Start a conversation with it
3. It will send you your user ID
4. Copy and paste it in `OWNER_ID`

### 5. Setup Channels

1. Create two public Telegram channels
2. Add your bot as an administrator to both channels
3. Update `CHANNEL_1` and `CHANNEL_2` with the channel usernames

### 6. Run the Bot

```bash
python osint_bot.py
```

## Commands

### User Commands

- `/start` - Start the bot and see the animated menu
- `/num <phone_number>` - Search for phone number information
  - Example: `/num 9876543210`
- `/veh <vehicle_number>` - Search for vehicle information
  - Example: `/veh HR26EV0001`
- `/stats` - View your search statistics

### Owner Commands

- `/broadcast <message>` - Broadcast a message to all users
- Reply to any media with caption to broadcast media to all users

## API Endpoints

- Phone OSINT: `https://danger-vip-key.shop/api.php?key=CyberXWorm&number=<number>`
- Vehicle OSINT: `http://india.42web.io/vehicle/?q=<vehicle_number>`

## Daily Limits

- Each user gets 50 searches per day (combined for both APIs)
- Limits reset at midnight
- Users must join both channels to use the bot

## File Structure

```
.
├── osint_bot.py      # Main bot script
├── requirements.txt  # Python dependencies
├── users.json        # User data storage (auto-created)
└── README.md         # This file
```

## Notes

- The bot stores user data in `users.json`
- All responses include watermark: `@Everyonesking`
- Large JSON responses are sent as files
- The bot checks channel membership before allowing searches

## Troubleshooting

1. **Bot not responding**: Check if bot token is correct
2. **Channel verification fails**: Make sure bot is admin in both channels
3. **API errors**: Check if API endpoints are accessible
4. **Permission errors**: Ensure bot has necessary permissions in channels

## Disclaimer

This bot is for educational and authorized OSINT purposes only. Use responsibly and in compliance with applicable laws and regulations.

