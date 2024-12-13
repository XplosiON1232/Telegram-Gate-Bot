# Telegram Gate Bot

A secure Telegram bot that manages access to private channels through an advanced image-based captcha verification system. Perfect for protecting your community from bots and automated joins while maintaining a user-friendly experience.

## Features

### Advanced Captcha System
- Image-based captcha with distortion lines
- Interactive button-based input system
- 4-character verification code
- Random character positioning and visual noise
- User-friendly input interface with live feedback

### Security Features
- Single-use invite links
- Invite links expire after a set time
- Comprehensive logging system
- Anti-bot protection mechanisms

### Logging System
- Tracks all gate access attempts
- Logs successful verifications
- Records invite link generation
- Maintains user interaction history

## Setup

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
4. Configure your `.env` file with:
   - `BOT_TOKEN`: Your Telegram bot token from @BotFather
   - `PRIVATE_CHANNEL_ID`: ID of your private channel
   - `GATE_LOG_CHANNEL_ID`: Channel ID for logging access attempts
   - `SUCCESS_LOG_CHANNEL_ID`: Channel ID for logging successful entries

5. Make sure the bot has the following permissions in your channel:
   - Admin rights
   - Ability to create invite links
   - Permission to send messages in log channels

6. Run the bot:
   ```bash
   python bot.py
   ```

## Channel Setup and Bot Permissions

### Getting Channel IDs
1. Forward a message from your channel to [@username_to_id_bot](https://t.me/username_to_id_bot)
   - This bot will show you the channel's ID
   - Channel IDs usually start with `-100`
   - Make sure to get IDs for all channels (private channel and log channels)

2. Alternative method:
   - Open your channel in web.telegram.org
   - The URL will look like: `https://web.telegram.org/k/#-1001234567890`
   - The number after `#-` is your channel ID
   - Add `-100` at the start if not present

### Required Bot Setup
1. Create your bot using [@BotFather](https://t.me/BotFather)
   - Use `/newbot` command
   - Choose a name and username
   - Save the bot token for your `.env` file

2. Bot Permissions in Private Channel:
   - Add bot as channel admin
   - Required permissions:
     - Invite Users through Links
     - Manage Chat
     - Delete Messages (recommended)
     - Post Messages (if you want bot announcements)

3. Bot Permissions in Log Channels:
   - Create two separate channels for logging
   - Add bot as admin in both channels
   - Required permissions:
     - Post Messages
     - Manage Chat
   - Make channels private for security

### Channel Privacy Settings
1. Private Channel:
   - Set channel to Private
   - Disable join requests
   - Remove all permanent invite links
   - Let the bot manage all invites

2. Log Channels:
   - Set both channels to Private
   - Add only necessary admins
   - Keep bot as admin

### Testing Setup
1. Remove bot from all channels
2. Add bot back with correct permissions
3. Try the following:
   - Start bot with `/start`
   - Complete captcha verification
   - Check both log channels for messages
   - Try joining with generated invite link
   - Verify link expires and is single-use

### Troubleshooting
- If bot can't send invite links:
  - Verify bot is admin in private channel
  - Check "Invite Users" permission
- If logs aren't appearing:
  - Verify bot is admin in log channels
  - Check "Post Messages" permission
  - Verify channel IDs in `.env` file
- If invite links don't work:
  - Ensure channel is private
  - Check bot's manage chat permissions
  - Verify channel ID format (should start with `-100`)

## User Flow

1. User starts the bot with `/start`
2. Clicks "I'm not a robot" button
3. Receives an image captcha with interactive keyboard
4. Inputs the code using the provided buttons
5. Can clear input or submit when ready
6. Upon successful verification, receives a unique, single-use invite link
7. Link expires after a set time if unused

## Technical Details

### Dependencies
- python-telegram-bot: Telegram API interface
- python-dotenv: Environment variable management
- Pillow: Image generation for captcha
- captcha: Captcha utilities

### Security Measures
- Each invite link is unique and single-use
- Links expire automatically after a set time
- Visual captcha with random noise makes automated solving difficult
- Interactive button system prevents automated text input
- Comprehensive logging for monitoring and security

## Logging Features

The bot maintains two separate logging channels:

### Gate Log Channel
- Records all new user attempts
- Tracks when users start the verification process
- Includes user ID, username, and timestamp

### Success Log Channel
- Records successful verifications
- Tracks generated invite links
- Includes full user details and verification time

## Customization

The bot can be easily customized through environment variables in your `.env` file:

### Captcha Settings
- `CAPTCHA_LENGTH` (default: 4)
  - Number of characters in the captcha
  - Recommended range: 3-6 characters
  - Example: `CAPTCHA_LENGTH=5`

- `DISTORTION_LINES` (default: 8)
  - Number of random lines drawn across the captcha image
  - More lines = harder to read for bots
  - Recommended range: 5-15 lines
  - Example: `DISTORTION_LINES=10`

### Invite Link Settings
- `INVITE_EXPIRE_MINUTES` (default: 60)
  - How long invite links remain valid
  - Value in minutes
  - Example: `INVITE_EXPIRE_MINUTES=30` for 30 minutes
  - Example: `INVITE_EXPIRE_MINUTES=120` for 2 hours

### Example Configuration
```env
# Required Settings
BOT_TOKEN=your_bot_token_here
PRIVATE_CHANNEL_ID=-100xxxxxxxxxx
GATE_LOG_CHANNEL_ID=-100xxxxxxxxxx
SUCCESS_LOG_CHANNEL_ID=-100xxxxxxxxxx

# Customization Options
CAPTCHA_LENGTH=5            # 5 character captcha
DISTORTION_LINES=10         # 10 distortion lines
INVITE_EXPIRE_MINUTES=30    # Links expire after 30 minutes
```

The keyboard layout and button appearance are automatically adjusted based on your captcha length. The number of available buttons will always be at least 3 times the captcha length to ensure security.

## Error Handling

The bot includes comprehensive error handling for:
- Invalid captcha attempts
- Failed invite link generation
- Session expiration
- Network issues
- Permission problems
