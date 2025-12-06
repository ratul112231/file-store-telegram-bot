# config.py - Final Configuration File

# --- REQUIRED: Fill these in ---
# Telegram API Credentials (from my.telegram.org)
API_ID = 8328942211 # Replace with your API ID
API_HASH = "YOUR_API_HASH"
BOT_TOKEN = "YOUR_BOT_API_TOKEN"

# Your private channel ID where files are stored
DB_CHANNEL = -88994477333  # Replace with your channel ID

# Your user ID and any other admin user IDs
ADMINS = [123456789, 987654321]  # Replace with actual Telegram user IDs

# Your API token from ShrinkEarn.com
SHORTENER_API = "YOUR_SHRINKEARN_API_TOKEN"

# --- DEFAULT SETTINGS (Can be changed from the admin panel) ---
DEFAULT_UPI_HANDLE = "your-upi-id@okhdfcbank"
DEFAULT_QR_CODE_URL = "https://i.ibb.co/g9fXy3x/image.png"
DEFAULT_PAYMENT_LINK = "https://upi.pe/your-link" # Example Link
DEFAULT_AUTO_DELETE_MINUTES = 10 # Default time in minutes for files to be deleted after sending

# Your username for users to send payment screenshots to
PAYMENT_ADMIN = "YOUR_TELEGRAM_USERNAME" # IF YOU DON'T HAVE USERNAME, USE YOUR TELEGRAM ID

# --- TEXT CONFIGURATION ---
USER_WELCOME_TEXT = "👋 Welcome, {name}!**\n\nI am your file assistant, Sarah. To get a file, simply click on a valid link."
ADMIN_WELCOME_TEXT = "🛡 **Admin Panel**\n\nWelcome, {name}! Use the menu below to manage the bot."

# Text for the "Become a Member" prompt
BECOME_MEMBER_TEXT = f"""💎 Become a Member!

**Benefits of Being a Member:**
- No ads, ever.
- Direct and instant file access.
- Early access to new content.

**How to Join:**
1.  Complete the payment using any option below.
2.  Send a screenshot of the payment to {PAYMENT_ADMIN}.

**UPI:** {{upi_handle}}
"""
