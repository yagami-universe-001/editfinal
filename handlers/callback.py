from pyrogram import Client
from pyrogram.types import CallbackQuery
from config import Config
import logging

logger = logging.getLogger(__name__)

async def handle_callback(client: Client, callback_query: CallbackQuery):
    """Handle all callback queries"""
    
    data = callback_query.data
    user_id = callback_query.from_user.id
    
    try:
        # Help callback
        if data == "help":
            await callback_query.message.edit_text(
                text=Config.HELP_MESSAGE,
                reply_markup=callback_query.message.reply_markup
            )
            await callback_query.answer("📚 Help Menu")
        
        # Settings callback
        elif data == "settings":
            settings_text = """
⚙️ **Bot Settings**

**Available Settings Commands:**

**Thumbnail:**
• `/setthumb` - Set custom thumbnail
• `/getthumb` - View saved thumbnail
• `/delthumb` - Delete thumbnail

**Watermark:**
• `/setwatermark` - Set default watermark
• `/getwatermark` - View watermark
• `/addwatermark` - Add watermark to video

**Upload Options:**
• `/setmedia` - Set media type (video/document)
• `/spoiler` - Toggle spoiler mode
• `/upload` - Set upload destination

**Encoding Settings:**
• `/codec` - Change video codec
• `/preset` - Change encoding preset
• `/crf` - Set quality (CRF value)
• `/audio` - Set audio bitrate

Send a video to start processing!
"""
            await callback_query.message.edit_text(
                text=settings_text,
                reply_markup=callback_query.message.reply_markup
            )
            await callback_query.answer("⚙️ Settings")
        
        # Start/Back callback
        elif data == "start":
            await callback_query.message.edit_text(
                text=Config.START_MESSAGE.format(first_name=callback_query.from_user.first_name),
                reply_markup=callback_query.message.reply_markup
            )
            await callback_query.answer("🏠 Home")
        
        # Close callback
        elif data == "close":
            await callback_query.message.delete()
            await callback_query.answer("✅ Closed")
        
        # Quality selection callbacks (for encoding)
        elif data.startswith("encode_"):
            quality = data.replace("encode_", "")
            await callback_query.answer(f"🎬 Encoding to {quality}...")
            # Import here to avoid circular imports
            from handlers import encode
            # Create a fake message object for encoding
            callback_query.message.command = [quality]
            await encode.encode_video(client, callback_query.message)
        
        # Compress callback
        elif data == "compress":
            await callback_query.answer("🗜️ Compressing...")
            from handlers import encode
            await encode.compress_video(client, callback_query.message)
        
        # Cancel/Stop callbacks
        elif data.startswith("cancel_"):
            task_id = data.replace("cancel_", "")
            from handlers import stop
            # Create a fake message for stop command
            callback_query.message.text = f"/stop{task_id}"
            callback_query.message.command = ["stop", task_id]
            await stop.stop_task(client, callback_query.message)
            await callback_query.answer("⛔ Task cancelled")
        
        # Unknown callback
        else:
            await callback_query.answer("⚠️ Unknown action", show_alert=True)
            logger.warning(f"Unknown callback data: {data}")
    
    except Exception as e:
        logger.error(f"Error handling callback {data}: {e}")
        await callback_query.answer(f"❌ Error: {str(e)}", show_alert=True)
