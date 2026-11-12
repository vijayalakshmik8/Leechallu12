import os
import time
import logging
import asyncio
import aiohttp
import subprocess
import random
import string
import re
import pytz
import glob
import tempfile
import shutil
import html
from datetime import datetime, timedelta
from urllib.parse import urlparse
from pyrogram import Client, filters, idle
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InputMediaPhoto
from pyrogram.errors import UserNotParticipant
import yt_dlp
from aiohttp import web
from leech import register_leech_handlers
from youtube_formats import (
    supported_quality_heights,
    extract_info_with_cookie_fallback,
    selected_video_height,
    youtube_format_for_height,
)

# Logging Setup
logging.basicConfig(level=logging.INFO)

API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

# Channel IDs
DATABASE_CHANNEL_ID = int(os.environ.get("DATABASE_CHANNEL_ID", "-1004396122384"))
LOG_CHANNEL_ID = int(os.environ.get("LOG_CHANNEL_ID", "-1004441596603"))
ALLOWED_GROUP_ID = int(os.environ.get("ALLOWED_GROUP_ID", "0"))

ADMIN_ID = 1727225499
ADMINS = [ADMIN_ID]

# Force Subscribe Channels
F_SUB_CHANNEL_1 = os.environ.get("F_SUB_CHANNEL_1", "AlluTvSerials")
F_SUB_CHANNEL_2 = os.environ.get("F_SUB_CHANNEL_2", "leech_Update_Channel")

# Start & Command Reactions
REACTIONS = ["🤝", "😇", "🤗", "😍", "👍", "🎅", "😐", "🥰", "🤩", "😱", "🤣", "😘", "👏", "😛", "😈", "🎉", "⚡️", "🫡", "🤓", "😎", "🏆", "🔥", "🤭", "🌚", "🆒", "👻", "😁"]

# Footer Branding Blockquote Format
def get_branding_footer():
    return "\n\n> **Powered by Anujith ❤️**\n> **@AlluTvSerials**"

async def send_random_reaction(client, message):
    try:
        reaction = random.choice(REACTIONS)
        await client.set_message_reaction(
            chat_id=message.chat.id,
            message_id=message.id,
            reaction=reaction
        )
    except Exception as e:
        pass

# Premium, Referral & Payment Variables
REFERAL_COUNT = int(os.environ.get('REFERAL_COUNT', '20'))
REFERAL_PREMEIUM_TIME = os.environ.get('REFERAL_PREMEIUM_TIME', '1month')
PAYMENT_QR = os.environ.get('PAYMENT_QR', 'https://ibb.co/xtr2Bb71')
PAYMENT_TEXT = os.environ.get('PAYMENT_TEXT', '<b>- ᴀᴠᴀɪʟᴀʙʟᴇ ᴘʟᴀns ❤️ - \n- 15ʀs - 1 ᴅᴀʏꜱ\n- 40ʀs - 1 ᴡᴇᴇ𝗸\n- 89ʀs - 1 ᴍᴏɴᴛʜs\n\n🎁 ᴘʀᴇᴍɪᴜᴍ ғᴇᴀᴛ𝘂ʀᴇs 🎁\n\n○ ɴᴏ ɴᴇᴇᴅ ᴛᴏ ᴠᴇʀɪғʏ\n○ ɴᴏ ɴᴇᴇْد ᴛᴏ ᴏ𝚙𝚎ɴ ʟɪɴ𝚔\n○ ᴅɪʀᴇᴄⵜ ғɪʟ𝚎s\n○ ᴀᴅ-ғʀᴇᴇ ᴇxᴘᴇʀɪᴇɴᴄᴇ\n○ ʜɪɢʜ-sᴘᴇᴇᴅ ᴅᴏᴡɴʟᴏᴀᴅ ʟɪɴ𝚔\n○ ᴍᴜʟᴛɪ-ᴘʟᴀʏᴇ🇷 sᴛʀᴇᴀᴍ𝘪nings ʟ𝑖ɴ𝚔𝘀\n○ ᴜɴʟ𝙸ᴍ𝙸ᴛᴇD ᴍᴏᴠɪᴇs & sᴇʀɪᴇs\n○ ꜰᴜʟʟ ᴀᴅᴍɪɴ sᴜ𝚙𝚙ᴏʀᴛ\n○ ʀᴇǫᴜᴇsْت ᴡɪʟʟ ʙᴇ ᴄᴏᴍᴘʟᴇ́tᴇْد ɪɴ 1ʜ ɪꜰ ᴀᴠᱟ𝚒𝚕ᱟʙ𝚕ᴇ\n\n✨ ᴜ𝚙ɪ ɪᴅ - <code>vijayalakshmik8825@ybl</code>\n\nᴄʟɪᴄᴋ ᴛᴏ 𝚌𝚑𝚎𝚌𝚔 ʏᴏ𝚞𝚛 𝚊𝚌𝚝𝚒𝚟𝚎 ᴘ𝚕𝚊𝚗 /myplan\n\n💢 ᴍᴜsᴛ sᴇɴᴅ sᴄʀᴇᴇnsʜᴏْت ᴀғᴛᴇ🇷 ᴘᴀʏᴍᴇɴᴛ\n\n‼️ ᴀғᴛᴇ🇷 sᴇɴᴅɪɴɢ ᴀ sᴄʀᴇᴇnsʜᴏᴛ ᴘʟᴇᴀsᴇ ɢɪᴠᴇ ᴜs sᴏᴍᴇ ᴛⵉᴍེ་ ᴛ𝙾 adⴷ yᴏU ɪɴ 𝘁𝗵𝗲 ᴘʀᴇᴍɪᴜᴍ</b>')
OWNER_USERNAME = os.environ.get('OWNER_USERNAME', 'Anujith1238')

# Token Verification Info :
VERIFY = bool(os.environ.get('VERIFY', True))
VERIFY_SHORTLINK_URL = os.environ.get('VERIFY_SHORTLINK_URL', 'linkshortify.com')
VERIFY_SHORTLINK_API = os.environ.get('VERIFY_SHORTLINK_API', '927f420bfcbeda36287288f7e98110467feedbef')
VERIFY_TUTORIAL = os.environ.get('VERIFY_TUTORIAL', 'https://t.me/How_or_Open_Link')

app = Client("LeechBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

USER_THUMBNAILS = {}
WAITING_FOR_THUMB = set()
USER_YTDL_LINKS = {}
USER_FILE_MODES = {}
USER_STATES = {}
RENAME_DATA = {}

ACTIVE_TASKS = {}
USER_TASK_LIMIT = 2
CANCEL_REQUESTS = set()

PREMIUM_USERS = {}
VERIFIED_USERS = {}
BANNED_USERS = set()
REDEEM_CODE = {}

class DummyDB:
    async def get_user(self, user_id):
        return {}
    async def update_user(self, user_data):
        pass

db = DummyDB()

class TempHolder:
    def __init__(self):
        self.U_NAME = "ott_downloader5_bot"
temp = TempHolder()

PREMIUM_LOGS = LOG_CHANNEL_ID

def generate_code(length=10):
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for _ in range(length))

async def get_seconds(time_string):
    time_string = time_string.strip().lower()
    if time_string.endswith("min"):
        val = int(time_string[:-3])
        return val * 60
    elif time_string.endswith("m"):
        val = int(time_string[:-1])
        return val * 60
    elif time_string.endswith("hour") or time_string.endswith("hrs"):
        val = int(time_string[:-4]) if time_string.endswith("hour") else int(time_string[:-3])
        return val * 3600
    elif time_string.endswith("h"):
        val = int(time_string[:-1])
        return val * 3600
    elif time_string.endswith("day") or time_string.endswith("days"):
        val = int(time_string[:-3]) if time_string.endswith("day") else int(time_string[:-4])
        return val * 86400
    elif time_string.endswith("d"):
        val = int(time_string[:-1])
        return val * 86400
    elif time_string.endswith("month"):
        val = int(time_string[:-5])
        return val * 2592000
    else:
        if time_string.isdigit():
            return int(time_string) * 86400
    return 0

START_IMAGE_URL = "https://ibb.co/2YLPDBzQ"

async def web_handler(request):
    return web.Response(text="Bot is Live! 🚀")

async def start_web_server():
    web_app = web.Application()
    web_app.add_routes([web.get("/", web_handler)])
    runner = web.AppRunner(web_app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logging.info(f"Web server started on port {port}")

def human_bytes(size):
    units = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size >= 1024 and i < len(units) - 1:
        size /= 1024
        i += 1
    return f"{size:.2f} {units[i]}"

def get_youtube_cookie_file():
    # instagram_com_cookies.txt is for Instagram and should not be sent to YouTube.
    return "cookies.txt" if os.path.isfile("cookies.txt") else None

def is_premium(user_id):
    if user_id == ADMIN_ID:
        return True
    if user_id in PREMIUM_USERS:
        if time.time() < PREMIUM_USERS[user_id]:
            return True
        else:
            del PREMIUM_USERS[user_id]
    return False

def is_verified(user_id):
    if is_premium(user_id):
        return True
    if not VERIFY:
        return True
    if user_id in VERIFIED_USERS:
        if time.time() < VERIFIED_USERS[user_id]:
            return True
        else:
            del VERIFIED_USERS[user_id]
    return False

async def get_shortlink(url):
    api_url = f"https://{VERIFY_SHORTLINK_URL}/api?api={VERIFY_SHORTLINK_API}&url={url}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, timeout=10) as response:
                data = await response.json()
                if data.get("status") == "success":
                    return data.get("shortenedUrl")
    except Exception as e:
        logging.error(f"Error fetching shortlink: {e}")
    return url

async def verification_keyboard(client, user_id):
    bot_info = await client.get_me()
    bot_username = bot_info.username
    long_url = f"https://t.me/{bot_username}?start=verify_{user_id}"
    short_url = await get_shortlink(long_url)
    
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔗 Click Here to Verify", url=short_url)],
        [InlineKeyboardButton("❓ How to Open Link", url=VERIFY_TUTORIAL)]
    ])

