# Telegram Game Bot

A configurable Telegram bot that runs various word games and message-based challenges in group chats.

## Features

- **Multiple Game Modes:**
  1. Word/Sticker Trigger - React to specific words or stickers
  2. Message Counter - Track nth message in chat
  3. Buffer/Timeout - Monitor inactive words/phrases
  4. Feature Counter - Count message characteristics (dots, spaces, loops, etc.)

- **Configurable Settings:**
  - Custom trigger words and match types
  - Adjustable message count ranges
  - Buffer timeouts
  - Multiple trigger conditions
  - Automated hints system

- **Persistence:**
  - Message counting across restarts
  - Session management
  - Configuration storage

## Requirements

```txt
python-telegram-bot~=20.7
telethon~=1.33.1
python-dotenv~=1.0.0
openai~=1.13.3
numpy~=1.26.3
pytz~=2023.3.post1
```

## Setup

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your credentials:
```env
API_ID=your_api_id
API_HASH=your_api_hash
PHONE=your_phone_number
PRIVATE_ID=your_private_chat_id
TARGET_CHAT_ID=target_group_chat_id
MY_ID=your_user_id
OPENAI_API_KEY=your_openai_key
```

4. Run the configuration manager to set up your game:
```bash
python config_manager.py
```

## Configuration

Use `config_manager.py` to interactively configure:
- Game type selection
- Trigger conditions
- Message counting rules
- Hint scheduling
- Custom messages

## Usage

Run the bot:
```bash
python main.py
```

The bot will:
1. Connect to Telegram
2. Load configurations
3. Monitor messages based on game rules
4. Send automated responses
5. Track progress and persist state

## Project Structure

```
telegram-bot/
├── bot/                # Bot core functionality
├── config/            # Configuration handling
├── games/            # Game logic implementations
├── services/         # Supporting services
│   ├── embedding.py  # OpenAI text analysis
│   └── counter.py    # Message counting
├── utils/            # Utility functions
└── main.py          # Entry point
```

## Security Notes

- Keep your `.env` file secure and never commit it
- Don't share your API credentials
- Monitor OpenAI API usage

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request
