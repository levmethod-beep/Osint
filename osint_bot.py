import os
import json
import re
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Tuple
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from telegram.constants import ParseMode
import logging
from playwright.async_api import async_playwright

# Global playwright instance
_playwright = None
_browser = None

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration
BOT_TOKEN = "8208285998:AAGrS794DrTdDLDF5lUxFDOF17FDt9dKnCU"
OWNER_ID = 7596091449
CHANNEL_1 = "@Osintbylev"
CHANNEL_2 = "@Free_cc_cards"
WATERMARK = "**@Tg_Starklev**"
DAILY_LIMIT = 50
API_1_BASE = "https://danger-vip-key.shop/api.php?key=CyberXWorm&number="
API_2_BASE = "http://india.42web.io/vehicle/?q="

# File to store user data
USERS_FILE = "users.json"

# Load users data
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

# Save users data
def save_users(users_data):
    with open(USERS_FILE, 'w') as f:
        json.dump(users_data, f, indent=4)

# Check if user has joined channels
async def check_channels(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    user_id = update.effective_user.id
    try:
        member1 = await context.bot.get_chat_member(CHANNEL_1, user_id)
        member2 = await context.bot.get_chat_member(CHANNEL_2, user_id)
        
        if member1.status in ['left', 'kicked'] or member2.status in ['left', 'kicked']:
            return False
        return True
    except Exception as e:
        logger.error(f"Error checking channels: {e}")
        return False

# Check daily limit
def check_daily_limit(user_id: int) -> Tuple[bool, int]:
    users_data = load_users()
    today = datetime.now().strftime("%Y-%m-%d")
    
    if str(user_id) not in users_data:
        users_data[str(user_id)] = {
            "searches": 0,
            "last_reset": today,
            "joined_at": datetime.now().isoformat()
        }
        save_users(users_data)
        return True, 0
    
    user = users_data[str(user_id)]
    last_reset = user.get("last_reset", today)
    
    # Reset if new day
    if last_reset != today:
        user["searches"] = 0
        user["last_reset"] = today
        save_users(users_data)
    
    searches = user.get("searches", 0)
    remaining = DAILY_LIMIT - searches
    
    if searches >= DAILY_LIMIT:
        return False, remaining
    
    return True, remaining

# Increment search count
def increment_search(user_id: int):
    users_data = load_users()
    today = datetime.now().strftime("%Y-%m-%d")
    
    if str(user_id) not in users_data:
        users_data[str(user_id)] = {
            "searches": 1,
            "last_reset": today,
            "joined_at": datetime.now().isoformat()
        }
    else:
        users_data[str(user_id)]["searches"] = users_data[str(user_id)].get("searches", 0) + 1
        users_data[str(user_id)]["last_reset"] = today
    
    save_users(users_data)

# Animated progress bar for /start
async def animated_start(update: Update, context: ContextTypes.DEFAULT_TYPE, message=None):
    if message is None:
        if update.message:
            message = await update.message.reply_text("🔴 **INITIALIZING SYSTEM...**")
        elif update.callback_query:
            message = await update.callback_query.message.reply_text("🔴 **INITIALIZING SYSTEM...**")
        else:
            return
    
    progress_messages = [
        "🔴 **INITIALIZING SYSTEM...**\n`[░░░░░░░░░░] 0%`",
        "🟠 **LOADING MODULES...**\n`[██░░░░░░░░] 20%`",
        "🟡 **CONNECTING TO DATABASE...**\n`[████░░░░░░] 40%`",
        "🟢 **AUTHENTICATING USER...**\n`[██████░░░░] 60%`",
        "🔵 **LOADING OSINT TOOLS...**\n`[████████░░] 80%`",
        "🟣 **FINALIZING SETUP...**\n`[██████████] 100%`",
    ]
    
    for i, progress_text in enumerate(progress_messages):
        await asyncio.sleep(0.5)
        await message.edit_text(progress_text, parse_mode=ParseMode.MARKDOWN)
    
    await asyncio.sleep(0.3)
    
    # Hacker-style menu
    menu_text = """
╔═══════════════════════════════╗
║   🔥 OSINT BOT 🔥            ║
║   DANGEROUS TOOLS ACTIVE      ║
╠═══════════════════════════════╣
║  ⚡ SYSTEM STATUS: ONLINE     ║
║  🔐 SECURITY: ENABLED         ║
║  🎯 MODE: STEALTH             ║
╠═══════════════════════════════╣
║  📱 /num - Phone OSINT        ║
║  🚗 /veh - Vehicle OSINT      ║
║  📊 /stats - Your Statistics  ║
╠═══════════════════════════════╣
║  ⚠️  Join Required Channels   ║
║  📢 Daily Limit: 50 Searches  ║
╚═══════════════════════════════╝
"""
    
    keyboard = [
        [InlineKeyboardButton("📱 Phone OSINT", callback_data="help_num")],
        [InlineKeyboardButton("🚗 Vehicle OSINT", callback_data="help_veh")],
        [InlineKeyboardButton("📊 Statistics", callback_data="stats")],
        [InlineKeyboardButton("📢 Join Channels", url=f"https://t.me/{CHANNEL_1.replace('@', '')}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await message.edit_text(menu_text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Check if user joined channels
    if not await check_channels(update, context):
        keyboard = [
            [InlineKeyboardButton("📢 Join Channel 1", url=f"https://t.me/{CHANNEL_1.replace('@', '')}")],
            [InlineKeyboardButton("📢 Join Channel 2", url=f"https://t.me/{CHANNEL_2.replace('@', '')}")],
            [InlineKeyboardButton("✅ Verify", callback_data="verify_channels")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            f"⚠️ **ACCESS DENIED**\n\n"
            f"You must join both channels to use this bot:\n"
            f"1. {CHANNEL_1}\n"
            f"2. {CHANNEL_2}\n\n"
            f"Click 'Verify' after joining.",
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    await animated_start(update, context)

# Verify channels callback
async def verify_channels(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if await check_channels(update, context):
        await query.edit_message_text("✅ **VERIFIED!** You can now use the bot.")
        await asyncio.sleep(1)
        # Start animation from the query message
        message = query.message
        await animated_start(update, context, message=message)
    else:
        await query.answer("❌ Please join both channels first!", show_alert=True)

# Number OSINT command
async def num_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Check channels
    if not await check_channels(update, context):
        await update.message.reply_text("⚠️ Please join the required channels first!")
        return
    
    # Check daily limit
    can_search, remaining = check_daily_limit(user_id)
    if not can_search:
        await update.message.reply_text(
            f"❌ **DAILY LIMIT REACHED**\n\n"
            f"You have used all {DAILY_LIMIT} searches today.\n"
            f"Limit resets at midnight."
        )
        return
    
    if not context.args:
        await update.message.reply_text(
            "📱 **PHONE OSINT**\n\n"
            "Usage: `/num <phone_number>`\n"
            "Example: `/num 9876543210`",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    phone_number = context.args[0]
    
    # Validate phone number (basic check)
    if not phone_number.isdigit() or len(phone_number) < 10:
        await update.message.reply_text("❌ Invalid phone number format!")
        return
    
    processing_msg = await update.message.reply_text("🔍 **SCANNING...**\n`[████░░░░░░] 50%`", parse_mode=ParseMode.MARKDOWN)
    
    try:
        async with aiohttp.ClientSession() as session:
            url = f"{API_1_BASE}{phone_number}"
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Format JSON response
                    json_text = json.dumps(data, indent=2, ensure_ascii=False)
                    
                    # Add watermark
                    result_text = f"📱 **PHONE OSINT RESULT**\n\n```json\n{json_text}\n```\n\n{WATERMARK}"
                    
                    # Check message length (Telegram limit is 4096)
                    if len(result_text) > 4000:
                        # Send as file if too long
                        await processing_msg.delete()
                        await update.message.reply_document(
                            document=json.dumps(data, indent=2).encode(),
                            filename=f"phone_{phone_number}.json",
                            caption=f"📱 Phone OSINT Result\n\n{WATERMARK}"
                        )
                    else:
                        await processing_msg.edit_text(result_text, parse_mode=ParseMode.MARKDOWN)
                    
                    increment_search(user_id)
                    remaining -= 1
                    await update.message.reply_text(f"✅ Search completed! Remaining: {remaining}/{DAILY_LIMIT}")
                else:
                    await processing_msg.edit_text(f"❌ API Error: Status {response.status}")
    except Exception as e:
        logger.error(f"Error in num_command: {e}")
        await processing_msg.edit_text(f"❌ Error: {str(e)}")

# Vehicle OSINT command
async def veh_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Check channels
    if not await check_channels(update, context):
        await update.message.reply_text("⚠️ Please join the required channels first!")
        return
    
    # Check daily limit
    can_search, remaining = check_daily_limit(user_id)
    if not can_search:
        await update.message.reply_text(
            f"❌ **DAILY LIMIT REACHED**\n\n"
            f"You have used all {DAILY_LIMIT} searches today.\n"
            f"Limit resets at midnight."
        )
        return
    
    if not context.args:
        await update.message.reply_text(
            "🚗 **VEHICLE OSINT**\n\n"
            "Usage: `/veh <vehicle_number>`\n"
            "Example: `/veh HR26EV0001`",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    vehicle_number = " ".join(context.args).upper()
    
    processing_msg = await update.message.reply_text("🔍 **SCANNING VEHICLE...**\n`[████░░░░░░] 50%`", parse_mode=ParseMode.MARKDOWN)
    
    try:
        # Use Playwright to handle JavaScript-based API
        global _playwright, _browser
        
        if _playwright is None:
            _playwright = await async_playwright().start()
            _browser = await _playwright.chromium.launch(headless=True)
        
        page = await _browser.new_page()
        url = f"{API_2_BASE}{vehicle_number}"
        
        try:
            # Navigate to the page and wait for JavaScript to execute
            await page.goto(url, wait_until="networkidle", timeout=30000)
            
            # Wait a bit for JavaScript redirects and cookie setting
            await asyncio.sleep(2)
            
            # Try to wait for JSON content
            try:
                await page.wait_for_function(
                    "document.body.innerText.trim().startsWith('{')",
                    timeout=10000
                )
            except:
                # If timeout, continue anyway
                pass
            
            # Get the JSON from page body
            text = await page.inner_text('body')
            
            # Check if we got JSON
            if text.strip().startswith('{'):
                try:
                    data = json.loads(text.strip())
                except json.JSONDecodeError as e:
                    raise ValueError(f"Failed to parse JSON: {str(e)}")
            else:
                raise ValueError("No JSON response received from API")
            
            await page.close()
            
        except Exception as e:
            await page.close()
            raise e
        
        # Remove copyright field if exists
        if isinstance(data, dict) and 'copyright' in data:
            del data['copyright']
            
            # Format JSON response
            json_text = json.dumps(data, indent=2, ensure_ascii=False)
            
            # Add watermark
            result_text = f"🚗 **VEHICLE OSINT RESULT**\n\n```json\n{json_text}\n```\n\n{WATERMARK}"
            
            # Check message length
            if len(result_text) > 4000:
                await processing_msg.delete()
                await update.message.reply_document(
                    document=json.dumps(data, indent=2).encode(),
                    filename=f"vehicle_{vehicle_number}.json",
                    caption=f"🚗 Vehicle OSINT Result\n\n{WATERMARK}"
                )
            else:
                await processing_msg.edit_text(result_text, parse_mode=ParseMode.MARKDOWN)
            
            increment_search(user_id)
            remaining -= 1
            await update.message.reply_text(f"✅ Search completed! Remaining: {remaining}/{DAILY_LIMIT}")
    except Exception as e:
        logger.error(f"Error in veh_command: {e}")
        error_msg = str(e)
        if len(error_msg) > 500:
            error_msg = error_msg[:500] + "..."
        await processing_msg.edit_text(f"❌ **ERROR**\n\n{error_msg}\n\n{WATERMARK}")

# Statistics command
async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    users_data = load_users()
    
    if str(user_id) not in users_data:
        await update.message.reply_text("📊 **STATISTICS**\n\nNo searches yet!")
        return
    
    user = users_data[str(user_id)]
    searches = user.get("searches", 0)
    remaining = DAILY_LIMIT - searches
    
    stats_text = f"""
📊 **YOUR STATISTICS**

🔍 Searches Today: {searches}/{DAILY_LIMIT}
⏳ Remaining: {remaining}
📅 Last Reset: {user.get('last_reset', 'N/A')}
"""
    
    await update.message.reply_text(stats_text, parse_mode=ParseMode.MARKDOWN)

# Broadcast command (owner only)
async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id != OWNER_ID:
        await update.message.reply_text("❌ Access denied!")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: `/broadcast <message>`", parse_mode=ParseMode.MARKDOWN)
        return
    
    message_text = " ".join(context.args)
    users_data = load_users()
    
    sent = 0
    failed = 0
    
    status_msg = await update.message.reply_text(f"📢 Broadcasting to {len(users_data)} users...")
    
    for user_id_str in users_data.keys():
        try:
            await context.bot.send_message(
                chat_id=int(user_id_str),
                text=f"📢 **BROADCAST**\n\n{message_text}\n\n{WATERMARK}",
                parse_mode=ParseMode.MARKDOWN
            )
            sent += 1
        except Exception as e:
            logger.error(f"Failed to send to {user_id_str}: {e}")
            failed += 1
        await asyncio.sleep(0.1)  # Rate limiting
    
    await status_msg.edit_text(f"✅ Broadcast complete!\nSent: {sent}\nFailed: {failed}")

# Handle media broadcast (owner sending media or replying to media)
async def handle_media_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id != OWNER_ID:
        return
    
    users_data = load_users()
    sent = 0
    failed = 0
    
    # Check if owner sent photo directly
    if update.message.photo:
        photo = update.message.photo[-1]
        file_id = photo.file_id
        caption = update.message.caption or ""
        
        status_msg = await update.message.reply_text(f"📢 Broadcasting photo to {len(users_data)} users...")
        
        for user_id_str in users_data.keys():
            try:
                await context.bot.send_photo(
                    chat_id=int(user_id_str),
                    photo=file_id,
                    caption=f"📢 **BROADCAST**\n\n{caption}\n\n{WATERMARK}" if caption else f"📢 **BROADCAST**\n\n{WATERMARK}",
                    parse_mode=ParseMode.MARKDOWN
                )
                sent += 1
            except Exception as e:
                logger.error(f"Failed to send to {user_id_str}: {e}")
                failed += 1
            await asyncio.sleep(0.1)
        
        await status_msg.edit_text(f"✅ Broadcast complete!\nSent: {sent}\nFailed: {failed}")
        return
    
    # Check if owner sent video directly
    if update.message.video:
        video = update.message.video
        file_id = video.file_id
        caption = update.message.caption or ""
        
        status_msg = await update.message.reply_text(f"📢 Broadcasting video to {len(users_data)} users...")
        
        for user_id_str in users_data.keys():
            try:
                await context.bot.send_video(
                    chat_id=int(user_id_str),
                    video=file_id,
                    caption=f"📢 **BROADCAST**\n\n{caption}\n\n{WATERMARK}" if caption else f"📢 **BROADCAST**\n\n{WATERMARK}",
                    parse_mode=ParseMode.MARKDOWN
                )
                sent += 1
            except Exception as e:
                logger.error(f"Failed to send to {user_id_str}: {e}")
                failed += 1
            await asyncio.sleep(0.1)
        
        await status_msg.edit_text(f"✅ Broadcast complete!\nSent: {sent}\nFailed: {failed}")
        return
    
    # Check if owner replied to media
    if update.message.reply_to_message:
        caption = update.message.caption or ""
        
        if update.message.reply_to_message.photo:
            photo = update.message.reply_to_message.photo[-1]
            file_id = photo.file_id
            
            status_msg = await update.message.reply_text(f"📢 Broadcasting photo to {len(users_data)} users...")
            
            for user_id_str in users_data.keys():
                try:
                    await context.bot.send_photo(
                        chat_id=int(user_id_str),
                        photo=file_id,
                        caption=f"📢 **BROADCAST**\n\n{caption}\n\n{WATERMARK}" if caption else f"📢 **BROADCAST**\n\n{WATERMARK}",
                        parse_mode=ParseMode.MARKDOWN
                    )
                    sent += 1
                except Exception as e:
                    logger.error(f"Failed to send to {user_id_str}: {e}")
                    failed += 1
                await asyncio.sleep(0.1)
            
            await status_msg.edit_text(f"✅ Broadcast complete!\nSent: {sent}\nFailed: {failed}")
            return
        
        elif update.message.reply_to_message.video:
            video = update.message.reply_to_message.video
            file_id = video.file_id
            
            status_msg = await update.message.reply_text(f"📢 Broadcasting video to {len(users_data)} users...")
            
            for user_id_str in users_data.keys():
                try:
                    await context.bot.send_video(
                        chat_id=int(user_id_str),
                        video=file_id,
                        caption=f"📢 **BROADCAST**\n\n{caption}\n\n{WATERMARK}" if caption else f"📢 **BROADCAST**\n\n{WATERMARK}",
                        parse_mode=ParseMode.MARKDOWN
                    )
                    sent += 1
                except Exception as e:
                    logger.error(f"Failed to send to {user_id_str}: {e}")
                    failed += 1
                await asyncio.sleep(0.1)
            
            await status_msg.edit_text(f"✅ Broadcast complete!\nSent: {sent}\nFailed: {failed}")
            return

# Callback query handler
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "verify_channels":
        await verify_channels(update, context)
    elif query.data == "help_num":
        await query.edit_message_text(
            "📱 **PHONE OSINT**\n\n"
            "Usage: `/num <phone_number>`\n"
            "Example: `/num 9876543210`\n\n"
            "This command searches for information about a phone number.",
            parse_mode=ParseMode.MARKDOWN
        )
    elif query.data == "help_veh":
        await query.edit_message_text(
            "🚗 **VEHICLE OSINT**\n\n"
            "Usage: `/veh <vehicle_number>`\n"
            "Example: `/veh HR26EV0001`\n\n"
            "This command searches for information about a vehicle number.",
            parse_mode=ParseMode.MARKDOWN
        )
    elif query.data == "stats":
        user_id = query.from_user.id
        users_data = load_users()
        
        if str(user_id) not in users_data:
            await query.edit_message_text("📊 **STATISTICS**\n\nNo searches yet!")
            return
        
        user = users_data[str(user_id)]
        searches = user.get("searches", 0)
        remaining = DAILY_LIMIT - searches
        
        stats_text = f"""
📊 **YOUR STATISTICS**

🔍 Searches Today: {searches}/{DAILY_LIMIT}
⏳ Remaining: {remaining}
📅 Last Reset: {user.get('last_reset', 'N/A')}
"""
        await query.edit_message_text(stats_text, parse_mode=ParseMode.MARKDOWN)

def main():
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("num", num_command))
    application.add_handler(CommandHandler("veh", veh_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("broadcast", broadcast_command))
    application.add_handler(CallbackQueryHandler(callback_handler))
    # Handle media broadcast (photo or video, with or without reply)
    application.add_handler(MessageHandler(
        (filters.PHOTO | filters.VIDEO) & (filters.REPLY | ~filters.REPLY),
        handle_media_broadcast
    ))
    
    # Start bot
    logger.info("Bot starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()