async def check_fsub(client, user_id):
    if user_id == ADMIN_ID:
        return True
    
    channels = [F_SUB_CHANNEL_1, F_SUB_CHANNEL_2]
    for channel in channels:
        try:
            await client.get_chat_member(channel, user_id)
        except UserNotParticipant:
            return False
        except Exception:
            try:
                ch = channel if channel.startswith("@") else f"@{channel}"
                await client.get_chat_member(ch, user_id)
            except Exception:
                pass
    return True

async def not_joined_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Join Update Channel 1", url="https://t.me/AlluTvSerials")],
        [InlineKeyboardButton("📢 Join Update Channel 2", url="https://t.me/leech_Update_Channel")],
        [InlineKeyboardButton("🔄 Try Again", callback_data="check_fsub")]
    ])

def get_video_info(file_path):
    duration = 0
    width = 0
    height = 0
    try:
        cmd = [
            "ffprobe", "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "format=duration:stream=width,height",
            "-of", "default=noprint_wrappers=1:nokey=1",
            file_path
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        lines = result.stdout.strip().split("\n")
        if len(lines) >= 3:
            width = int(lines[0]) if lines[0].isdigit() else 0
            height = int(lines[1]) if lines[1].isdigit() else 0
            duration = int(float(lines[2])) if lines[2] else 0
    except Exception as e:
        logging.error(f"Error getting video info: {e}")
    return duration, width, height

def generate_thumbnail(video_path, user_id):
    os.makedirs("thumbnails", exist_ok=True)
    thumb_path = f"thumbnails/auto_{user_id}.jpg"
    try:
        cmd = [
            "ffmpeg", "-ss", "00:00:05", "-i", video_path,
            "-vframes", "1", "-q:v", "2", thumb_path, "-y"
        ]
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if os.path.exists(thumb_path) and os.path.getsize(thumb_path) > 0:
            return thumb_path
    except Exception as e:
        logging.error(f"Error generating thumbnail: {e}")
    return None

def download_youtube_thumbnail(thumbnail_url, user_id):
    os.makedirs("thumbnails", exist_ok=True)
    thumb_path = f"thumbnails/yt_{user_id}.jpg"
    try:
        import requests
        response = requests.get(thumbnail_url, timeout=10)
        if response.status_code == 200:
            with open(thumb_path, "wb") as f:
                f.write(response.content)
            if os.path.exists(thumb_path) and os.path.getsize(thumb_path) > 0:
                converted_thumb = f"thumbnails/thumb_{user_id}.jpg"
                result = subprocess.run(
                    ["ffmpeg", "-y", "-i", thumb_path, "-vf",
                     "scale=320:320:force_original_aspect_ratio=decrease",
                     "-q:v", "5", converted_thumb],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )
                if os.path.exists(thumb_path):
                    os.remove(thumb_path)
                if result.returncode == 0 and os.path.exists(converted_thumb):
                    return converted_thumb
                elif os.path.exists(thumb_path):
                    return thumb_path
    except Exception as e:
        logging.error(f"Error downloading YouTube thumbnail: {e}")
    return None

def get_progress_bar(percentage):
    completed = int(percentage / 10)
    remaining = 10 - completed
    return "█" * completed + "░" * remaining

async def download_thumbnail_from_source(client, thumb_source, user_id):
    os.makedirs("thumbnails", exist_ok=True)
    custom_thumb_path = f"thumbnails/custom_{user_id}.jpg"
    try:
        if "t.me/" in thumb_source:
            parts = thumb_source.strip("/").split("/")
            msg_id = int(parts[-1])
            channel_username = parts[-2]
            target_msg = await client.get_messages(channel_username, msg_id)
            if target_msg and target_msg.media:
                downloaded_thumb = await client.download_media(target_msg, file_name=custom_thumb_path)
                if downloaded_thumb and os.path.exists(downloaded_thumb):
                    return downloaded_thumb
        else:
            async with aiohttp.ClientSession() as session:
                async with session.get(thumb_source) as resp:
                    if resp.status == 200:
                        with open(custom_thumb_path, "wb") as f:
                            f.write(await resp.read())
                        if os.path.exists(custom_thumb_path) and os.path.getsize(custom_thumb_path) > 0:
                            return custom_thumb_path
    except Exception as e:
        logging.error(f"Failed to fetch custom thumbnail from -t: {e}")
    return None

def download_instagram_photos(url, download_path):
    cookie_file_path = "instagram_com_cookies.txt" if os.path.exists("instagram_com_cookies.txt") else "cookies.txt"
    ydl_opts = {
        "outtmpl": os.path.join(download_path, "%(id)s_%(autonumber)s.%(ext)s"),
        "quiet": True,
        "no_warnings": True,
        "ignoreerrors": True,
        "noplaylist": False,
        "retries": 3,
        "extractor_retries": 3,
        "cookiefile": cookie_file_path if os.path.exists(cookie_file_path) else None,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.extract_info(url, download=True)

    image_extensions = ("*.jpg", "*.jpeg", "*.png", "*.webp")
    images = []
    for ext in image_extensions:
        images.extend(glob.glob(os.path.join(download_path, ext)))
    return sorted(set(images))

@app.on_message(filters.command("id") & (filters.private | filters.chat(ALLOWED_GROUP_ID)))
async def id_command_handler(client: Client, message: Message):
    await send_random_reaction(client, message)
    
    target_user = message.from_user
    chat_info = message.chat
    forward_info = message.forward_from_chat
    forward_sender_name = message.forward_sender_name
    forward_from = message.forward_from

    response_text = ""

    if forward_info:
        f_title = forward_info.title or "Unknown"
        f_username = f"@{forward_info.username}" if forward_info.username else "No Username"
        f_id = forward_info.id
        f_type = forward_info.type
        
        response_text = (
            f"📌 Forwarded Source Info:\n"
            f"📁 Title/Name: {f_title}\n"
            f"📁 Type: {f_type}\n"
            f"📁 Chat ID: {f_id}\n"
            f"📁 Username: {f_username}\n"
        )
    elif forward_from:
        response_text = (
            f"📌 Forwarded User Info:\n"
            f"📁 First Name: {forward_from.first_name}\n"
            f"📁 User ID: {forward_from.id}\n"
            f"📁 Username: @{forward_from.username if forward_from.username else 'None'}\n"
        )
    elif forward_sender_name:
        response_text = (
            f"📌 Forwarded Source Info:\n"
            f"📁 Sender Name: {forward_sender_name}\n"
        )

    elif message.reply_to_message and message.reply_to_message.from_user:
        target_user = message.reply_to_message.from_user
        first_name = target_user.first_name or "None"
        last_name = target_user.last_name or ""
        username = f"@{target_user.username}" if target_user.username else "No Username"
        user_id = target_user.id
        dc_id = getattr(target_user, "dc_id", "Unknown")

        response_text = (
            f"👤 Replied User Info:\n"
            f"📁 First Name: {first_name} {last_name}\n"
            f"📁 Username: {username}\n"
            f"📁 Telegram ID: {user_id}\n"
            f"📁 Data Centre: {dc_id}\n"
        )

    if chat_info.type.value in ["group", "supergroup"]:
        group_title = chat_info.title
        group_id = chat_info.id
        
        response_text += (
            f"\n🏢 Current Group Info:\n"
            f"📁 Group Name: {group_title}\n"
            f"📁 Group ID: {group_id}\n"
        )

    if not response_text or (not forward_info and not forward_from and not forward_sender_name and not message.reply_to_message):
        first_name = target_user.first_name or "None"
        last_name = target_user.last_name or ""
        username = f"@{target_user.username}" if target_user.username else "No Username"
        user_id = target_user.id
        dc_id = getattr(target_user, "dc_id", "Unknown")

        response_text = (
            f"📁 First Name: {first_name} {last_name}\n"
            f"📁 Last Name: {last_name}\n"
            f"📁 Username: {username}\n"
            f"📁 Telegram ID: {user_id}\n"
            f"📁 Data Centre: {dc_id}"
        )
        if chat_info.type.value in ["group", "supergroup"]:
            response_text += f"\n📁 Group ID: {chat_info.id}"

    await message.reply_text(response_text, quote=True)

@app.on_message(filters.command("ban") & (filters.private | filters.chat(ALLOWED_GROUP_ID)))
async def ban_command_handler(client: Client, message: Message):
    await send_random_reaction(client, message)
    if message.from_user.id != ADMIN_ID:
        await message.reply_text("❌ You are not authorized to use this command!")
        return

    if len(message.command) < 2 and not message.reply_to_message:
        await message.reply_text("Give me a user id / username")
        return

    try:
        if message.reply_to_message and message.reply_to_message.from_user:
            b_id = message.reply_to_message.from_user.id
        else:
            query = message.command[1]
            if query.isdigit():
                b_id = int(query)
            else:
                user_obj = await client.get_users(query)
                b_id = user_obj.id

        BANNED_USERS.add(b_id)
        await message.reply_text(f"✅ Successfully banned user <code>{b_id}</code>.")
    except Exception as e:
        await message.reply_text(f"❌ Failed to ban user! Error: `{str(e)}`")

@app.on_message(filters.command("unban") & (filters.private | filters.chat(ALLOWED_GROUP_ID)))
async def unban_command_handler(client: Client, message: Message):
    await send_random_reaction(client, message)
    if message.from_user.id != ADMIN_ID:
        await message.reply_text("❌ You are not authorized to use this command!")
        return

    if len(message.command) < 2 and not message.reply_to_message:
        await message.reply_text("Give me a user id / username")
        return

    try:
        if message.reply_to_message and message.reply_to_message.from_user:
            u_id = message.reply_to_message.from_user.id
        else:
            query = message.command[1]
            if query.isdigit():
                u_id = int(query)
            else:
                user_obj = await client.get_users(query)
                u_id = user_obj.id

        if u_id in BANNED_USERS:
            BANNED_USERS.remove(u_id)
            await message.reply_text(f"✅ Successfully unbanned user <code>{u_id}</code>.")
        else:
            await message.reply_text("⚠️ This user is not in the banned list.")
    except Exception as e:
        await message.reply_text(f"❌ Failed to unban user! Error: `{str(e)}`")

@app.on_message(filters.command("broadcast") & (filters.private | filters.chat(ALLOWED_GROUP_ID)))
async def broadcast_command_handler(client: Client, message: Message):
    await send_random_reaction(client, message)
    if message.from_user.id != ADMIN_ID:
        await message.reply_text("❌ You are not authorized to use this command!")
        return

    if not message.reply_to_message:
        await message.reply_text("❌ Please reply to a message to broadcast!")
        return

    if len(message.command) > 1 and message.command[1].isdigit():
        target_user_id = int(message.command[1])
        status_msg = await message.reply_text(f"📢 Sending message to user <code>{target_user_id}</code>...")
        try:
            await message.reply_to_message.copy(chat_id=target_user_id)
            await status_msg.edit_text(f"✅ Message successfully sent to user <code>{target_user_id}</code>!")
        except Exception as e:
            await status_msg.edit_text(f"❌ Failed to send message to user <code>{target_user_id}</code>!\nError: `{str(e)}`")
        return

    status_msg = await message.reply_text("📢 Broadcast started...")
    await status_msg.edit_text("✅ Broadcast completed successfully!")

@app.on_message(filters.command("add_redeem") & filters.user(ADMINS))
async def add_redeem_code(client, message):
    await send_random_reaction(client, message)
    if len(message.command) == 3:
        try:
            time_val = message.command[1]
            num_codes = int(message.command[2])
        except ValueError:
            await message.reply_text("Please provide a valid number of codes to generate.")
            return

        codes = []
        for _ in range(num_codes):
            code = generate_code()
            REDEEM_CODE[code] = time_val
            codes.append(code)

        codes_text = '\n'.join(f"➔ <code>/redeem {code}</code>" for code in codes)
        text = f"""
<b>🎉 <u>Giftcode Generated ✅</u></b>

<b> <u>Total Code:</u></b> {num_codes}

{codes_text}

<b>⏳ <u>Duration:</u></b> {time_val}

🌟<u><b>Redeem Code Instruction</b></u>🌟

<b> <u>Click on the code above</u> to copy it instantly!</b>
<b> <u>Send the copied code to the bot</u>\n to unlock your premium features!</b>

<b>🚀 Enjoy your premium access! 🔥</b>
"""
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔑 Redeem Now 🔥", url=f"https://t.me/{temp.U_NAME}")]])
        await message.reply_text(text, reply_markup=keyboard)
    else:
        await message.reply_text("<b>♻ Usage:\n\n➩ <code>/add_redeem 1min 1</code>,\n➩ <code>/add_redeem 1hour 10</code>,\n➩ <code>/add_redeem 1day 5</code></b>")

@app.on_message(filters.command("redeem") & (filters.private | filters.chat(ALLOWED_GROUP_ID)))
async def redeem_code(client, message):
    await send_random_reaction(client, message)
    user_id = message.from_user.id
    if len(message.command) == 2:
        r_code = message.command[1]

        if r_code in REDEEM_CODE:
            try:
                time_val = REDEEM_CODE.pop(r_code)
                user = await client.get_users(user_id)
                try:
                    seconds = await get_seconds(time_val)
                except Exception:
                    await message.reply_text("Invalid time format in redeem code.")
                    return
                if seconds > 0:
                    data = await db.get_user(user_id)
                    current_expiry = data.get("expiry_time") if data else None
                    now_aware = datetime.now(pytz.utc)

                    if current_expiry:
                        current_expiry = current_expiry.replace(tzinfo=pytz.utc)
                    if current_expiry and current_expiry > now_aware:
                        expiry_str_in_ist = current_expiry.astimezone(pytz.timezone("Asia/Kolkata")).strftime("%d-%m-%Y\n⏱️ Expiry Time: %I:%M:%S %p")
                        await message.reply_text(
                            f"🚫 <b>You already have active premium access!</b>\n\n"
                            f"⏳ <b>Current Premium Expiry:</b> {expiry_str_in_ist}\n\n"
                            f"<i>You cannot redeem another code until your current premium access expires.</i>\n\n"
                            f"<b>Thank you for using our service! 🔥</b>",
                            disable_web_page_preview=True
                        )
                        return
                    expiry_time = now_aware + timedelta(seconds=seconds)
                    user_data = {"id": user_id, "expiry_time": expiry_time}
                    await db.update_user(user_data)

                    PREMIUM_USERS[user_id] = time.time() + seconds

                    expiry_str_in_ist = expiry_time.astimezone(pytz.timezone("Asia/Kolkata")).strftime("%d-%m-%Y\n⏱️ Expiry Time: %I:%M:%S %p")
                    await message.reply_text(
                        f"🎉 <b>Premium activated successfully! 🚀</b>\n\n"
                        f"👤 <b>User:</b> {user.mention}\n"
                        f"⚡ <b>User ID:</b> <code>{user_id}</code>\n"
                        f"⏳ <b>Premium Access Duration:</b> <code>{time_val}</code>\n"
                        f"⌛️ <b>Expiry Date:</b> {expiry_str_in_ist}",
                        disable_web_page_preview=True
                    )
                    log_message = f"""
#Redeem_Premium 🔓

👤 <b>User:</b> {user.mention}
⚡ <b>User ID:</b> <code>{user_id}</code>
⏳ <b>Premium Access Duration:</b> <code>{time_val}</code>
⌛️ <b>Expiry Date:</b> {expiry_str_in_ist}

🎉 Premium activated successfully! 🚀
"""
                    await client.send_message(PREMIUM_LOGS, text=log_message, disable_web_page_preview=True)
                else:
                    await message.reply_text("Invalid time format in redeem code.")
            except Exception as e:
                await message.reply_text(f"An error occurred while redeeming the code: {e}")
        else:
            await message.reply_text("Invalid Redeem Code or Expired.")
    else:
        await message.reply_text("Usage: /redeem <code>")

@app.on_message(filters.command("addpremium") & (filters.private | filters.chat(ALLOWED_GROUP_ID)))
async def add_premium_handler(client: Client, message: Message):
    await send_random_reaction(client, message)
    if message.from_user.id != ADMIN_ID:
        await message.reply_text("❌ You are not authorized to use this command!")
        return

    if len(message.command) < 3:
        await message.reply_text("❌ Usage: `/addpremium <user_id> <days>`")
        return

    try:
        target_user_id = int(message.command[1])
        days = int(message.command[2])
        expiry_time = time.time() + (days * 24 * 60 * 60)
        PREMIUM_USERS[target_user_id] = expiry_time
        await message.reply_text(f"✅ Successfully added user `{target_user_id}` to Premium for `{days}` days!")
    except Exception as e:
        await message.reply_text(f"❌ Failed to add premium! Error: `{str(e)}`")

@app.on_message(filters.command("removepremium") & (filters.private | filters.chat(ALLOWED_GROUP_ID)))
async def remove_premium_handler(client: Client, message: Message):
    await send_random_reaction(client, message)
    if message.from_user.id != ADMIN_ID:
        await message.reply_text("❌ You are not authorized to use this command!")
        return

    if len(message.command) < 2:
        await message.reply_text("❌ Usage: `/removepremium <user_id>`")
        return

    try:
        target_user_id = int(message.command[1])
        if target_user_id in PREMIUM_USERS:
            del PREMIUM_USERS[target_user_id]
            await message.reply_text(f"✅ Successfully removed user `{target_user_id}` from Premium!")
        else:
            await message.reply_text("⚠️ This user is not in the premium list.")
    except Exception as e:
        await message.reply_text(f"❌ Failed to remove premium! Error: `{str(e)}`")

@app.on_message((filters.command("plan") | filters.command("plans")) & (filters.private | filters.chat(ALLOWED_GROUP_ID)))
async def plan_command_handler(client: Client, message: Message):
    await send_random_reaction(client, message)
    user_id = message.from_user.id
    if user_id in BANNED_USERS:
        return
    if not await check_fsub(client, user_id):
        await message.reply_text(
            "⚠️ **Force Subscription Required!**\n\n"
            "You must join our update channels below to view plans.",
            reply_markup=await not_joined_keyboard()
        )
        return

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("👤 Contact Admin", url=f"https://t.me/{OWNER_USERNAME}")]
    ])
    try:
        await message.reply_photo(
            photo=PAYMENT_QR,
            caption=PAYMENT_TEXT,
            reply_markup=keyboard
        )
    except Exception:
        await message.reply_text(
            PAYMENT_TEXT,
            reply_markup=keyboard
        )

