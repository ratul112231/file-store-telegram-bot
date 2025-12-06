# Telegram File Store Bot

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pyrogram](https://img.shields.io/badge/Pyrogram-2.0+-0088cc?style=for-the-badge&logo=telegram&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

A feature-rich Telegram bot for storing and sharing files with monetization features, force subscription, premium membership, auto-deletion, and comprehensive admin management.

---

## Table of Contents

- [Features](#features)
- [Demo Workflow](#demo-workflow)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [User Guide](#user-guide)
  - [How Users Access Files](#how-users-access-files)
  - [Free vs Premium Users](#free-vs-premium-users)
- [Admin Guide](#admin-guide)
  - [Admin Commands](#admin-commands)
  - [Uploading Files](#uploading-files)
  - [Creating Batches](#creating-batches)
  - [Managing Users](#managing-users)
  - [Payment Settings](#payment-settings)
  - [Bot Settings](#bot-settings)
  - [Broadcasting](#broadcasting)
- [Monetization Features](#monetization-features)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## Features

### File Management
- Upload and store unlimited files (documents, videos, audio, photos)
- Generate unique shareable links for each file
- Batch file upload with range-based link generation
- Auto-deletion system with configurable timer
- Secure file storage in private database channel

### Monetization
- **URL Shortener Integration**: Earn from link clicks (ShrinkEarn)
- **Premium Membership System**: Paid subscriptions for ad-free access
- **UPI Payment Integration**: Accept payments via UPI with QR codes
- **Customizable Payment Options**: Set custom UPI IDs and payment links

### User Management
- Force subscription to channels before file access
- User status tracking (Free, Premium, Banned, Unlocked)
- Temporary access grants (time-limited unlocks)
- Ban/unban system for user moderation
- User statistics and analytics

### Admin Features
- Comprehensive admin control panel
- Broadcast messages to all users
- User and channel management interface
- Payment configuration dashboard
- Detailed bot statistics
- Auto-delete timer configuration

---

## Demo Workflow

### For Regular Users:
1. User receives a file link
2. Clicks link → Opens bot
3. Bot checks force subscription status
4. If not subscribed → Shows join buttons
5. After joining → User chooses:
   - Watch ad (URL shortener) → Get temporary access
   - Go premium → Pay once, access forever
6. File is sent with auto-delete warning

### For Premium Users:
1. User receives a file link
2. Clicks link → File sent instantly
3. No ads, no waiting, no expiry

### For Admins:
1. Send any file to bot → Get shareable link
2. Use `/batch` command → Create batch links
3. Access admin panel → Manage everything

---

## Prerequisites

Before setting up the bot, ensure you have:

1. **Python 3.8 or higher** installed
2. **Telegram API Credentials**
   - Get API ID and API Hash from [my.telegram.org](https://my.telegram.org)
3. **Bot Token** from [@BotFather](https://t.me/BotFather)
4. **Database Channel** - A private channel where files will be stored
   - Create a private channel
   - Add your bot as admin with posting rights
   - Get the channel ID (use [@username_to_id_bot](https://t.me/username_to_id_bot))
5. **Your Telegram User ID**
   - Get from [@userinfobot](https://t.me/userinfobot)
6. **ShrinkEarn API Key** (Optional, for monetization)
   - Register at [ShrinkEarn.com](https://shrinkearn.com)

---

## Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/div0enormous/file-store-telegram-bot.git
cd file-store-telegram-bot
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

**Required Packages:**
```
pyrogram==2.0.106
tgcrypto==1.2.5
requests==2.31.0
pyrofork==2.3.41
aiohttp==3.9.5
```

### Step 3: Configure the Bot

Edit `config.py` with your credentials:

```python
# Telegram API Credentials
API_ID = 20338805  # From my.telegram.org
API_HASH = "your_api_hash_here"
BOT_TOKEN = "your_bot_token_here"

# Database Channel (Private channel for storing files)
DB_CHANNEL = -1001234567890  # Your private channel ID

# Admin User IDs
ADMINS = [1500034181]  # Your Telegram user ID

# ShrinkEarn API (for monetization)
SHORTENER_API = "your_shrinkearn_api_key"

# Payment Settings
DEFAULT_UPI_HANDLE = "yourname@okaxis"
DEFAULT_QR_CODE_URL = "https://i.ibb.co/xxxxx/qr.png"
DEFAULT_PAYMENT_LINK = "https://upi.pe/your-link"

# Admin contact for payment verification
PAYMENT_ADMIN = "@yourusername"

# Auto-delete timer (in minutes)
DEFAULT_AUTO_DELETE_MINUTES = 10
```

### Step 4: Set Up Database Channel

1. Create a **private channel** in Telegram
2. Add your bot as **administrator** with **post messages** permission
3. Forward any message from the channel to [@username_to_id_bot](https://t.me/username_to_id_bot)
4. Copy the channel ID (starts with -100)
5. Paste it in `config.py` as `DB_CHANNEL`

### Step 5: Run the Bot

```bash
python main.py
```

You should see: **"BOT STARTED"**

---

## Configuration

### config.py Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `API_ID` | Integer | Yes | Telegram API ID from my.telegram.org |
| `API_HASH` | String | Yes | Telegram API Hash |
| `BOT_TOKEN` | String | Yes | Bot token from @BotFather |
| `DB_CHANNEL` | Integer | Yes | Private channel ID for file storage |
| `ADMINS` | List | Yes | List of admin user IDs |
| `SHORTENER_API` | String | No | ShrinkEarn API key for monetization |
| `DEFAULT_UPI_HANDLE` | String | No | Default UPI ID for payments |
| `DEFAULT_QR_CODE_URL` | String | No | QR code image URL |
| `DEFAULT_PAYMENT_LINK` | String | No | Direct UPI payment link |
| `PAYMENT_ADMIN` | String | Yes | Admin username for payment verification |
| `DEFAULT_AUTO_DELETE_MINUTES` | Integer | Yes | Default file expiry time in minutes |

### Database Structure

The bot automatically creates `bot.db` with these tables:
- **users**: User information and status
- **files**: File metadata and storage references
- **batches**: Batch file collections
- **bot_settings**: Dynamic configuration
- **force_sub_channels**: Force subscription channels
- **user_access**: Temporary access grants
- **unlock_tokens**: URL shortener unlock tokens
- **batch_messages**: Batch auto-delete tracking

---

## User Guide

### How Users Access Files

#### Step 1: Receive a Link

Users receive a link like:
```
https://t.me/YourBot?start=ZmlsZV8xMjM=
```

#### Step 2: Start the Bot

When clicked, the bot opens with the `/start` command automatically processed.

#### Step 3: Check Force Subscription

If force subscription is enabled, users must join required channels:

```
Please Join Our Channels

You must join our channel(s) to get files.

[Join Tech Channel]
[Join News Channel]

[✅ I Have Joined, Retry]
```

#### Step 4: Choose Access Method

**For Free Users:**
```
🚀 Continue Using the Bot

To keep all features active, select an option below:

[▶️ Watch an Ad]
[💎 Go Premium]
```

**Watch an Ad Option:**
- Redirects to URL shortener
- Complete the ad steps
- Returns with 1-hour temporary access
- Files sent instantly during this period

**Go Premium Option:**
- Shows payment details with QR code
- UPI ID displayed
- After payment, send screenshot to admin
- Admin manually grants premium status
- Permanent ad-free access

#### Step 5: Receive File

**Free Users (after ad):**
```
⏳ Sending file, please wait...

[File is sent]

⚠️ Notice:

This file will automatically expire and self-destruct in 10 minutes.

Please forward this to your Saved Messages 🕒
```

**Premium Users:**
```
⏳ Sending file, please wait...

[File is sent instantly with no expiry warning]
```

### Free vs Premium Users

| Feature | Free Users | Premium Users |
|---------|------------|---------------|
| File Access | Via shortened URL (ads) | Instant, direct access |
| Waiting Time | ~5-10 seconds per file | None |
| Access Duration | 1 hour after unlock | Permanent |
| Auto-Delete | Files expire after set time | No expiry (optional) |
| Force Subscribe | Required | Optional (can be skipped) |

---

## Admin Guide

### Admin Commands

Admins have access to these commands:

| Command | Description | Example |
|---------|-------------|---------|
| `/start` | Opens admin control panel | `/start` |
| `/help` | Shows admin menu | `/help` |
| `/batch` | Creates batch file link | `/batch 101 150 Movie Collection` |

**Note:** Regular file uploads are done by simply sending files to the bot (no command needed).

### Admin Control Panel

When admins type `/start`, they see:

```
🛡 Admin Panel

Welcome, Admin! Use the menu below to manage the bot.

[📢 Broadcast] [📊 Statistics]
[👥 User Management] [🔗 Force Sub]
[💰 Payment Settings] [⚙️ Bot Settings]
```

---

### Uploading Files

#### Single File Upload

**Step 1:** Send any file (document, video, audio, photo) directly to the bot

**Step 2:** Bot processes and stores it in the database channel

**Step 3:** Bot responds with shareable link:

```
✅ File Uploaded

🔗 Link: https://t.me/YourBot?start=ZmlsZV8xMjM=
```

**Step 4:** Share this link with users

#### Supported File Types
- Documents (PDF, DOCX, ZIP, etc.)
- Videos (MP4, MKV, AVI, etc.)
- Audio (MP3, WAV, FLAC, etc.)
- Photos (JPG, PNG, GIF, etc.)

**File Size Limit:** Up to 2GB (Telegram limitation)

---

### Creating Batches

Batch links allow sharing multiple files with a single link.

#### Prerequisites
Files must be already uploaded to the database channel with sequential message IDs.

#### Syntax

```bash
/batch <start_message_id> <end_message_id> <Batch Name>
```

#### Example

```
/batch 101 150 Avengers Collection
```

**This creates:**
- A batch containing messages 101 to 150 (50 files)
- Batch name: "Avengers Collection"

#### Bot Response

```
✅ Batch 'Avengers Collection' created!

- Contains: 50 files.
- Link: https://t.me/YourBot?start=YmF0Y2hfNQ==
```

#### How Users Receive Batches

1. User clicks batch link
2. Completes force sub/unlock process (if required)
3. All files in batch are sent sequentially
4. Auto-delete timer applies to all files
5. Warning message shows expiry time

#### Finding Message IDs

To find message IDs in your database channel:

1. Forward a message from the channel to [@username_to_id_bot](https://t.me/username_to_id_bot)
2. Or right-click → Copy message link (ID is in URL)
3. Example: `t.me/c/1234567890/101` → Message ID is `101`

---

### Managing Users

Click **"👥 User Management"** in the admin panel:

```
👥 User Management

[➕ Add Member] [➖ Remove Member]
[🚫 Ban User] [✅ Unban User]
[⬅️ Back]
```

#### Add Premium Member

1. Click **"➕ Add Member"**
2. Bot asks: *"Send the User ID to make a member."*
3. Send the user's Telegram ID (e.g., `123456789`)
4. Bot confirms: *"✅ User `123456789` has been updated successfully."*

**How to Get User IDs:**
- Ask user to forward a message to [@userinfobot](https://t.me/userinfobot)
- Or check bot logs when user starts the bot

#### Remove Premium Member

1. Click **"➖ Remove Member"**
2. Send user ID
3. User returns to free tier

#### Ban User

1. Click **"🚫 Ban User"**
2. Send user ID
3. User gets: *"🚫 You are banned from using this bot."*

#### Unban User

1. Click **"✅ Unban User"**
2. Send user ID
3. User can access bot again

---

### Payment Settings

Click **"💰 Payment Settings"** in the admin panel:

```
💰 Payment Settings

- UPI: yourname@okaxis
- Link: https://upi.pe/your-link

[✏️ UPI ID] [🔗 Pay Link]
[🖼️ QR Code]
[⬅️ Back]
```

#### Change UPI ID

1. Click **"✏️ UPI ID"**
2. Bot asks: *"Send the new UPI ID."*
3. Send your UPI ID (e.g., `yourname@paytm`)
4. Bot confirms: *"✅ UPI ID updated."*

#### Change Payment Link

1. Click **"🔗 Pay Link"**
2. Send your UPI payment link
   - Example: `upi://pay?pa=yourname@okaxis&pn=YourName&cu=INR`
   - Or use link shorteners for cleaner URLs
3. Bot confirms: *"✅ Payment Link updated."*

**Generating UPI Links:**
- Use Google Pay, PhonePe, or Paytm apps
- Go to "Request Money" → "Share Link"
- Or use online UPI link generators

#### Change QR Code

1. Click **"🖼️ QR Code"**
2. Send a QR code image (photo)
3. Bot confirms: *"✅ QR Code updated."*

**Generating QR Codes:**
- Use any QR code generator with your UPI ID
- Or download from your payment app
- Upload to image hosting (e.g., [ImgBB](https://imgbb.com))

#### When Users Click "Go Premium"

They see:

```
💎 Become a Member!

Benefits of Being a Member:
- No ads, ever.
- Direct and instant file access.
- Early access to new content.

How to Join:
1. Complete the payment using any option below.
2. Send a screenshot of the payment to @youradmin.

UPI: yourname@okaxis

[QR Code Image]

[Click Here to Pay (UPI Link)]
```

---

### Bot Settings

Click **"⚙️ Bot Settings"** in the admin panel:

```
⚙️ Bot Settings

- Files are deleted after 10 minutes.

[⏱️ Change Auto-Delete Time]
[⬅️ Back]
```

#### Change Auto-Delete Time

1. Click **"⏱️ Change Auto-Delete Time"**
2. Select duration:

```
Select the auto-delete time:

[10 min] [30 min] [60 min]
[Never (0)]
[⬅️ Back]
```

**Options:**
- **10 minutes**: Quick expiry (default)
- **30 minutes**: Moderate expiry
- **60 minutes**: Extended expiry
- **Never (0)**: Files never auto-delete

**Note:** Setting to "Never" means files stay in user's chat permanently unless manually deleted.

---

### Force Subscription Management

Click **"🔗 Force Sub"** in the admin panel:

```
Use the buttons to manage your force subscribe channels.

[➕ Add Channel]
[⬅️ Back]
```

#### Adding a Force Subscribe Channel

**Method 1: Forward Message**
1. Click **"➕ Add Channel"**
2. Forward any message from your channel to the bot
3. Bot extracts channel ID automatically
4. Confirms: *"✅ Channel 'Tech News' added to force sub list."*

**Method 2: Send Channel ID**
1. Click **"➕ Add Channel"**
2. Send the channel ID (e.g., `-1001234567890`)
3. Bot verifies and adds channel

**Important Requirements:**
- Bot must be admin in the channel
- Channel must be public or bot must have access
- Users will be required to join before accessing files

#### How Force Subscribe Works

When a user tries to access a file:

1. Bot checks if user is subscribed to all force sub channels
2. If not subscribed, shows:

```
Please Join Our Channels

You must join our channel(s) to get files.

[Join Tech News]
[Join Updates Channel]

[✅ I Have Joined, Retry]
```

3. After joining, user clicks retry
4. Bot verifies membership
5. If verified, proceeds to unlock/file delivery

---

### Broadcasting

Click **"📢 Broadcast"** in the admin panel:

```
Send the message to broadcast to all users.

[❌ Cancel]
```

#### Steps to Broadcast

1. Click **"📢 Broadcast"**
2. Send your message (text, photo, video, or any media)
3. Bot shows progress:

```
📢 Broadcasting to 1250 users...
```

4. After completion:

```
✅ Broadcast Complete

- Sent: 1200 | Failed: 50
```

**Features:**
- Broadcasts to all non-banned users
- Preserves formatting (Markdown, HTML)
- Works with any message type
- Shows success/failure count
- Failed deliveries are users who blocked the bot

**Best Practices:**
- Keep messages concise and clear
- Use formatting for important points
- Test with small group first
- Broadcast during active hours
- Include call-to-action buttons if needed

---

### Statistics

Click **"📊 Statistics"** in the admin panel:

```
📊 Bot Statistics

📁 Content: 1,234 files saved.
👥 Users: 5,678 total users.
💎 Members: 234 premium members.
🚫 Banned: 12 users banned.

[⬅️ Back]
```

**Metrics Explained:**
- **Content**: Total files stored in database
- **Users**: All users who started the bot
- **Members**: Users with premium access
- **Banned**: Users blocked from bot access

---

## Monetization Features

### How Monetization Works

#### Revenue Stream 1: URL Shortener Ads

1. User requests a file
2. Bot generates shortened link with ShrinkEarn
3. User completes ad/captcha
4. User gets 1-hour access
5. You earn from every ad completion

**Earnings:** $1-5 per 1000 views (varies by country)

#### Revenue Stream 2: Premium Memberships

1. User wants ad-free access
2. Pays via UPI (one-time or recurring)
3. Admin verifies payment
4. User gets permanent premium status
5. You set your own pricing

**Suggested Pricing:**
- Monthly: $2-5
- Quarterly: $5-10
- Lifetime: $10-20

### Setting Up Monetization

#### Step 1: Create ShrinkEarn Account

1. Visit [ShrinkEarn.com](https://shrinkearn.com)
2. Sign up for free account
3. Go to "API" section
4. Copy your API key
5. Paste in `config.py` as `SHORTENER_API`

#### Step 2: Configure Payment Options

1. Set your UPI ID in config or via admin panel
2. Generate QR code for your UPI ID
3. Upload QR code to image hosting
4. Add image URL to config
5. Optionally create direct UPI payment link

#### Step 3: Promote Your Bot

1. Share file links in channels/groups
2. Users access via shortened URLs (you earn)
3. Offer premium benefits
4. Process payments manually
5. Grant premium status via admin panel

### Maximizing Revenue

**Tips:**
- Share high-demand content (movies, courses, software)
- Use multiple channels for distribution
- Offer attractive premium benefits
- Price competitively
- Automate payment verification (future feature)
- Cross-promote with other channels

---

## Project Structure

```
telegram-file-store-bot/
│
├── main.py              # Main bot logic and handlers
├── database.py          # SQLite database operations
├── config.py            # Configuration file
├── requirements.txt     # Python dependencies
├── bot.db              # SQLite database (auto-generated)
└── README.md           # This file
```

### Key Components

**main.py**
- Bot initialization and client setup
- Command handlers (`/start`, `/help`, `/batch`)
- Callback query handlers (admin panel buttons)
- Message handlers (file uploads, admin inputs)
- File and batch sending logic
- Auto-deletion scheduler
- Force subscription checks
- URL shortener integration

**database.py**
- Database schema and initialization
- User management functions
- File and batch CRUD operations
- Settings management
- Access control and tokens
- Statistics aggregation

**config.py**
- API credentials
- Admin configuration
- Payment settings
- Default values
- Custom welcome messages

---

## Troubleshooting

### Bot Not Starting

**Error:** `ValueError: Invalid API ID`

**Solution:**
- Check `API_ID` is an integer (no quotes)
- Verify credentials from my.telegram.org
- Ensure no extra spaces in config.py

### Files Not Uploading

**Error:** `Failed to save file: Forbidden`

**Solution:**
- Make sure bot is admin in `DB_CHANNEL`
- Verify channel ID starts with `-100`
- Check bot has "Post Messages" permission
- Try re-adding bot to channel

### Force Subscribe Not Working

**Error:** Users can access files without joining

**Solution:**
- Ensure bot is admin in force sub channels
- Public channels need bot to be admin
- Private channels need bot to have member list access
- Check channel IDs are correct

### URL Shortener Not Working

**Error:** Links not shortened, original link shown

**Solution:**
- Verify ShrinkEarn API key is valid
- Check internet connection
- Ensure API key doesn't contain "YOUR" placeholder
- Test API key on ShrinkEarn website

### Payment Issues

**Problem:** QR code not displaying

**Solution:**
- Upload QR code to stable image hosting (ImgBB, Imgur)
- Use direct image URL (must end with .jpg/.png)
- Test URL in browser first
- Try re-uploading via admin panel

### Auto-Delete Not Working

**Problem:** Files not deleting after set time

**Solution:**
- Check auto-delete timer is not set to 0 (Never)
- Verify bot has message deletion permissions
- Bot must remain online for auto-delete to work
- Check bot logs for deletion errors

### User Can't Access Files

**Problem:** User sees "File Not Found"

**Solution:**
- Verify file exists in database channel
- Check message ID hasn't been deleted
- Ensure bot still has access to DB_CHANNEL
- Try re-uploading the file

---

## Contributing

Contributions are welcome! Here's how you can help:

### How to Contribute

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/AmazingFeature
   ```
3. **Commit your changes**
   ```bash
   git commit -m 'Add some AmazingFeature'
   ```
4. **Push to the branch**
   ```bash
   git push origin feature/AmazingFeature
   ```
5. **Open a Pull Request**

### Feature Ideas

- Automated payment verification via payment gateway API
- Subscription management with expiry dates
- Referral system (earn premium by inviting friends)
- Download statistics and analytics
- Custom file categories and tags
- Search functionality for uploaded files
- Multi-language support
- Scheduled broadcasts
- Integration with more URL shorteners
- Web dashboard for admin management

### Bug Reports

When reporting bugs, please include:
- Python version
- Operating system
- Error messages (full traceback)
- Steps to reproduce
- Expected vs actual behavior

---

## License

This project is licensed under the **MIT License**.

```
MIT License

Copyright (c) 2024 [Your Name]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Telegram: [@yourusername](https://t.me/x0deyen)

---

## Acknowledgments

**Built with:**
- [Pyrogram](https://docs.pyrogram.org/) - Telegram MTProto API Framework
- [ShrinkEarn](https://shrinkearn.com) - URL Shortening & Monetization
- SQLite - Lightweight database engine

**Special Thanks:**
- Telegram for their excellent Bot API
- Pyrogram community for documentation and support
- All contributors and users

---

**Made with ☕ and Python**

**Star ⭐ this repo if you find it useful!**
