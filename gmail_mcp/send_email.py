import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from dotenv import load_dotenv
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
logger = logging.getLogger("send_email")

load_dotenv()
app_password = os.getenv("APP-PASSWORD")
logger.debug("Environment variables loaded")

if app_password:
    logger.info("App password successfully loaded from environment")
else:
    logger.warning("App password not found in environment variables")

print("-----------------------------------------------------")
print(app_password)
print("-----------------------------------------------------")
SENDER_EMAIL = "yourcoolaibro@gmail.com"  # Hardcoded sender email


def send_email(receiver_email=None, subject="", body="", attachment_path=None):
    logger.info(f"Preparing to send email to {receiver_email}")
    # Email configuration
    if receiver_email is None:
        #TODO: temporary hardcoded email as enter key is not working
        # receiver_email = input("Enter recipient email: ")
        receiver_email = "danishxr@gmail.com"
        logger.info(f"Using default receiver email: {receiver_email}")
    password = app_password

    # Create a multipart message
    message = MIMEMultipart()
    message["From"] = SENDER_EMAIL
    message["To"] = receiver_email
    message["Subject"] = subject
    logger.debug(f"Email headers set: From={SENDER_EMAIL}, To={receiver_email}, Subject={subject}")

    # Add body to email
    message.attach(MIMEText(body, "plain"))
    logger.debug("Email body attached")

    # Add attachment if provided
    if attachment_path and os.path.exists(attachment_path):
        logger.info(f"Attaching file: {attachment_path}")
        # Open the file in binary mode
        with open(attachment_path, "rb") as attachment:
            # Add file as application/octet-stream
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())

        # Encode file in ASCII characters to send by email
        encoders.encode_base64(part)

        # Add header as key/value pair to attachment part
        filename = os.path.basename(attachment_path)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {filename}",
        )

        # Add attachment to message
        message.attach(part)
        logger.debug(f"File {filename} attached successfully")
    elif attachment_path:
        logger.warning(f"Attachment file not found: {attachment_path}")

    try:
        # Create SMTP session
        logger.info("Connecting to SMTP server: smtp.gmail.com:587")
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()  # Secure the connection
        logger.debug("TLS connection established")

        # Login to sender email
        logger.info(f"Attempting to login with email: {SENDER_EMAIL}")
        server.login(SENDER_EMAIL, password)
        logger.debug("Login successful")

        # Send email
        server.send_message(message)
        logger.info("Email sent successfully!")
        print("Email sent successfully!")

        # Terminate the session
        server.quit()
        logger.debug("SMTP session terminated")
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}", exc_info=True)
        print(f"Error: {e}")


if __name__ == "__main__":
    logger.info("Running send_email.py directly")
    send_email()