@app.on_message(filters.command("myplan") & (filters.private | filters.chat(ALLOWED_GROUP_ID)))
async def myplan_command_handler(client: Client, message: Message):
    await send_random_reaction(client, message)
    user_id = message.from_user.id
    if user_id in BANNED_USERS:
        return
    if not await check_fsub(client, user_id):
        await message.reply_text(
            "⚠️ **Force Subscription Required!**\n\n"
            "You must join our update channels below to check your plan.",
            reply_markup=await not_joined_keyboard()
        )
        return

    user_name = message.from_user.first_name

    if is_premium(user_id):
        if user_id == ADMIN_ID:
            status_text = "👑 **Status:** Admin / Lifetime Premium ♾️"
        else:
            expiry_timestamp = PREMIUM_USERS.get(user_id, time.time())
            expiry_date = datetime.fromtimestamp(expiry_timestamp).strftime('%Y-%m-%d %H:%M:%S')
            status_text = f"🌟 **Status:** Active Premium User ✨\n⏳ **Expires On:** `{expiry_date}`"
    else:
        status_text = "📦 **Status:** Free User / Standard Plan\n\n💡 *Upgrade to Premium to get unlimited downloads and ad-free experience! Use /plan to check details.*"

    await message.reply_text(
        f"👤 **User Account Plan Info:**\n\n"
        f"<b>Name:</b> {user_name}\n"
        f"<b>User ID:</b> <code>{user_id}</code>\n\n"
        f"{status_text}"
    )

