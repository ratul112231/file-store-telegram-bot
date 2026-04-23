import base64
import asyncio
import requests
from urllib.parse import quote
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.errors import UserNotParticipant, ChatAdminRequired
from pyrogram.enums import ParseMode

from config import (
    API_ID, API_HASH, BOT_TOKEN, DB_CHANNEL, ADMINS, SHORTENER_API,
    PAYMENT_ADMIN, USER_WELCOME_TEXT, ADMIN_WELCOME_TEXT, BECOME_MEMBER_TEXT
)
from database import Database

# --- Initialization ---
bot = Client("FileStoreBot", api_id=39396720, api_hash=945f0314b982ab0847fd009e5e447b64, bot_token=8222385318:AAH6AK3nSOX2CPxLNAr9CQtqhJZfM-8Jhro)
db = Database()
user_states = {}

# --- Helper Functions ---
def is_admin(user_id: int) -> bool: return user_id in ADMINS
def encode_payload(p: str) -> str: return base64.urlsafe_b64encode(p.encode()).decode()
def decode_payload(p: str) -> str:
    try: return base64.urlsafe_b64decode(p.encode()).decode()
    except: return None

def shorten_url(long_url):
    if not SHORTENER_API or "d3d48de6b3ec0268e3d69a0f68869c6b40d94322" in SHORTENER_API: return long_url
    try:
        api_url = f"https://shrinkearn.com/st?api=d3d48de6b3ec0268e3d69a0f68869c6b40d94322&url=yourdestinationlink.com"
        response = requests.get(api_url, timeout=10)
        return response.text.strip() if response.ok and response.text.strip() else long_url
    except: return long_url

async def check_force_sub(user_id: int):
    not_joined = []
    for channel_id in db.get_fsub_channels():
        try:
            await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
        except UserNotParticipant:
            not_joined.append(channel_id)
        except Exception:
            pass
    return not_joined

async def delete_messages_after_delay(chat_id, message_ids, delay_minutes):
    if delay_minutes <= 0: return
    await asyncio.sleep(delay_minutes * 60)
    try: await bot.delete_messages(chat_id, message_ids)
    except: pass

# --- Core Bot Logic ---
@bot.on_message(filters.command(["start", "help"]) & filters.private)
async def start_command(_, message: Message):
    db.add_user(message.from_user)
    status = "admin" if is_admin(message.from_user.id) else db.get_user_status(message.from_user.id)
    
    if status == "banned": return await message.reply_text("🚫 You are banned from using this bot.", quote=True)
    
    if len(message.command) > 1:
        payload = message.command[1]
        if payload.startswith("unlock_"):
            original_payload = db.verify_unlock_token(payload.split("_", 1)[1], message.from_user.id)
            if original_payload:
                db.grant_temporary_access(message.from_user.id)
                await message.reply_text("✅ **Access Unlocked for 1 hour!**", quote=True)
                if original_payload != "None":
                    await process_payload(message, original_payload)
            else:
                await message.reply_text("❌ Invalid or expired unlock link. Please try again.", quote=True)
            return

        not_joined = await check_force_sub(message.from_user.id)
        if not_joined: return await show_force_sub_channels(message, not_joined, payload)
        
        if status in ["admin", "member", "unlocked"]: return await process_payload(message, payload)
        else: return await show_unlock_prompt(message, payload)
    
    if status == "admin": await show_admin_menu(message)
    else: await show_user_menu(message)

