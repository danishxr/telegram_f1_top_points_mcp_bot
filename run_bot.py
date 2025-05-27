import subprocess
import sys
import time
from pathlib import Path
import signal
import os

def start_mcp_server():
    """Start the FastMCP server"""
    print("Starting FastMCP server...")
    process = subprocess.Popen([
        sys.executable, 
        str(Path(__file__).parent / "gmail_mcp" / "gamil_mcp_server.py")
    ])
    
    # Wait a bit for server to start
    time.sleep(3)
    return process

def start_telegram_bot():
    """Start the Telegram bot"""
    print("Starting Telegram bot...")
    process = subprocess.Popen([
        sys.executable, 
        str(Path(__file__).parent / "main.py")
    ])
    return process

def main():
    """Start both services"""
    mcp_process = None
    bot_process = None
    
    try:
        # Start MCP server first
        mcp_process = start_mcp_server()
        
        # Start Telegram bot
        bot_process = start_telegram_bot()
        
        print("\n🚀 Both services are running!")
        print("📧 FastMCP server: http://localhost:8001")
        print("🤖 Telegram bot: Active")
        print("\nPress Ctrl+C to stop both services")
        
        # Wait for processes
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            if mcp_process.poll() is not None:
                print("❌ MCP server stopped unexpectedly")
                break
            if bot_process.poll() is not None:
                print("❌ Telegram bot stopped unexpectedly")
                break
                
    except KeyboardInterrupt:
        print("\n🛑 Stopping services...")
    finally:
        if mcp_process:
            mcp_process.terminate()
            mcp_process.wait()
        if bot_process:
            bot_process.terminate()
            bot_process.wait()
        print("✅ Services stopped")

if __name__ == "__main__":
    main()