@app.on_message(filters.command("start") & filters.private)
async def start_handler(client: Client, message: Message):
    await send_random_reaction(client, message)
    user = message.from_user
    user_id = user.id if user else 0

    if user_id in BANNED_USERS:
        return

    if len(message.command) > 1 and message.command[1].startswith("verify_"):
        try:
            target_id = int(message.command[1].split("_")[1])
            if user_id == target_id:
                VERIFIED_USERS[user_id] = time.time() + 43200
                await message.reply_text(
                    "🎉 **Verification Successful!** ✅\n\n"
                    "Your token has been successfully verified. You can now use all download features for the next 12 hours! 🚀"
                )
                return
        except Exception as e:
            logging.error(f"Verification error: {e}")

    if not await check_fsub(client, user_id):
        await message.reply_text(
            "⚠️ **Force Subscription Required!**\n\n"
            "You must join our update channels below to use this bot.\n\n"
            "👉 **Join Update Channel 1 & 2, then click Try Again!**",
            reply_markup=await not_joined_keyboard()
        )
        return

    user_name = user.first_name if user else "Unknown"
    welcome_text = (
        f"🌟 **Welcome to Advanced Bot, {user_name}!** 🚀\n\n"
        f"I can help you download videos and audio from Instagram, YouTube, Gofile, M3U8, MP4, MP3, and more.\n\n"
        f"🛠️ **Key Features:**\n"
        f" • Use `-t` to set custom thumbnails.\n"
        f" • Use `/usetting` to configure settings.\n"
        f" • Premium users get unlimited concurrent tasks!\n\n"
        f"For any assistance or support, feel free to contact the admin below. 👇"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("👤 Contact Admin", url=f"https://t.me/{OWNER_USERNAME}")]
    ])
    try:
        await message.reply_photo(photo=START_IMAGE_URL, caption=welcome_text, reply_markup=keyboard)
    except Exception:
        await message.reply_text(welcome_text, reply_markup=keyboard)

@app.on_message(filters.command("help") & (filters.private | filters.chat(ALLOWED_GROUP_ID)))
async def help_handler(client: Client, message: Message):
    await send_random_reaction(client, message)
    user_id = message.from_user.id
    if user_id in BANNED_USERS:
        return
    if not await check_fsub(client, user_id):
        await message.reply_text(
            "⚠️ **Force Subscription Required!**\n\n"
            "You must join our update channels below to access help.",
            reply_markup=await not_joined_keyboard()
        )
        return

    help_text = (
        "🆘 **Need Help & Support?** 🛠️\n\n"
        "Dear user, if you are facing any issues with downloads or have any questions regarding the bot's functionality, we are here to help you!\n\n"
        "You can directly contact our admin for support using the button below. 👇"
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("👤 Contact Admin", url=f"https://t.me/{OWNER_USERNAME}")]
    ])

    await message.reply_text(
        help_text,
        reply_markup=keyboard
    )

@app.on_message(filters.command("usetting") & (filters.private | filters.chat(ALLOWED_GROUP_ID)))
async def usetting_handler(client: Client, message: Message):
    await send_random_reaction(client, message)
    user_id = message.from_user.id
    if user_id in BANNED_USERS:
        return
    if not await check_fsub(client, user_id):
        await message.reply_text(
            "⚠️ **Force Subscription Required!**\n\n"
            "You must join our update channels below to use settings.",
            reply_markup=await not_joined_keyboard()
        )
        return

    has_thumb = "Yes 🖼️" if user_id in USER_THUMBNAILS and USER_THUMBNAILS[user_id] else "No ❌"
    current_mode = USER_FILE_MODES.get(user_id, "video")
    mode_text = "📹 Video Format" if current_mode == "video" else "📁 Document Format"
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"Thumbnail Set: {has_thumb}", callback_data="set_thumb")],
        [InlineKeyboardButton(f"Mode: {mode_text}", callback_data="toggle_mode")],
        [InlineKeyboardButton("👁️ View Thumbnail", callback_data="view_thumb")],
        [InlineKeyboardButton("🗑️ Remove Thumbnail", callback_data="remove_thumb")]
    ])
    
    await message.reply_text(
        "⚙️ **User Personal Settings**\n\n"
        "Configure your personal thumbnail, view it, or change upload format here:",
        reply_markup=keyboard
    )

@app.on_callback_query()
async def callback_handler(client: Client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    if user_id in BANNED_USERS:
        await callback_query.answer("You are banned from using this bot!", show_alert=True)
        return
    data = callback_query.data
    
    if data == "check_fsub":
        if await check_fsub(client, user_id):
            await callback_query.message.edit_text("✅ Thank you for joining our update channels! You can now use the bot freely. Send /start or your command again.")
        else:
            await callback_query.answer("❌ You have not joined both update channels yet! Please join them first.", show_alert=True)
        return

    if not await check_fsub(client, user_id):
        await callback_query.message.edit_text(
            "⚠️ **Force Subscription Required!**\n\n"
            "You must join our update channels below to proceed.",
            reply_markup=await not_joined_keyboard()
        )
        return

    if data == "set_thumb":
        WAITING_FOR_THUMB.add(user_id)
        await callback_query.message.edit_text(
            "🖼️ Please send your thumbnail photo (Image) here.\n"
            "The bot will automatically save it as your default thumbnail!"
        )
    elif data == "view_thumb":
        if user_id in USER_THUMBNAILS and USER_THUMBNAILS[user_id] and os.path.exists(USER_THUMBNAILS[user_id]):
            await client.send_photo(
                chat_id=callback_query.message.chat.id,
                photo=USER_THUMBNAILS[user_id],
                caption="🖼️ **Your Current Saved Thumbnail:**"
            )
            await callback_query.answer("Here is your thumbnail!")
        else:
            await callback_query.answer("❌ You haven't set any custom thumbnail yet!", show_alert=True)

    elif data == "remove_thumb":
        if user_id in USER_THUMBNAILS:
            if USER_THUMBNAILS[user_id] and os.path.exists(USER_THUMBNAILS[user_id]):
                try:
                    os.remove(USER_THUMBNAILS[user_id])
                except:
                    pass
            del USER_THUMBNAILS[user_id]
        if user_id in WAITING_FOR_THUMB:
            WAITING_FOR_THUMB.remove(user_id)
            
        await callback_query.message.edit_text("🗑️ Your thumbnail has been successfully removed!")
    
    elif data == "toggle_mode":
        current_mode = USER_FILE_MODES.get(user_id, "video")
        new_mode = "document" if current_mode == "video" else "video"
        USER_FILE_MODES[user_id] = new_mode
        mode_text = "📹 Video Format" if new_mode == "video" else "📁 Document Format"
        
        has_thumb = "Yes 🖼️" if user_id in USER_THUMBNAILS and USER_THUMBNAILS[user_id] else "No ❌"
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"Thumbnail Set: {has_thumb}", callback_data="set_thumb")],
            [InlineKeyboardButton(f"Mode: {mode_text}", callback_data="toggle_mode")],
            [InlineKeyboardButton("👁️ View Thumbnail", callback_data="view_thumb")],
            [InlineKeyboardButton("🗑️ Remove Thumbnail", callback_data="remove_thumb")]
        ])
        await callback_query.message.edit_reply_markup(reply_markup=keyboard)
        await callback_query.answer(f"Changed upload mode to {new_mode}!")

    elif data.startswith("cancel_dl_"):
        parts = data.split("_")
        task_user_id = int(parts[2])
        if user_id == task_user_id or user_id == ADMIN_ID:
            CANCEL_REQUESTS.add(task_user_id)
            await callback_query.answer("⚠️ Task Cancel requested... Please wait.", show_alert=True)
        else:
            await callback_query.answer("❌ You are not authorized to cancel this task!", show_alert=True)

    elif data == "start_rename":
        USER_STATES[user_id] = "waiting_for_name"
        RENAME_DATA[user_id] = {"original_msg": callback_query.message.reply_to_message, "prompt_msg": callback_query.message}
        try:
            await callback_query.message.edit_text(
                "Please send the new name you want to give.\n"
                "Examples: `New_Movie.mp4`, `New_Song.mp3`, `Movie.mkv`"
            )
        except Exception:
            pass
        await callback_query.answer()

    elif data.startswith("rename_mode_"):
        mode = data.split("_")[2]
        data_info = RENAME_DATA.get(user_id)
        if not data_info:
            try:
                await callback_query.message.edit_text("❌ Session expired. Please try again.")
            except Exception:
                pass
            return

        original_msg = data_info.get("original_msg")
        new_name = data_info.get("new_name")

        try:
            await callback_query.message.delete()
        except Exception:
            pass

        cancel_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("✖️ Task Cancel", callback_data=f"cancel_dl_{user_id}")]
        ])
        status_msg = await callback_query.message.reply_text(f"⏳ Processing renamed file as `{mode}`... Please wait.", reply_markup=cancel_keyboard)
        await process_renamed_file(client, status_msg, user_id, callback_query.from_user.first_name, original_msg, new_name, mode)
        
        if user_id in RENAME_DATA:
            del RENAME_DATA[user_id]

    elif data == "ytdl_photo":
        url = USER_YTDL_LINKS.get(user_id)
        if not url:
            await callback_query.answer("Instagram link not found!", show_alert=True)
            return

        await callback_query.answer("Downloading photos...")
        status = await callback_query.message.reply_text(
            "📸 **Instagram Photo Downloading...**\n⏳ Please wait..."
        )

        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                images = await asyncio.to_thread(
                    download_instagram_photos,
                    url,
                    temp_dir
                )

                if not images:
                    await status.edit_text(
                        "❌ No photos found!\n\n"
                        "Check the Instagram link or update yt-dlp."
                    )
                    return

                await status.edit_text(
                    f"✅ Found {len(images)} photo(s)!\n"
                    "📤 Sending to Telegram..."
                )

                for start in range(0, len(images), 10):
                    batch = images[start:start + 10]
                    if len(batch) == 1:
                        sent_msg = await client.send_photo(
                            chat_id=callback_query.message.chat.id,
                            photo=batch[0],
                            caption=f"📸 Instagram Photo{get_branding_footer()}"
                        )
                        try:
                            if sent_msg:
                                await sent_msg.copy(chat_id=DATABASE_CHANNEL_ID)
                        except Exception:
                            pass
                    else:
                        media = [
                            InputMediaPhoto(media=photo, caption=f"📸 Instagram Photo{get_branding_footer()}" if idx == 0 else "")
                            for idx, photo in enumerate(batch)
                        ]
                        sent_msgs = await client.send_media_group(
                            chat_id=callback_query.message.chat.id,
                            media=media
                        )
                        try:
                            for s_m in sent_msgs:
                                await s_m.copy(chat_id=DATABASE_CHANNEL_ID)
                        except Exception:
                            pass

                await status.edit_text("✅ Instagram Photo Download Completed!")

        except Exception as e:
            await status.edit_text(f"❌ Photo Download Failed!\n\n{str(e)[:2500]}")
        return

    elif data.startswith("ytdl_"):
        format_code = data.split("_")[1]
        url = USER_YTDL_LINKS.get(user_id)
        if not url:
            try:
                await callback_query.message.edit_text("❌ Link expired or not found. Please send the link again.")
            except Exception:
                pass
            return

        if not is_verified(user_id):
            keyboard = await verification_keyboard(client, user_id)
            try:
                await callback_query.message.edit_text(
                    "⚠️ **Token Verification Required!**\n\n"
                    "You haven't verified your token for the last 12 hours. Please click the button below to verify and unlock downloads.",
                    reply_markup=keyboard
                )
            except Exception:
                pass
            return

        if not is_premium(user_id):
            active_count = ACTIVE_TASKS.get(user_id, 0)
            if active_count >= USER_TASK_LIMIT:
                try:
                    await callback_query.message.edit_text(
                        f"⚠️ **Limit Exceeded!**\n\n"
                        f"You have `{active_count}` active downloads running. "
                        f"Upgrade to Premium for unlimited downloads!"
                    )
                except Exception:
                    pass
                return

        try:
            await callback_query.message.delete()
        except Exception:
            pass

        cancel_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("✖️ Task Cancel", callback_data=f"cancel_dl_{user_id}")]
        ])
        
        status_msg = await client.send_message(
            chat_id=callback_query.message.chat.id,
            text=f"⏳ Initializing download for `{format_code}`... Please wait.",
            reply_markup=cancel_keyboard
        )

        await process_download(client, status_msg, user_id, callback_query.from_user.first_name, url, None, None, format_code)