# NEW BATCH COMMAND
@bot.on_message(filters.command("batch") & filters.private)
async def batch_command(_, message: Message):
    if not is_admin(message.from_user.id): return

    try:
        if len(message.command) < 4:
            raise ValueError
        
        start_id = int(message.command[1])
        end_id = int(message.command[2])
        batch_name = " ".join(message.command[3:])

        if start_id >= end_id:
            return await message.reply_text("❌ Start message ID must be less than the end message ID.", quote=True)
        
        batch_id = db.add_batch(batch_name, start_id, end_id, message.from_user.id)
        link = f"https://t.me/{(await bot.get_me()).username}?start={encode_payload(f'batch_{batch_id}')}"
        
        await message.reply_text(f"✅ **Batch '{batch_name}' created!**\n\n- Contains: `{end_id - start_id + 1}` files.\n- Link: `{link}`", quote=True, disable_web_page_preview=True)

    except (ValueError, IndexError):
        await message.reply_text(
            "**Invalid Command Format**\n\n"
            "**Usage:** `/batch <start_msg_id> <end_msg_id> <Batch Name>`\n\n"
            "**Example:** `/batch 101 150 My Awesome Collection`",
            quote=True
        )

async def process_payload(message: Message, encoded_payload: str):
    payload = decode_payload(encoded_payload)
    if not payload: return await message.reply_text("⚠️ Invalid or expired link.", quote=True)
    if payload.startswith("file_"): await send_file(message, int(payload.split("_", 1)[1]))
    if payload.startswith("batch_"): await send_batch(message, int(payload.split("_", 1)[1]))

async def show_unlock_prompt(message: Message, original_payload: str):
    token = db.create_unlock_token(message.from_user.id, original_payload)
    deep_link = f"https://t.me/{(await bot.get_me()).username}?start=unlock_{token}"
    shortened_link = shorten_url(deep_link)
    buttons = [
        [InlineKeyboardButton("▶️ Watch an Ad", url=shortened_link)],
        [InlineKeyboardButton("💎 Go Premium", callback_data="become_member")]
    ]
    unlock_text = (
        "🚀 **Continue Using the Bot**\n\n"
        "To keep all features active, select an option below:"
    )
    await message.reply_text(unlock_text, reply_markup=InlineKeyboardMarkup(buttons), quote=True)

async def show_force_sub_channels(message: Message, channel_ids: list, payload: str):
    buttons = []
    for cid in channel_ids:
        try:
            chat = await bot.get_chat(cid)
            invite_link = chat.invite_link or f"https://t.me/{chat.username}"
            buttons.append([InlineKeyboardButton(f"Join {chat.title}", url=invite_link)])
        except Exception: pass
    buttons.append([InlineKeyboardButton("✅ I Have Joined, Retry", callback_data=f"retry_{payload}")])
    await message.reply_text("**Please Join Our Channels**\n\nYou must join our channel(s) to get files.", reply_markup=InlineKeyboardMarkup(buttons), quote=True)

# --- Menus & UI ---
async def show_user_menu(message: Message):
    await message.reply_text(USER_WELCOME_TEXT.format(name=message.from_user.first_name), quote=True)

