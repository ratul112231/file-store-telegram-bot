# config.py - Final Configuration File

# --- REQUIRED: Fill these in ---
# Telegram API Credentials (from my.telegram.org)
API_ID = 39396720 # Replace with your API ID
API_HASH = "945f0314b982ab0847fd009e5e447b64"
BOT_TOKEN = "8222385318:AAH6AK3nSOX2CPxLNAr9CQtqhJZfM-8Jhro"

# Your private channel ID where files are stored
DB_CHANNEL = -1003656239689  # Replace with your channel ID

# Your user ID and any other admin user IDs
ADMINS = [6992010963, 7831735222]  # Replace with actual Telegram user IDs

# Your API token from ShrinkEarn.com
SHORTENER_API = "YOUR_SHRINKEARN_API_TOKEN"

# --- DEFAULT SETTINGS (Can be changed from the admin panel) ---
DEFAULT_bkash_HANDLE = "your-bkash-id@RatulHosain"
DEFAULT_QR_CODE_URL = "https://qr.bka.sh/281014021VIVv0szr0EB6CCB5C"
DEFAULT_PAYMENT_LINK = "https://qr.bka.sh/281014021VIVv0szr0EB6CCB5C" # Example Link
DEFAULT_AUTO_DELETE_MINUTES = 10 # Default time in minutes for files to be deleted after sending

# Your username for users to send payment screenshots to
PAYMENT_ADMIN = "@ratulislam1133" # IF YOU DON'T HAVE USERNAME, USE YOUR TELEGRAM ID

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