@app.on_message(filters.photo & (filters.private | filters.chat(ALLOWED_GROUP_ID)))
async def save_thumbnail(client: Client, message: Message):
    user_id = message.from_user.id
    if user_id in BANNED_USERS:
        return
    if not await check_fsub(client, user_id):
        return

    if user_id in WAITING_FOR_THUMB:
        os.makedirs("downloads", exist_ok=True)
        photo_path = f"thumbnails/{user_id}.jpg"
        await message.download(file_name=photo_path)
        USER_THUMBNAILS[user_id] = photo_path
        WAITING_FOR_THUMB.remove(user_id)
        await message.reply_text("✅ Thumbnail saved successfully!")

@app.on_message(filters.command(["leech", "l"]) & (filters.group | filters.private))
async def leech_command_handler(client: Client, message: Message):
    await send_random_reaction(client, message)
    user_id = message.from_user.id
    if user_id in BANNED_USERS:
        return
    if not await check_fsub(client, user_id):
        await message.reply_text("⚠️ Force subscription required.", reply_markup=await not_joined_keyboard())
        return

    text = message.text.strip()
    command_parts = text.split(maxsplit=1)
    
    if len(command_parts) < 2:
        await message.reply_text(
            "❌ **Please provide a link!**\n\n"
            "**Usage Examples:**\n"
            "• `/leech https://t.me/channel/123`\n"
            "• `/leech <url> -n CustomName.mp4`\n"
            "• `/leech <url> -t <thumb_url_or_telegram_link>`"
        )
        return

    query_content = command_parts[1]

    custom_name = None
    custom_thumb = None

    if "-n " in query_content:
        parts = query_content.split("-n ")
        query_content = parts[0].strip()
        custom_name = parts[1].split("-t ")[0].strip() if "-t " in parts[1] else parts[1].strip()

    if "-t " in query_content:
        parts = query_content.split("-t ")
        query_content = parts[0].strip()
        custom_thumb = parts[1].split("-n ")[0].strip() if "-n " in parts[1] else parts[1].strip()
    elif "-t " in message.text:
        try:
            parts = message.text.split("-t ")
            custom_thumb = parts[1].split("-n ")[0].strip()
        except:
            pass

    if "t.me/" in query_content or "telegram.me/" in query_content:
        cancel_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("✖️ Task Cancel", callback_data=f"cancel_dl_{user_id}")]
        ])
        status_msg = await message.reply_text("⏳ Processing Telegram link...", quote=True, reply_markup=cancel_keyboard)
        await process_telegram_link(client, status_msg, user_id, message.from_user.first_name, query_content, custom_name, custom_thumb)
        return

    url_match = re.search(r'https?://[^\s]+|magnet:\?xt=urn:btih:[a-zA-Z0-9]+', query_content)
    if not url_match:
        await message.reply_text("❌ No valid URL found in your command!")
        return

    url = url_match.group(0)
    USER_YTDL_LINKS[user_id] = url

    if not is_verified(user_id):
        keyboard = await verification_keyboard(client, user_id)
        await message.reply_text(
            "⚠️ **Token Verification Required!**\n\n"
            "You haven't verified your token for the last 12 hours. Please click the button below to verify and unlock downloads.",
            reply_markup=keyboard
        )
        return

    if not is_premium(user_id):
        active_count = ACTIVE_TASKS.get(user_id, 0)
        if active_count >= USER_TASK_LIMIT:
            await message.reply_text(
                f"⚠️ **Limit Exceeded!**\n\n"
                f"You have `{active_count}` active downloads running. "
                f"Upgrade to Premium for unlimited downloads!"
            )
            return

    cancel_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✖️ Task Cancel", callback_data=f"cancel_dl_{user_id}")]
    ])
    status_msg = await message.reply_text("⏳ Initializing Leech download... Please wait.", quote=True, reply_markup=cancel_keyboard)
    await process_download(client, status_msg, user_id, message.from_user.first_name, url, custom_name, custom_thumb, "best")


