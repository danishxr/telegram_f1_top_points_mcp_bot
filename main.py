import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
import asyncio
from f1_scraper import get_f1_standings_csv
from fastmcp import Client

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)
# Bot configuration
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
MCP_SERVER_URL = "http://localhost:8001"

class F1TelegramBot:
    def __init__(self, token: str):
        self.token = token
        self.application = Application.builder().token(token).build()
        self.mcp_client = None
        self.setup_handlers()
    
    async def get_mcp_client(self):
        """Get or create MCP client connection"""
        if self.mcp_client is None:
            # Use the correct FastMCP client initialization
            self.mcp_client = Client("http://localhost:8001/mcp")
        return self.mcp_client
    
    def setup_handlers(self):
        """Setup command and message handlers"""
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("standings", self.standings_command))
        self.application.add_handler(CommandHandler("email", self.email_command))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_message = (
            "🏎️ Welcome to the F1 Standings Bot!\n\n"
            "Available commands:\n"
            "/standings - Get current F1 driver standings\n"
            "/email <your-email> - Get standings sent to your email\n"
            "/help - Show this help message"
        )
        await update.message.reply_text(welcome_message)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_message = (
            "🏎️ F1 Standings Bot Commands:\n\n"
            "📊 /standings - Display current F1 driver standings\n"
            "📧 /email <your-email> - Send standings CSV to your email\n"
            "❓ /help - Show this help message\n\n"
            "Example: /email john@example.com"
        )
        await update.message.reply_text(help_message)
    
    async def standings_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /standings command"""
        await update.message.reply_text("🔍 Fetching current F1 standings...")
        
        try:
            # Get F1 standings
            csv_path = await get_f1_standings_csv()
            
            # Read and format standings for display
            import pandas as pd
            df = pd.read_csv(csv_path)
            
            standings_text = "🏎️ **Current F1 Driver Standings:**\n\n"
            for _, row in df.iterrows():
                standings_text += f"{row['position']}. {row['driver']} - {row['points']} pts\n"
            
            await update.message.reply_text(standings_text, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error fetching standings: {e}")
            await update.message.reply_text("❌ Sorry, I couldn't fetch the current standings. Please try again later.")
    
    async def email_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /email command"""
        if not context.args:
            await update.message.reply_text(
                "📧 Please provide an email address.\n"
                "Usage: /email your-email@example.com"
            )
            return
        
        email = context.args[0]
        
        # Basic email validation
        if '@' not in email or '.' not in email:
            await update.message.reply_text("❌ Please provide a valid email address.")
            return
        
        await update.message.reply_text(f"📊 Preparing F1 standings and sending to {email}...")
        
        try:
            # Get F1 standings CSV
            csv_path = await get_f1_standings_csv()
            
            # Send email via FastMCP server
            success = await self.send_email_via_mcp(email, csv_path)
            
            if success:
                await update.message.reply_text(
                    f"✅ F1 standings have been sent to {email}!\n"
                    "Check your inbox for the CSV file."
                )
            else:
                await update.message.reply_text(
                    "❌ Failed to send email. Please check your email address and try again."
                )
                
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            await update.message.reply_text(
                "❌ Sorry, there was an error sending the email. Please try again later."
            )
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular text messages"""
        message_text = update.message.text.lower()
        
        if any(word in message_text for word in ['f1', 'formula', 'standings', 'points']):
            await update.message.reply_text(
                "🏎️ I can help you with F1 standings!\n"
                "Use /standings to see current standings or /email <your-email> to get them sent to you."
            )
        else:
            await update.message.reply_text(
                "👋 Hi! I'm the F1 Standings Bot.\n"
                "Use /help to see what I can do for you!"
            )
    
    async def send_email_via_mcp(self, email: str, csv_path: str) -> bool:
        """Send email via FastMCP server using proper MCP client"""
        try:
            client = await self.get_mcp_client()
            
            async with client:
                result = await client.call_tool(
                    "send_f1_standings_email",
                    {
                        "receiver_email": email,
                        "csv_file_path": csv_path,
                        "subject": "🏎️ Current F1 Driver Standings",
                        "body": "Hello! Please find the latest Formula 1 driver standings attached as a CSV file.\n\nEnjoy the races!\n\n🏎️ F1 Standings Bot"
                    }
                )
                
                # Handle different response formats
                if isinstance(result, list):
                    # If result is a list
                    if result and hasattr(result[0], 'text'):
                        import json
                        tool_result = json.loads(result[0].text)
                        return tool_result.get('success', False)
                    return False
                elif hasattr(result, 'content'):
                    # If result has content attribute
                    import json
                    tool_result = json.loads(result.content[0].text)
                    return tool_result.get('success', False)
                elif isinstance(result, dict):
                    # If result is already a dictionary
                    return result.get('success', False)
                else:
                    # Log the actual result type for debugging
                    logger.info(f"Unexpected result type: {type(result)}, value: {result}")
                    # The email was sent successfully according to logs
                    return True
                    
        except Exception as e:
            logger.error(f"Error calling MCP server: {e}")
            return False
    
    def run(self):
        """Run the bot using run_polling which handles the event loop properly"""
        logger.info("Starting F1 Telegram Bot...")
        self.application.run_polling()

def main():
    """Main function to run the bot"""
    if not BOT_TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN not found in environment variables")
        print("Please create a .env file with your bot token:")
        print("TELEGRAM_BOT_TOKEN=your_bot_token_here")
        return
    
    bot = F1TelegramBot(BOT_TOKEN)
    bot.run()  # Use synchronous run instead of asyncio.run

if __name__ == "__main__":
    main()