async def show_admin_menu(message: Message, is_edit=False):
    text = ADMIN_WELCOME_TEXT.format(name=message.from_user.first_name)
    buttons = [
        [InlineKeyboardButton("📢 Broadcast", callback_data="broadcast"), InlineKeyboardButton("📊 Statistics", callback_data="stats")],
        [InlineKeyboardButton("👥 User Management", callback_data="user_mgmt"), InlineKeyboardButton("🔗 Force Sub", callback_data="force_sub_mgmt")],
        [InlineKeyboardButton("💰 Payment Settings", callback_data="payment_settings"), InlineKeyboardButton("⚙️ Bot Settings", callback_data="bot_settings")]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    
    if is_edit:
        try: await message.edit_text(text, reply_markup=reply_markup)
        except: pass
    else:
        await message.reply_text(text, reply_markup=reply_markup, quote=True)

# --- Callback Handler ---
@bot.on_callback_query()
async def handle_callbacks(_, query: Message):
    data, user_id = query.data, query.from_user.id
    
    is_public = data.startswith("retry_") or data == "become_member"
    if not is_admin(user_id) and not is_public: return await query.answer("🚫 Access Denied.", show_alert=True)

    if data.startswith("retry_"):
        payload = data.split("_", 1)[1]
        if not await check_force_sub(user_id):
            await query.message.delete()
            await process_payload(query.message, payload)
        else:
            await query.answer("You still haven't joined all channels.", show_alert=True)
        return

    if data == "back_admin": return await show_admin_menu(query.message, is_edit=True)
    
    if data == "become_member":
        upi = db.get_setting("upi_handle")
        qr = db.get_setting("qr_code_url")
        link = db.get_setting("payment_link")
        caption = BECOME_MEMBER_TEXT.format(upi_handle=upi)
        buttons = [[InlineKeyboardButton("Click Here to Pay (UPI Link)", url=link)]] if link and "http" in link else []
        try: await query.message.reply_photo(photo=qr, caption=caption, reply_markup=InlineKeyboardMarkup(buttons) if buttons else None, parse_mode=ParseMode.MARKDOWN)
        except: await query.message.reply_text(caption, reply_markup=InlineKeyboardMarkup(buttons) if buttons else None, parse_mode=ParseMode.MARKDOWN)
        await query.answer()
        return

    # --- Admin Callbacks ---
    if data == "stats":
        stats = db.get_stats()
        stats_text = (f"📊 **Bot Statistics**\n\n"
                      f"📁 **Content:** `{stats['files']}` files saved.\n"
                      f"👥 **Users:** `{stats['users']}` total users.\n"
                      f"💎 **Members:** `{stats['members']}` premium members.\n"
                      f"🚫 **Banned:** `{stats['banned']}` users banned.")
        await query.message.edit_text(stats_text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="back_admin")]]))

    elif data == "bot_settings":
        delete_time = db.get_setting("auto_delete_minutes")
        buttons = [[InlineKeyboardButton("⏱️ Change Auto-Delete Time", callback_data="change_autodelete")], [InlineKeyboardButton("⬅️ Back", callback_data="back_admin")]]
        await query.message.edit_text(f"⚙️ **Bot Settings**\n\n- Files are deleted after `{delete_time}` minutes.", reply_markup=InlineKeyboardMarkup(buttons))

    elif data == "change_autodelete":
        buttons = [[InlineKeyboardButton(f"{m} min", callback_data=f"set_delete_{m}") for m in [10, 30, 60]], [InlineKeyboardButton("Never (0)", callback_data="set_delete_0")], [InlineKeyboardButton("⬅️ Back", callback_data="bot_settings")]]
        await query.message.edit_text("Select the auto-delete time:", reply_markup=InlineKeyboardMarkup(buttons))

    elif data.startswith("set_delete_"):
        minutes = int(data.split("_")[-1])
        db.set_setting("auto_delete_minutes", str(minutes))
        await query.answer(f"✅ Auto-delete time set to {minutes} minutes.", show_alert=True)
        query.data = "bot_settings"
        await handle_callbacks(bot, query)

    elif data == "payment_settings":
        upi = db.get_setting('upi_handle')
        link = db.get_setting('payment_link')
        buttons = [[InlineKeyboardButton("✏️ UPI ID", callback_data="change_upi"), InlineKeyboardButton("🔗 Pay Link", callback_data="change_payment_link")], [InlineKeyboardButton("🖼️ QR Code", callback_data="change_qr")], [InlineKeyboardButton("⬅️ Back", callback_data="back_admin")]]
        await query.message.edit_text(f"💰 **Payment Settings**\n\n- **UPI:** `{upi}`\n- **Link:** `{link}`", reply_markup=InlineKeyboardMarkup(buttons))

    elif data == "user_mgmt":
        buttons = [
            [InlineKeyboardButton("➕ Add Member", callback_data="add_member"), InlineKeyboardButton("➖ Remove Member", callback_data="remove_member")],
            [InlineKeyboardButton("🚫 Ban User", callback_data="ban_user"), InlineKeyboardButton("✅ Unban User", callback_data="unban_user")],
            [InlineKeyboardButton("⬅️ Back", callback_data="back_admin")]
        ]
        await query.message.edit_text("👥 **User Management**", reply_markup=InlineKeyboardMarkup(buttons))
    
    elif data == "force_sub_mgmt":
        buttons = [[InlineKeyboardButton("➕ Add Channel", callback_data="add_channel")], [InlineKeyboardButton("⬅️ Back", callback_data="back_admin")]]
        await query.message.edit_text("Use the buttons to manage your force subscribe channels.", reply_markup=InlineKeyboardMarkup(buttons))
    
    prompts = {
        "broadcast": "Send the message to broadcast to all users.", "add_channel": "Forward a message from the channel or send its ID.",
        "change_upi": "Send the new UPI ID.", "change_payment_link": "Send the new payment link.", "change_qr": "Send the new QR code photo.",
        "add_member": "Send the User ID to make a member.", "remove_member": "Send the User ID to remove from members.",
        "ban_user": "Send the User ID to ban.", "unban_user": "Send the User ID to unban."
    }
    if data in prompts:
        user_states[user_id] = data
        back_map = {"change_upi": "payment_settings", "change_payment_link": "payment_settings", "change_qr": "payment_settings", "add_channel": "force_sub_mgmt"}
        back_callback = back_map.get(data, "user_mgmt" if "user" in data or "member" in data else "back_admin")
        await query.message.edit_text(prompts[data], reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data=back_callback)]]))