async def process_telegram_link(client, status_msg, user_id, user_name, link, custom_name, custom_thumb_source):
    ACTIVE_TASKS[user_id] = ACTIVE_TASKS.get(user_id, 0) + 1
    downloaded_file = None
    auto_thumb_path = None
    custom_thumb_path = None

    try:
        parts = link.strip("/").split("/")
        msg_id = int(parts[-1])
        channel_username = parts[-2]

        cancel_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("✖️ Task Cancel", callback_data=f"cancel_dl_{user_id}")]
        ])

        await status_msg.edit_text("📥 Downloading media from Telegram (Full File)...", reply_markup=cancel_keyboard)
        target_msg = await client.get_messages(channel_username, msg_id)

        if not target_msg or not target_msg.media:
            await status_msg.edit_text("❌ No media found in the provided Telegram link!")
            return

        os.makedirs("downloads", exist_ok=True)
        
        start_time = time.time()
        last_update_time = 0

        def progress_callback(current, total):
            nonlocal last_update_time
            if user_id in CANCEL_REQUESTS:
                raise Exception("Task cancelled by user/admin.")

            current_time = time.time()
            if current_time - last_update_time > 3 or current == total:
                last_update_time = current_time
                elapsed_time = current_time - start_time
                percentage = (current / total) * 100 if total > 0 else 0
                bar = get_progress_bar(percentage)
                speed = current / elapsed_time if elapsed_time > 0 else 0
                eta = (total - current) / speed if speed > 0 else 0
                
                prog_str = (
                    f"📥 **Downloading Telegram File · {percentage:.1f}%**\n\n"
                    f"{bar} {percentage:.1f}%\n"
                    f" ┣ 💾 **Size:** {human_bytes(current)} / {human_bytes(total)}\n"
                    f" ┣ ⚡ **Speed:** {human_bytes(speed)}/s\n"
                    f" ┗ ⏱️ **ETA:** {int(eta)}s"
                )
                try:
                    client.loop.create_task(status_msg.edit_text(prog_str, reply_markup=cancel_keyboard))
                except Exception:
                    pass

        downloaded_file = await client.download_media(
            target_msg,
            file_name="downloads/",
            progress=progress_callback
        )

        if user_id in CANCEL_REQUESTS:
            raise Exception("Task cancelled by user/admin.")

        if not downloaded_file or not os.path.exists(downloaded_file):
            raise Exception("Failed to download file from Telegram.")

        original_name = os.path.basename(downloaded_file)
        ext = os.path.splitext(original_name)[1]

        if custom_name:
            file_title = custom_name if custom_name.endswith(ext) else custom_name + ext
            new_file_path = os.path.join("downloads", file_title)
            if downloaded_file != new_file_path:
                if os.path.exists(new_file_path):
                    os.remove(new_file_path)
                os.rename(downloaded_file, new_file_path)
                downloaded_file = new_file_path
        else:
            file_title = original_name

        file_size = os.path.getsize(downloaded_file)

        start_time_up = time.time()
        last_upload_update = 0

        def upload_progress(current, total):
            nonlocal last_upload_update
            if user_id in CANCEL_REQUESTS:
                return

            current_time = time.time()
            if current_time - last_upload_update > 3 or current == total:
                last_upload_update = current_time
                elapsed_time = current_time - start_time_up
                percentage = (current / total) * 100 if total > 0 else 0
                bar = get_progress_bar(percentage)
                speed = current / elapsed_time if elapsed_time > 0 else 0
                eta = (total - current) / speed if speed > 0 else 0
                
                upload_str = (
                    f"📤 **Uploading Telegram File · {percentage:.1f}%**\n"
                    f"🎬 <code>{file_title}</code>\n\n"
                    f"{bar} {percentage:.1f}%\n"
                    f" ┣ 💾 **Size:** {human_bytes(current)} / {human_bytes(total)}\n"
                    f" ┣ ⚡ **Speed:** {human_bytes(speed)}/s\n"
                    f" ┗ ⏱️ **ETA:** {int(eta)}s"
                )
                try:
                    client.loop.create_task(status_msg.edit_text(upload_str, reply_markup=cancel_keyboard))
                except Exception:
                    pass

        quality_str = "HD / Best"
        caption = (
            f"<b>{file_title}</b>\n\n"
            f"🎬 <b>Quality:</b> {quality_str}\n"
            f"📦 <b>Size:</b> {human_bytes(file_size)}\n\n"
            f"👤 <b>Task By:</b> {user_name} (`{user_id}`)\n"
            f"🔗 <b>Link:</b> {link}"
            f"{get_branding_footer()}"
        )

        valid_thumb = None
        if custom_thumb_source:
            custom_thumb_path = await download_thumbnail_from_source(client, custom_thumb_source, user_id)
            if custom_thumb_path and os.path.exists(custom_thumb_path):
                valid_thumb = custom_thumb_path

        if not valid_thumb:
            thumb = USER_THUMBNAILS.get(user_id)
            valid_thumb = thumb if thumb and os.path.exists(thumb) else None

        duration, width, height = 0, 0, 0
        file_ext = os.path.splitext(file_title)[1].lower()

        if file_ext in [".mp4", ".mkv", ".avi", ".mov", ".webm"]:
            duration, width, height = get_video_info(downloaded_file)
            if not valid_thumb:
                auto_thumb_path = generate_thumbnail(downloaded_file, user_id)
                valid_thumb = auto_thumb_path

        file_mode = USER_FILE_MODES.get(user_id, "video")

        if file_mode == "document" or file_ext == ".mp3":
            sent_msg = await client.send_document(
                chat_id=status_msg.chat.id,
                document=downloaded_file,
                caption=caption,
                thumb=valid_thumb,
                progress=upload_progress
            )
        else:
            sent_msg = await client.send_video(
                chat_id=status_msg.chat.id,
                video=downloaded_file,
                caption=caption,
                duration=duration,
                width=width,
                height=height,
                thumb=valid_thumb,
                progress=upload_progress
            )

        try:
            if sent_msg:
                await sent_msg.copy(chat_id=DATABASE_CHANNEL_ID)
        except Exception as db_err:
            logging.error(f"Failed to forward to Database Channel: {db_err}")

        if downloaded_file and os.path.exists(downloaded_file):
            os.remove(downloaded_file)
        if auto_thumb_path and os.path.exists(auto_thumb_path):
            os.remove(auto_thumb_path)
        if custom_thumb_path and os.path.exists(custom_thumb_path):
            os.remove(custom_thumb_path)

        await status_msg.delete()

    except Exception as e:
        await status_msg.edit_text(f"❌ **Telegram Download/Upload Failed!**\n\n**Reason:** `{str(e)}`")
        if downloaded_file and os.path.exists(downloaded_file):
            os.remove(downloaded_file)
        if auto_thumb_path and os.path.exists(auto_thumb_path):
            os.remove(auto_thumb_path)
        if custom_thumb_path and os.path.exists(custom_thumb_path):
            os.remove(custom_thumb_path)
    finally:
        if user_id in CANCEL_REQUESTS:
            CANCEL_REQUESTS.remove(user_id)
        if user_id in ACTIVE_TASKS:
            ACTIVE_TASKS[user_id] -= 1
            if ACTIVE_TASKS[user_id] <= 0:
                del ACTIVE_TASKS[user_id]


# --- YouTube Link Detection & Accurate Quality + Original MB Size ---
@app.on_message(filters.regex(r'https?://[^\s]+|magnet:\?xt=urn:btih:[a-zA-Z0-9]+') & (filters.group | filters.private))
async def auto_media_link(client: Client, message: Message):
    await send_random_reaction(client, message)
    user_id = message.from_user.id

    if user_id in BANNED_USERS:
        return

    if not await check_fsub(client, user_id):
        return

    url = message.text.strip()

    if "t.me/" in url or "telegram.me/" in url:
        return

    USER_YTDL_LINKS[user_id] = url

    if "instagram.com" in url or "instagr.am" in url:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📥 Best (HD)", callback_data="ytdl_best")],
            [InlineKeyboardButton("🎵 MP3 Audio", callback_data="ytdl_mp3")],
            [InlineKeyboardButton("📸 Photo / Image", callback_data="ytdl_photo")]
        ])

        await message.reply_text(
            "📷 **Instagram Link Detected!**\n👇 **Select your option below:**",
            reply_markup=keyboard
        )

    elif "youtube.com" in url or "youtu.be" in url:
        status_msg = await message.reply_text(
            "⏳ **Fetching original video qualities & file sizes... Please wait!**"
        )

        cookie_file_path = get_youtube_cookie_file()

        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'skip_download': True,
                'noplaylist': True,
                'cookiefile': cookie_file_path if os.path.exists(cookie_file_path) else None,
                'nocheckcertificate': True
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    info = ydl.extract_info(url, download=False)
                except Exception:
                    if not ydl_opts.get('cookiefile'):
                        raise
                    fallback_opts = dict(ydl_opts)
                    fallback_opts.pop('cookiefile', None)
                    with yt_dlp.YoutubeDL(fallback_opts) as fallback_ydl:
                        info = fallback_ydl.extract_info(url, download=False)

                formats = info.get('formats', [])
                title = info.get('title', 'YouTube Video')
                thumbnail_url = info.get('thumbnail')

                # Offer only the requested standard resolutions that actually
                # exist in the source. This avoids duplicate/phantom choices.
                resolutions = supported_quality_heights(formats)
                quality_buttons = []

                for res in resolutions:
                    label = (
                        "1440p (2K)" if res == 1440
                        else "2160p (4K)" if res == 2160
                        else f"{res}p"
                    )
                    quality_buttons.append([
                        InlineKeyboardButton(
                            f"📥 {label}",
                            callback_data=f"ytdl_{res}"
                        )
                    ])

                quality_buttons.append([
                    InlineKeyboardButton(
                        "🎵 MP3 Audio",
                        callback_data="ytdl_mp3"
                    )
                ])

                caption_text = (
                    f"🎬 <b>{title}</b>\n\n"
                    "👇 <b>Select your preferred quality:</b>"
                )

                if thumbnail_url:
                    try:
                        await message.reply_photo(
                            photo=thumbnail_url,
                            caption=caption_text,
                            reply_markup=InlineKeyboardMarkup(quality_buttons)
                        )
                        await status_msg.delete()
                        return
                    except Exception:
                        pass

                await status_msg.edit_text(
                    caption_text,
                    reply_markup=InlineKeyboardMarkup(quality_buttons)
                )

        except Exception as e:
            logging.exception("YouTube quality extraction error: %s", e)

            await status_msg.edit_text(
                "❌ Could not fetch available YouTube formats.\n\n"
                f"<b>Reason:</b> <code>{html.escape(str(e)[:500])}</code>",
                parse_mode="html",
            )

    else:
        cancel_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                "✖️ Task Cancel",
                callback_data=f"cancel_dl_{user_id}"
            )]
        ])

        status_msg = await message.reply_text(
            "⏳ Initializing full download from link... Please wait.",
            quote=True,
            reply_markup=cancel_keyboard
        )

        await process_download(
            client,
            status_msg,
            user_id,
            message.from_user.first_name,
            url,
            None,
            None,
            "best"
        )

@app.on_message(filters.command("ytdl") & (filters.group | filters.private))
async def ytdl_command_handler(client: Client, message: Message):
    await send_random_reaction(client, message)
    user_id = message.from_user.id
    if user_id in BANNED_USERS:
        return
    if not await check_fsub(client, user_id):
        await message.reply_text("⚠️ Force subscription required.", reply_markup=await not_joined_keyboard())
        return

    if len(message.command) < 2:
        await message.reply_text("❌ Please provide a link!\nExample: `/ytdl https://youtu.be/xxxx`")
        return

    url = message.command[1]
    USER_YTDL_LINKS[user_id] = url

    fake_msg = await message.reply_text(url)
    await auto_media_link(client, fake_msg)
    try:
        await fake_msg.delete()
    except:
        pass


