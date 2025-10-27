from pyrogram import Client
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
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
            buttons = [
                [InlineKeyboardButton("🔙 Back", callback_data="start")]
            ]
            await callback_query.message.edit_text(
                Config.HELP_MESSAGE,
                reply_markup=InlineKeyboardMarkup(buttons),
                disable_web_page_preview=True
            )
            await callback_query.answer()
        
        # Settings callback
        elif data == "settings":
            thumbnail = await client.db.get_thumbnail(user_id)
            watermark = await client.db.get_watermark(user_id)
            media_type = await client.db.get_media_type(user_id)
            spoiler = await client.db.get_spoiler(user_id)
            
            buttons = [
                [
                    InlineKeyboardButton("📸 Thumbnail", callback_data="set_thumb"),
                    InlineKeyboardButton("💧 Watermark", callback_data="set_watermark")
                ],
                [
                    InlineKeyboardButton("📹 Media Type", callback_data="toggle_media"),
                    InlineKeyboardButton("👻 Spoiler", callback_data="toggle_spoiler")
                ],
                [InlineKeyboardButton("🔙 Back", callback_data="start")]
            ]
            
            settings_text = (
                f"⚙️ **Your Settings**\n\n"
                f"**Thumbnail:** {'✅ Set' if thumbnail else '❌ Not set'}\n"
                f"**Watermark:** {watermark if watermark else '❌ Not set'}\n"
                f"**Media Type:** {media_type.title()}\n"
                f"**Spoiler:** {'✅ Enabled' if spoiler else '❌ Disabled'}"
            )
            
            await callback_query.message.edit_text(
                settings_text,
                reply_markup=InlineKeyboardMarkup(buttons)
            )
            await callback_query.answer()
        
        # Start callback
        elif data == "start":
            is_premium = await client.db.is_premium_user(user_id)
            premium_text = "👑 Premium User" if is_premium else ""
            
            buttons = [
                [
                    InlineKeyboardButton("📚 Help", callback_data="help"),
                    InlineKeyboardButton("⚙️ Settings", callback_data="settings")
                ],
                [
                    InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/yourusername"),
                    InlineKeyboardButton("📢 Updates", url="https://t.me/yourchannel")
                ]
            ]
            
            await callback_query.message.edit_text(
                Config.START_MESSAGE + f"\n\n{premium_text}",
                reply_markup=InlineKeyboardMarkup(buttons),
                disable_web_page_preview=True
            )
            await callback_query.answer()
        
        # Toggle media type
        elif data == "toggle_media":
            current = await client.db.get_media_type(user_id)
            new_type = "document" if current == "video" else "video"
            await client.db.set_media_type(user_id, new_type)
            
            await callback_query.answer(f"Media type set to: {new_type.title()}", show_alert=True)
            
            # Refresh settings - pass actual callback_query object
            await handle_callback(client, callback_query._replace(data="settings"))
        
        # Toggle spoiler
        elif data == "toggle_spoiler":
            new_state = await client.db.toggle_spoiler(user_id)
            status = "Enabled" if new_state else "Disabled"
            
            await callback_query.answer(f"Spoiler: {status}", show_alert=True)
            
            # Refresh settings
            await handle_callback(client, callback_query._replace(data="settings"))
        
        # Set thumbnail
        elif data == "set_thumb":
            await callback_query.message.reply_text(
                "📸 **Set Thumbnail**\n\n"
                "Send me a photo to set as thumbnail.\n"
                "The photo will be used for all your encoded videos.\n\n"
                "Use /delthumb to remove thumbnail."
            )
            await callback_query.answer()
        
        # Set watermark
        elif data == "set_watermark":
            await callback_query.message.reply_text(
                "💧 **Set Watermark**\n\n"
                "Use /setwatermark <text> to set watermark text.\n\n"
                "**Example:**\n"
                "`/setwatermark @YourChannel`\n\n"
                "The watermark will appear on all encoded videos."
            )
            await callback_query.answer()
        
        # Check force subscribe
        elif data == "check_fsub":
            fsub_mode = await client.db.get_bot_setting("fsub_mode", "off")
            if fsub_mode not in ["on", "request"]:
                await callback_query.answer("Force subscribe is disabled", show_alert=True)
                return
            
            channels = await client.db.get_fsub_channels()
            not_joined = []
            
            for channel_id in channels:
                try:
                    member = await client.get_chat_member(channel_id, user_id)
                    if member.status not in ["member", "administrator", "creator"]:
                        not_joined.append(channel_id)
                except:
                    pass
            
            if not_joined:
                await callback_query.answer(
                    "❌ You haven't joined all channels yet!",
                    show_alert=True
                )
            else:
                await callback_query.answer("✅ Verification successful!", show_alert=True)
                
                # Show start message
                is_premium = await client.db.is_premium_user(user_id)
                premium_text = "👑 Premium User" if is_premium else ""
                
                buttons = [
                    [
                        InlineKeyboardButton("📚 Help", callback_data="help"),
                        InlineKeyboardButton("⚙️ Settings", callback_data="settings")
                    ],
                    [
                        InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/yourusername"),
                        InlineKeyboardButton("📢 Updates", url="https://t.me/yourchannel")
                    ]
                ]
                
                await callback_query.message.edit_text(
                    Config.START_MESSAGE + f"\n\n{premium_text}",
                    reply_markup=InlineKeyboardMarkup(buttons),
                    disable_web_page_preview=True
                )
        
        # Quality selection callbacks
        elif data.startswith("quality_"):
            quality = data.replace("quality_", "")
            await callback_query.answer(f"Encoding to {quality}...", show_alert=False)
            # Note: Actual encoding needs to be triggered with the video reference
            # This is just acknowledging the button press
        
        # Aspect ratio selection
        elif data.startswith("aspect_"):
            aspect = data.replace("aspect_", "")
            await callback_query.answer(f"Cropping to {aspect}...", show_alert=False)
        
        # Action buttons from media handler
        elif data == "action_trim":
            await callback_query.message.reply_text(
                "✂️ **Trim Video**\n\n"
                "Use: `/cut <start_time> <end_time>`\n\n"
                "Example: `/cut 00:00:10 00:01:30`\n\n"
                "Reply to the video with this command."
            )
            await callback_query.answer()
        
        elif data == "action_crop":
            await callback_query.message.reply_text(
                "📐 **Crop Video**\n\n"
                "Use: `/crop` command\n\n"
                "Reply to the video with this command,\n"
                "then select aspect ratio."
            )
            await callback_query.answer()
        
        elif data == "action_mediainfo":
            await callback_query.message.reply_text(
                "ℹ️ **Get Media Info**\n\n"
                "Use: `/mediainfo` command\n\n"
                "Reply to the video with this command."
            )
            await callback_query.answer()
        
        # Close button
        elif data == "close":
            await callback_query.message.delete()
            await callback_query.answer()
        
        else:
            await callback_query.answer("Unknown action!", show_alert=True)
            logger.warning(f"Unknown callback data: {data}")
    
    except Exception as e:
        logger.error(f"Callback handler error: {e}")
        try:
            await callback_query.answer("An error occurred!", show_alert=True)
        except:
            pass
