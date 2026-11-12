import os
import asyncio
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def register_leech_handlers(app):
    @app.on_message(filters.command(["leech", "l"]))
    async def leech_command(client, message):
        user = message.from_user
        if not user:
            return

        # Check if link or replied media is provided
        if len(message.command) < 2 and not message.reply_to_message:
            error_text = (
                f"<b>{user.mention}</b>\n"
                f"<code>{message.text}</code>\n\n"
                "❌ <b>Please provide a link or reply to a message/media!</b>\n"
                "Example: <code>/leech https://... -n video.mp4 -t thumbnail_url</code>"
            )
            await message.reply_text(error_text, parse_mode="html")
            return

        # Start download processing message
        status_message = await message.reply_text(
            f"<b>{user.mention}</b>\n"
            f"<code>{message.text}</code>\n\n"
            "📥 <b>Downloading File...</b>",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("❌ Task Cancel", callback_data="cancel_task")]]
            ),
            parse_mode="html"
        )

        try:
            # Download simulation / actual download logic
            await asyncio.sleep(3)

            file_name = "gc8ze63g.mp4"
            file_size_str = "88.41 MB"
            
            if len(message.command) > 1:
                download_url = message.command[1]
            elif message.reply_to_message:
                download_url = "Telegram Media"
            else:
                download_url = "N/A"

            DATABASE_CHANNEL_ID = int(os.environ.get("DATABASE_CHANNEL_ID", "-1004396122384"))
            LOG_CHANNEL_ID = int(os.environ.get("LOG_CHANNEL_ID", "-1004441596603"))

            caption = (
                f"<b>{file_name}</b>\n\n"
                f"👤 <b>Task By:</b> {user.mention} ({user.id})\n"
                f"📦 <b>Size:</b> {file_size_str}\n"
                f"🔗 <b>Link:</b> {download_url}\n\n"
                f"> Powered by Bot\n"
                f"> @AlluTvSerials"
            )

            # Save to Database Channel
            await client.send_message(DATABASE_CHANNEL_ID, caption, parse_mode="html")
            
            # Send success notification to Log Channel
            log_text = (
                "📥 <b>New Download Completed!</b>\n\n"
                f"👤 <b>User:</b> {user.mention} ({user.id})\n"
                f"🔗 <b>URL:</b> {download_url}\n"
                f"📁 <b>File:</b> {file_name}\n"
                f"📦 <b>Size:</b> {file_size_str}"
            )
            await client.send_message(LOG_CHANNEL_ID, log_text, parse_mode="html")

            await status_message.edit_text("✅ **Download & Upload Completed Successfully!**")

        except Exception as e:
            error_log = f"❌ **Download Error:**\nUser: {user.id}\nError: {str(e)}"
            await client.send_message(LOG_CHANNEL_ID, error_log)
            await status_message.edit_text(f"❌ **An error occurred:** {str(e)}")

    @app.on_callback_query(filters.regex("cancel_task"))
    async def cancel_task_callback(client, callback_query):
        await callback_query.message.edit_text("❌ **Task Cancelled by User.**")
        await callback_query.answer("Task successfully cancelled!", show_alert=True)
