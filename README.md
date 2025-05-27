# telegram_f1_top_points_mcp_bot
The project is a simple telegram bot which fetches the current points of the F1 racers and makes it into a spreadsheet and sends to the user as email via gmail

F1PointTracker_bot


# Requirements
Instagram Bot: F1 Standings and Email Reporting

This document outlines the requirements for an Instagram bot designed to retrieve and disseminate the latest Formula 1 (F1) racer standings.

1. F1 Standings Retrieval
	* The telegram bot (python-telegram-bot) shall programmatically use DuckDuckGo search to find the most current F1 racer points.
	* The search results must be processed to extract the latest points for each F1 racer.
	* The extracted data must be ordered based on the racers' official ranking.

2. Data Export and Email Delivery
	* Upon command, the bot shall generate a CSV file containing the ordered F1 racer standings.
	* The bot shall then use the Gmail API (via FastMCP) to send this CSV file as an attachment to a user-specified email address.

3. Technical Implementation Details
	* The telegram bot will be coded using the python-telegram-bot
		- Here is the library documentation [python-telegram-bot documentation](https://github.com/python-telegram-bot/python-telegram-bot/wiki/Extensions---Your-first-Bot)
	* The bot will utilize a FastMCP server for its backend.
		- Here is the library documentation [FastMCP documentation](https://github.com/jlowin/fastmcp)
	* The FastMCP server will operate with an HTTP transport type.
	* The FastMCP server will be accessible on port 8001.
	* Specific Instagram bot commands will be implemented to trigger the search, data processing, and email sending functionalities.

# Setup and Running the Bot

## Dependencies Management with uv

This project uses `uv` for Python package management. Follow these steps to set up and run the bot:

1. Install dependencies using uv sync:

```bash
uv pip sync
```
2. Run the bot:

```bash
uv run run_bot.py
```
You can now interact with your bot on Telegram using the following commands:

- /start - Get started with the bot
- /help - Show available commands
- /standings - Get current F1 driver standings
- /email <your-email> - Get standings sent to your email

> Ensure you have the APP-PASSWORD and TELEGRAM_BOT_TOKEN in the .env file.
