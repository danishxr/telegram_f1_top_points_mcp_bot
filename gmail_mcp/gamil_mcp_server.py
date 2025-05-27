import asyncio
from fastmcp import FastMCP
from send_email import send_email
import os
from typing import Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("gmail_mcp.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("gmail_mcp_server")

# Initialize FastMCP server
app: FastMCP = FastMCP("F1 Email Service")
logger.info("FastMCP server initialized with name 'F1 Email Service'")

@app.tool()
def send_f1_standings_email(
    receiver_email: str,
    csv_file_path: str,
    subject: str = "F1 Current Standings",
    body: str = "Please find the latest F1 standings attached."
) -> dict:
    """
    Send F1 standings CSV file via email
    
    Args:
        receiver_email: Email address to send the standings to
        csv_file_path: Path to the CSV file containing F1 standings
        subject: Email subject line
        body: Email body text
    
    Returns:
        dict: Status of email sending operation
    """
    logger.info(f"Attempting to send F1 standings email to {receiver_email} with CSV: {csv_file_path}")
    try:
        if not os.path.exists(csv_file_path):
            logger.error(f"CSV file not found: {csv_file_path}")
            return {"success": False, "error": "CSV file not found"}
        
        send_email(
            receiver_email=receiver_email,
            subject=subject,
            body=body,
            attachment_path=csv_file_path
        )
        
        logger.info(f"Email successfully sent to {receiver_email}")
        return {"success": True, "message": "Email sent successfully"}
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}", exc_info=True)
        return {"success": False, "error": str(e)}

@app.tool()
def get_server_status() -> dict:
    """
    Get the status of the FastMCP server
    
    Returns:
        dict: Server status information
    """
    logger.info("Server status requested")
    return {
        "status": "running",
        "service": "F1 Email Service",
        "port": 8001
    }

if __name__ == "__main__":
    logger.info("Starting FastMCP server on http://localhost:8001")
    print("Starting FastMCP server on http://localhost:8001")
    # Use streamable-http transport as recommended by FastMCP 2.x
    app.run(transport="streamable-http", host="127.0.0.1", port=8001)