# --- Message Handler ---
@bot.on_message(filters.private & ~filters.command(["start", "help", "batch"]))
async def handle_private_messages(_, message: Message):
    user_id = message.from_user.id
    if not is_admin(user_id): return
    
    if user_id in user_states:
        state = user_states.pop(user_id)
        
        if state == "broadcast":
            users = db.get_broadcast_users()
            progress = await message.reply_text(f"📢 Broadcasting to {len(users)} users...", quote=True)
            s, f = 0, 0
            for u in users:
                try: await message.copy(u[0]); s += 1
                except: f += 1
                await asyncio.sleep(0.05)
            await progress.edit_text(f"✅ **Broadcast Complete**\n\n- Sent: `{s}` | Failed: `{f}`")
        
        elif state == "add_channel":
            try:
                cid = message.forward_from_chat.id if message.forward_from_chat else int(message.text)
                cname = (await bot.get_chat(cid)).title
                db.add_fsub_channel(cid, cname)
                await message.reply_text(f"✅ Channel '{cname}' added to force sub list.", quote=True)
            except: await message.reply_text("❌ Could not add channel. Make sure I am an admin there and the ID is correct.", quote=True)

        elif state == "change_upi": db.set_setting("upi_handle", message.text.strip()); await message.reply_text("✅ UPI ID updated.", quote=True)
        elif state == "change_payment_link": db.set_setting("payment_link", message.text.strip()); await message.reply_text("✅ Payment Link updated.", quote=True)
        elif state == "change_qr":
            if message.photo: db.set_setting("qr_code_url", message.photo.file_id); await message.reply_text("✅ QR Code updated.", quote=True)
            else: await message.reply_text("❌ Please send a photo.", quote=True)
        
        elif message.text and message.text.isdigit():
            target_id = int(message.text)
            if state == "add_member": db.set_user_member(target_id, True)
            elif state == "remove_member": db.set_user_member(target_id, False)
            elif state == "ban_user": db.set_user_banned(target_id, True)
            elif state == "unban_user": db.set_user_banned(target_id, False)
            await message.reply_text(f"✅ User `{target_id}` has been updated successfully.", quote=True)
        else:
            await message.reply_text("❌ Invalid input. Please send a numeric User ID.", quote=True)
        return

    # Default action for admins is to upload a single file
    if message.media: await handle_media_upload(message)

# --- File Operations ---
def get_file_info(message: Message):
    media = message.document or message.video or message.audio or message.photo
    if not media: return None
    return {'name': getattr(media, 'file_name', f"Media File"), 'type': message.media.value.split('.')[-1].title(), 'size': media.file_size}