async def process_download(client, status_msg, user_id, user_name, url, custom_name, custom_thumb_source, quality):
    ACTIVE_TASKS[user_id] = ACTIVE_TASKS.get(user_id, 0) + 1
    
    file_path = None
    auto_thumb_path = None
    custom_thumb_path = None
    yt_thumb_path = None
    downloaded_files = []
    
    try:
        os.makedirs("downloads", exist_ok=True)
        last_update_time = 0

        cancel_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("✖️ Task Cancel", callback_data=f"cancel_dl_{user_id}")]
        ])

        cookie_file_path = get_youtube_cookie_file()

        try:
            with yt_dlp.YoutubeDL({'quiet': True, 'skip_download': True, 'nocheckcertificate': True, 'cookiefile': cookie_file_path}) as ydl_thumb:
                info_thumb = ydl_thumb.extract_info(url, download=False)
                thumbnail_url = info_thumb.get('thumbnail')
                if not thumbnail_url and 'thumbnails' in info_thumb:
                    thumbnails = info_thumb.get('thumbnails', [])
                    if thumbnails:
                        thumbnail_url = thumbnails[-1].get('url')
                
                if thumbnail_url:
                    yt_thumb_path = download_youtube_thumbnail(thumbnail_url, user_id)
        except Exception as thumb_err:
            logging.error(f"Error pre-extracting thumbnail: {thumb_err}")

        def download_progress(d):
            nonlocal last_update_time
            if user_id in CANCEL_REQUESTS:
                raise Exception("Task cancelled by user/admin.")

            if d['status'] == 'downloading':
                current_time = time.time()
                if current_time - last_update_time > 3:
                    last_update_time = current_time
                    filename = d.get('filename', 'Media')
                    downloaded = d.get('downloaded_bytes', 0)
                    total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                    
                    if quality == 'photo':
                        progress_str = f"🖼️ **Downloading photos...**\n\n📁 File: `{os.path.basename(filename)}`"
                    else:
                        if total > 0:
                            percentage = (downloaded / total) * 100
                            progress_str = f"📥 **Downloading...**\n\n" \
                                           f"📁 **File:** `{os.path.basename(filename)}`\n" \
                                           f"📊 **Progress:** `{percentage:.1f}%`\n" \
                                           f"📦 **Size:** `{human_bytes(downloaded)} / {human_bytes(total)}`"
                        else:
                            progress_str = f"📥 **Downloading...**\n\n" \
                                           f"📁 **File:** `{os.path.basename(filename)}`\n" \
                                           f"📦 **Downloaded:** `{human_bytes(downloaded)}`"
                    
                    try:
                        client.loop.create_task(status_msg.edit_text(progress_str, reply_markup=cancel_keyboard))
                    except Exception:
                        pass

        common_ydl_opts = {
            'outtmpl': 'downloads/%(title)s_%(autonumber)s.%(ext)s' if quality == 'photo' else 'downloads/%(title)s.%(ext)s',
            'max_filesize': 2000 * 1024 * 1024,
            'progress_hooks': [download_progress],
            'cookiefile': cookie_file_path,
            'geo_bypass': True,
            'nocheckcertificate': True,
        }

        if quality == 'mp3':
            ydl_opts = {
                **common_ydl_opts,
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }
        elif quality == 'photo':
            ydl_opts = {
                **common_ydl_opts,
                'format': 'best',
                'skip_download': False,
            }
        elif quality == 'best':
            ydl_opts = {
                **common_ydl_opts,
                'format': 'best',
            }
        else:
            res_val = int(quality)
            available_info, effective_check_opts = extract_info_with_cookie_fallback(
                yt_dlp,
                url,
                {**common_ydl_opts, 'skip_download': True},
                download=False,
            )
            if not effective_check_opts.get('cookiefile'):
                common_ydl_opts['cookiefile'] = None
            if not available_info.get('formats') and available_info.get('entries'):
                available_info = next(
                    (entry for entry in available_info['entries'] if entry and entry.get('formats')),
                    available_info,
                )
            fmt_selector = youtube_format_for_height(
                available_info.get('formats', []), res_val,
                can_merge=bool(shutil.which('ffmpeg')),
            )
            ydl_opts = {
                **common_ydl_opts,
                'format': fmt_selector,
                'merge_output_format': 'mp4',
            }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            
            if 'entries' in info_dict:
                entries_list = info_dict['entries']
                total_media_count = len(entries_list)
                if quality == 'photo':
                    try:
                        await status_msg.edit_text(f"🖼️ **Total Photos: {total_media_count}**\n🔄 Downloading and uploading...", reply_markup=cancel_keyboard)
                    except Exception:
                        pass

                for entry in entries_list:
                    if entry:
                        p = ydl.prepare_filename(entry)
                        if os.path.exists(p):
                            downloaded_files.append(p)
                        else:
                            for ext_c in ['.jpg', '.jpeg', '.png', '.webp', '.mp4', '.mkv']:
                                cand = os.path.splitext(p)[0] + ext_c
                                if os.path.exists(cand) and cand not in downloaded_files:
                                    downloaded_files.append(cand)
                                    break
                if not downloaded_files and 'requested_downloads' in info_dict:
                    for rd in info_dict['requested_downloads']:
                        if 'filepath' in rd and os.path.exists(rd['filepath']):
                            downloaded_files.append(rd['filepath'])
            
            if not downloaded_files:
                file_path = ydl.prepare_filename(info_dict)
                if quality == 'mp3':
                    file_path = os.path.splitext(file_path)[0] + ".mp3"
                elif quality == 'photo' and not os.path.exists(file_path):
                    for ext_candidate in ['.jpg', '.jpeg', '.png', '.webp']:
                        candidate = os.path.splitext(file_path)[0] + ext_candidate
                        if os.path.exists(candidate):
                            file_path = candidate
                            break
                if os.path.exists(file_path):
                    downloaded_files.append(file_path)

            original_title = info_dict.get('title', 'Media')

            if not yt_thumb_path:
                thumb_url_fallback = info_dict.get('thumbnail')
                if not thumb_url_fallback and 'thumbnails' in info_dict:
                    thumbs_list = info_dict.get('thumbnails', [])
                    if thumbs_list:
                        thumb_url_fallback = thumbs_list[-1].get('url')
                if thumb_url_fallback:
                    yt_thumb_path = download_youtube_thumbnail(thumb_url_fallback, user_id)

        if user_id in CANCEL_REQUESTS:
            raise Exception("Task cancelled by user/admin.")

        if not downloaded_files:
            raise Exception("No media files found to download!")

        start_time = time.time()
        last_upload_update = 0

        if quality == 'mp3':
            display_quality = "MP3 Audio"
        elif quality == 'photo':
            display_quality = "Photo / Image"
        elif quality == 'best':
            display_quality = "Best (HD)"
        else:
            quality_info = info_dict
            if info_dict.get('entries'):
                quality_info = next((entry for entry in info_dict['entries'] if entry), info_dict)
            actual_height = selected_video_height(quality_info)
            display_quality = f"{actual_height}p" if actual_height else f"Up to {quality}p"

        file_path_for_size = downloaded_files[0]
        actual_file_size = os.path.getsize(file_path_for_size) if os.path.exists(file_path_for_size) else 0

        caption = (
            f"<b>{original_title}</b>\n\n"
            f"🎬 <b>Quality:</b> {display_quality}\n"
            f"📦 <b>Size:</b> {human_bytes(actual_file_size)}\n\n"
            f"👤 <b>Task By:</b> {user_name} (`{user_id}`)\n"
            f"🔗 <b>Link:</b> {url}"
            f"{get_branding_footer()}"
        )

        file_ext = os.path.splitext(downloaded_files[0])[1].lower()

        if quality == 'photo' or file_ext in ['.jpg', '.jpeg', '.png', '.webp']:
            if len(downloaded_files) > 1:
                media_group = []
                for i, f_p in enumerate(downloaded_files[:10]):
                    media_group.append(InputMediaPhoto(media=f_p, caption=caption if i == 0 else ""))
                sent_msgs = await client.send_media_group(
                    chat_id=status_msg.chat.id,
                    media=media_group,
                    reply_to_message_id=status_msg.reply_to_message_id
                )
                try:
                    for s_m in sent_msgs:
                        await s_m.copy(chat_id=DATABASE_CHANNEL_ID)
                except Exception:
                    pass
            else:
                sent_msg = await client.send_photo(
                    chat_id=status_msg.chat.id,
                    photo=downloaded_files[0],
                    caption=caption,
                    reply_to_message_id=status_msg.reply_to_message_id
                )
                try:
                    if sent_msg:
                        await sent_msg.copy(chat_id=DATABASE_CHANNEL_ID)
                except Exception:
                    pass
        else:
            file_path = downloaded_files[0]
            file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
            
            def upload_progress(current, total):
                nonlocal last_upload_update
                if user_id in CANCEL_REQUESTS:
                    return

                current_time = time.time()
                if current_time - last_upload_update > 3 or current == total:
                    last_upload_update = current_time
                    elapsed_time = time.time() - start_time
                    
                    percentage = (current / total) * 100 if total > 0 else 0
                    bar = get_progress_bar(percentage)
                    
                    speed = current / elapsed_time if elapsed_time > 0 else 0
                    eta = (total - current) / speed if speed > 0 else 0
                    
                    upload_str = (
                        f"📤 **Uploading · {percentage:.1f}%**\n"
                        f"🎬 <code>{os.path.basename(file_path)}</code>\n\n"
                        f"{bar} {percentage:.1f}%\n"
                        f" ┣ 💾 **Size:** {human_bytes(current)} / {human_bytes(total)}\n"
                        f" ┣ ⚡ **Speed:** {human_bytes(speed)}/s\n"
                        f" ┗ ⏱️ **ETA:** {int(eta)}s"
                    )
                    try:
                        client.loop.create_task(
                            status_msg.edit_text(
                                upload_str,
                                reply_markup=InlineKeyboardMarkup([
                                    [InlineKeyboardButton("✖️ Task Cancel", callback_data=f"cancel_dl_{user_id}")]
                                ])
                            )
                        )
                    except Exception:
                        pass

            valid_thumb = None
            if custom_thumb_source:
                custom_thumb_path = await download_thumbnail_from_source(client, custom_thumb_source, user_id)
                if custom_thumb_path and os.path.exists(custom_thumb_path):
                    valid_thumb = custom_thumb_path

            if not valid_thumb:
                thumb = USER_THUMBNAILS.get(user_id)
                if thumb and os.path.exists(thumb):
                    valid_thumb = thumb

            if not valid_thumb and yt_thumb_path and os.path.exists(yt_thumb_path):
                valid_thumb = yt_thumb_path

            if not valid_thumb and quality != 'mp3' and file_path:
                auto_thumb_path = generate_thumbnail(file_path, user_id)
                if auto_thumb_path and os.path.exists(auto_thumb_path):
                    valid_thumb = auto_thumb_path

            duration, width, height = 0, 0, 0
            if quality != 'mp3' and file_path and os.path.exists(file_path):
                duration, width, height = get_video_info(file_path)

            if quality == 'mp3' or USER_FILE_MODES.get(user_id, "video") == "document":
                sent_msg = await client.send_document(
                    chat_id=status_msg.chat.id,
                    document=file_path,
                    caption=caption,
                    thumb=valid_thumb,
                    progress=upload_progress,
                    reply_to_message_id=status_msg.reply_to_message_id
                )
            else:
                sent_msg = await client.send_video(
                    chat_id=status_msg.chat.id,
                    video=file_path,
                    caption=caption,
                    duration=duration,
                    width=width,
                    height=height,
                    thumb=valid_thumb,
                    progress=upload_progress,
                    reply_to_message_id=status_msg.reply_to_message_id
                )

            try:
                if sent_msg:
                    await sent_msg.copy(chat_id=DATABASE_CHANNEL_ID)
            except Exception as db_err:
                logging.error(f"Failed to forward to Database Channel: {db_err}")

        for f_p in downloaded_files:
            if os.path.exists(f_p):
                os.remove(f_p)
        if auto_thumb_path and os.path.exists(auto_thumb_path):
            os.remove(auto_thumb_path)
        if custom_thumb_path and os.path.exists(custom_thumb_path):
            os.remove(custom_thumb_path)
        if yt_thumb_path and os.path.exists(yt_thumb_path):
            os.remove(yt_thumb_path)
            
        await status_msg.delete()

    except Exception as e:
        error_msg = (
            f"⚠️ <b>Download Failed / Error Occurred!</b>\n\n"
            f"<b>User:</b> {user_name} (`{user_id}`)\n"
            f"<b>URL:</b> `{url}`\n"
            f"<b>Error Details:</b> `{str(e)}`"
        )
        try:
            await client.send_message(chat_id=LOG_CHANNEL_ID, text=error_msg)
        except Exception:
            pass
        
        try:
            await status_msg.edit_text(f"❌ **Task Cancelled / Failed!**\n\n**Reason:** `{str(e)}`")
        except Exception:
            pass

        for f_p in downloaded_files:
            if os.path.exists(f_p):
                os.remove(f_p)
        if auto_thumb_path and os.path.exists(auto_thumb_path):
            os.remove(auto_thumb_path)
        if custom_thumb_path and os.path.exists(custom_thumb_path):
            os.remove(custom_thumb_path)
        if yt_thumb_path and os.path.exists(yt_thumb_path):
            os.remove(yt_thumb_path)
            
    finally:
        if user_id in CANCEL_REQUESTS:
            CANCEL_REQUESTS.remove(user_id)
        if user_id in ACTIVE_TASKS:
            ACTIVE_TASKS[user_id] -= 1
            if ACTIVE_TASKS[user_id] <= 0:
                del ACTIVE_TASKS[user_id]