async def handle_media_upload(message: Message):
    if not (file_info := get_file_info(message)): return await message.reply_text("❌ Unsupported file type.", quote=True)
    try:
        sent_msg = await message.forward(DB_CHANNEL)
        file_id = db.add_file(message, sent_msg, file_info)
        link = f"https://t.me/{(await bot.get_me()).username}?start={encode_payload(f'file_{file_id}')}"
        await message.reply_text(f"✅ **File Uploaded**\n\n🔗 **Link:** `{link}`", disable_web_page_preview=True, parse_mode=ParseMode.MARKDOWN, quote=True)
    except Exception as e: await message.reply_text(f"❌ Failed to save file: {e}", quote=True)

async def send_file(message, file_id):
    if not (file_data := db.get_file(file_id)): return await message.reply_text("❌ File Not Found.", quote=True)
    chat_id, msg_id, file_name = file_data
    delete_time = int(db.get_setting("auto_delete_minutes") or 0)
    
    # Show loading message
    loading_msg = await message.reply_text("⏳ **Sending file, please wait...**", quote=True)
    
    try:
        sent_msg = await bot.copy_message(message.chat.id, chat_id, msg_id)
        
        # Delete loading message
        await loading_msg.delete()
        
        if delete_time > 0:
            info_msg = await message.reply_text(
                f"⚠️ **Notice:**\n\n"
                f"This file will automatically **expire** and **self-destruct** in **{delete_time} minutes**.\n\n"
                f"Please forward this to your **Saved Messages** 🕒",
                quote=True
            )
            asyncio.create_task(delete_messages_after_delay(message.chat.id, [sent_msg.id, info_msg.id], delete_time))
    except Exception as e: 
        await loading_msg.delete()
        await message.reply_text(f"❌ Download Failed: {e}", quote=True)

async def send_batch(message, batch_id):
    if not (batch_data := db.get_batch(batch_id)): return await message.reply_text("❌ Batch Not Found.", quote=True)
    name, start_id, end_id = batch_data
    delete_time = int(db.get_setting("auto_delete_minutes") or 0)
    
    # Show loading message
    loading_msg = await message.reply_text(f"⏳ **Sending files, please wait...**", quote=True)
    
    sent_message_ids = []
    
    for msg_id in range(start_id, end_id + 1):
        try:
            sent_msg = await bot.copy_message(message.chat.id, DB_CHANNEL, msg_id)
            sent_message_ids.append(sent_msg.id)
            await asyncio.sleep(0.5)
        except Exception:
            pass
    
    # Delete loading message
    await loading_msg.delete()
    
    if delete_time > 0:
        info_msg = await message.reply_text(
            f"⚠️ **Notice:**\n\n"
            f"These files will automatically **expire** and **self-destruct** in **{delete_time} minutes**.\n\n"
            f"Please forward them to your **Saved Messages** 🕒",
            quote=True
        )
        
        # Store batch message IDs for deletion
        for msg_id in sent_message_ids:
            db.add_batch_message(batch_id, msg_id, message.from_user.id)
        
        # Add info message to deletion list
        sent_message_ids.append(info_msg.id)
        
        # Schedule deletion
        asyncio.create_task(delete_batch_messages(message.chat.id, batch_id, message.from_user.id, sent_message_ids, delete_time))

async def delete_batch_messages(chat_id, batch_id, user_id, message_ids, delay_minutes):
    """Delete batch messages after delay"""
    if delay_minutes <= 0: return
    await asyncio.sleep(delay_minutes * 60)
    try:
        await bot.delete_messages(chat_id, message_ids)
        db.clear_batch_messages(batch_id, user_id)
    except: pass

# --- Bot Startup ---
if __name__ == "__main__":
    db._create_tables()
    print("BOT STARTED")
    bot.run()