@app.on_message((filters.document | filters.video) & (filters.chat(ALLOWED_GROUP_ID) | filters.private))
async def send_rename_button(client, message):
    if message.from_user.id in BANNED_USERS:
        return
    if not await check_fsub(client, message.from_user.id):
        return
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✏️ File Renaming", callback_data="start_rename")]
    ])
    await message.reply_text("Click the button below if you want to rename this file:", reply_markup=keyboard)

@app.on_message(filters.text & (filters.chat(ALLOWED_GROUP_ID) | filters.private) & ~filters.command("/"))
async def handle_new_name(client, message: Message):
    user_id = message.from_user.id
    if user_id in BANNED_USERS:
        return
    
    if USER_STATES.get(user_id) == "waiting_for_name":
        new_name = message.text.strip()
        USER_STATES[user_id] = None
        
        data_info = RENAME_DATA.get(user_id)
        
        try:
            await message.delete()
        except Exception as e:
            logging.error(f"Error deleting user input message: {e}")

        if data_info and data_info.get("prompt_msg"):
            try:
                await data_info.get("prompt_msg").delete()
            except Exception as e:
                logging.error(f"Error deleting prompt message: {e}")
            
        if not data_info:
            await message.reply_text("❌ Session expired. Please try again.")
            return

        RENAME_DATA[user_id]["new_name"] = new_name
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("📹 Video Format", callback_data="rename_mode_video"),
                InlineKeyboardButton("📁 Document Format", callback_data="rename_mode_document")
            ]
        ])
        
        await message.reply_text(
            f"✨ **New Name set to:** `{new_name}`\n\n"
            f"👇 **Choose upload format:**",
            reply_markup=keyboard
        )

async def process_renamed_file(client, status_msg, user_id, user_name, original_msg, new_name, mode):
    if not original_msg or not original_msg.media:
        await status_msg.edit_text("❌ Original media message not found or invalid!")
        return

    downloaded_file = None
    auto_thumb_path = None
    try:
        os.makedirs("downloads", exist_ok=True)
        
        cancel_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("✖️ Task Cancel", callback_data=f"cancel_dl_{user_id}")]
        ])
        await status_msg.edit_text("📥 Downloading file for renaming (Full File)...", reply_markup=cancel_keyboard)
        
        downloaded_file = await client.download_media(
            original_msg,
            file_name="downloads/"
        )

        if user_id in CANCEL_REQUESTS:
            raise Exception("Task cancelled by user/admin.")

        if not downloaded_file or not os.path.exists(downloaded_file):
            raise Exception("Failed to download file.")

        ext = os.path.splitext(new_name)[1]
        if not ext:
            old_ext = os.path.splitext(downloaded_file)[1]
            file_title = new_name + old_ext
        else:
            file_title = new_name

        new_file_path = os.path.join("downloads", file_title)
        if downloaded_file != new_file_path:
            if os.path.exists(new_file_path):
                os.remove(new_file_path)
            os.rename(downloaded_file, new_file_path)
            downloaded_file = new_file_path
            
        file_size = os.path.getsize(downloaded_file)

        start_time = time.time()
        last_upload_update = 0

        def upload_progress(current, total):
            nonlocal last_upload_update
            if user_id in CANCEL_REQUESTS:
                return

            current_time = time.time()
            if current_time - last_upload_update > 3 or current == total:
                last_upload_update = current_time
                elapsed_time = time.time() - start_time
                percentage = (current / total) * 100 if total > 0 else 0
                bar = get_progress_bar(percentage)
                speed = current / elapsed_time if elapsed_time > 0 else 0
                eta = (total - current) / speed if speed > 0 else 0
                
                upload_str = (
                    f"📤 **Uploading Renamed File · {percentage:.1f}%**\n"
                    f"🎬 <code>{file_title}</code>\n\n"
                    f"{bar} {percentage:.1f}%\n"
                    f" ┣ 💾 **Size:** {human_bytes(current)} / {human_bytes(total)}\n"
                    f" ┣ ⚡ **Speed:** {human_bytes(speed)}/s\n"
                    f" ┗ ⏱️ **ETA:** {int(eta)}s"
                )
                try:
                    client.loop.create_task(status_msg.edit_text(upload_str, reply_markup=cancel_keyboard))
                except Exception:
                    pass

        caption = (
            f"<b>{file_title}</b>\n\n"
            f"📦 <b>Size:</b> {human_bytes(file_size)}\n"
            f"👤 <b>Task By:</b> {user_name} (`{user_id}`)"
            f"{get_branding_footer()}"
        )

        thumb = USER_THUMBNAILS.get(user_id)
        valid_thumb = thumb if thumb and os.path.exists(thumb) else None

        duration, width, height = 0, 0, 0
        file_ext = os.path.splitext(file_title)[1].lower()

        if file_ext in [".mp4", ".mkv", ".avi", ".mov", ".webm"]:
            duration, width, height = get_video_info(downloaded_file)
            if not valid_thumb:
                auto_thumb_path = generate_thumbnail(downloaded_file, user_id)
                valid_thumb = auto_thumb_path

        if mode == "document" or file_ext == ".mp3":
            sent_msg = await client.send_document(
                chat_id=status_msg.chat.id,
                document=downloaded_file,
                caption=caption,
                thumb=valid_thumb,
                progress=upload_progress
            )
        else:
            sent_msg = await client.send_video(
                chat_id=status_msg.chat.id,
                video=downloaded_file,
                caption=caption,
                duration=duration,
                width=width,
                height=height,
                thumb=valid_thumb,
                progress=upload_progress
            )

        try:
            if sent_msg:
                await sent_msg.copy(chat_id=DATABASE_CHANNEL_ID)
        except Exception as db_err:
            logging.error(f"Failed to forward to Database Channel: {db_err}")

        if downloaded_file and os.path.exists(downloaded_file):
            os.remove(downloaded_file)
        if auto_thumb_path and os.path.exists(auto_thumb_path):
            os.remove(auto_thumb_path)

        await status_msg.delete()

    except Exception as e:
        await status_msg.edit_text(f"❌ **Rename & Upload Failed!**\n\n**Reason:** `{str(e)}`")
        if downloaded_file and os.path.exists(downloaded_file):
            os.remove(downloaded_file)
        if auto_thumb_path and os.path.exists(auto_thumb_path):
            os.remove(auto_thumb_path)
    finally:
        if user_id in CANCEL_REQUESTS:
            CANCEL_REQUESTS.remove(user_id)

async def main():
    await start_web_server()
    await app.start()
    
    try:
        startup_msg = "🤖 **Bot Started Successfully! 🚀**"
        await app.send_message(chat_id=LOG_CHANNEL_ID, text=startup_msg)
    except Exception as e:
        logging.error(f"Failed to send startup message to LOG_CHANNEL: {e}")

    print("🤖 Bot Started Successfully...")
    await idle()

if __name__ == "__main__":
    app.run(main())

# Register leech command handlers
register_leech_handlers(app)
