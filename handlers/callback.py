from pyrogram import Client
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from config import Config
import logging

logger = logging.getLogger(__name__)

async def handle_callback(client: Client, callback_query: CallbackQuery):
    """Handle all callback queries"""
    data = callback_query.data
    user_id = callback_query.from_user.id
    
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
    
    # Start callback
    elif data == "start":
        is_premium = await client.db.is_premium_user(user_id)
        premium_text = "\n\n👑 **Premium User**" if is_premium else ""
        
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
        
        # Try to edit with photo if start pic exists
        start_pic = await client.db.get_bot_setting("start_pic", "")
        caption = Config.START_MESSAGE + premium_text
        
        if start_pic:
            try:
                # Delete old message and send new with photo
                await callback_query.message.delete()
                await callback_query.message.chat.send_photo(
                    photo=start_pic,
                    caption=caption,
                    reply_markup=InlineKeyboardMarkup(buttons)
                )
                await callback_query.answer()
                return
            except:
                pass
        
        # Fallback to text edit
        await callback_query.message.edit_text(
            caption,
            reply_markup=InlineKeyboardMarkup(buttons),
            disable_web_page_preview=True
        )
    
    # Toggle media type
    elif data == "toggle_media":
        current = await client.db.get_media_type(user_id)
        new_type = "document" if current == "video" else "video"
        await client.db.set_media_type(user_id, new_type)
        
        await callback_query.answer(f"Media type set to: {new_type.title()}", show_alert=True)
        
        # Refresh settings
        await handle_callback(client, CallbackQuery(
            client=client,
            from_user=callback_query.from_user,
            message=callback_query.message,
            data="settings"
        ))
    
    # Toggle spoiler
    elif data == "toggle_spoiler":
        new_state = await client.db.toggle_spoiler(user_id)
        status = "Enabled" if new_state else "Disabled"
        
        await callback_query.answer(f"Spoiler: {status}", show_alert=True)
        
        # Refresh settings
        await handle_callback(client, CallbackQuery(
            client=client,
            from_user=callback_query.from_user,
            message=callback_query.message,
            data="settings"
        ))
    
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
        from pyrogram.errors import UserNotParticipant, ChatAdminRequired
        
        fsub_mode = await client.db.get_bot_setting("fsub_mode", "off")
        if fsub_mode not in ["on", "request"]:
            await callback_query.answer("Force subscribe is disabled", show_alert=True)
            return
        
        channels = await client.db.get_fsub_channels()
        
        if not channels:
            await callback_query.answer("No channels configured", show_alert=True)
            return
        
        not_joined = []
        
        for channel_id in channels:
            try:
                member = await client.get_chat_member(channel_id, user_id)
                # Properly check membership status
                if member.status not in ["member", "administrator", "creator"]:
                    not_joined.append(channel_id)
            except UserNotParticipant:
                not_joined.append(channel_id)
            except ChatAdminRequired:
                logger.error(f"Bot is not admin in channel {channel_id}")
                continue
            except Exception as e:
                logger.error(f"Error checking membership: {e}")
                continue
        
        if not_joined:
            # Still haven't joined all channels
            channel_names = []
            for ch_id in not_joined:
                try:
                    chat = await client.get_chat(ch_id)
                    channel_names.append(chat.title)
                except:
                    channel_names.append(str(ch_id))
            
            await callback_query.answer(
                f"❌ Please join: {', '.join(channel_names[:2])}{'...' if len(channel_names) > 2 else ''}",
                show_alert=True
            )
        else:
            # Successfully joined all channels
            await callback_query.answer("✅ Verification successful!", show_alert=True)
            
            # Show main menu
            is_premium = await client.db.is_premium_user(user_id)
            premium_text = "\n\n👑 **Premium User**" if is_premium else ""
            
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
                Config.START_MESSAGE + premium_text,
                reply_markup=InlineKeyboardMarkup(buttons),
                disable_web_page_preview=True
            )
    
    # Quality selection callbacks
    elif data.startswith("quality_"):
        quality = data.replace("quality_", "")
        await callback_query.answer(f"Encoding to {quality}...", show_alert=False)
        # Trigger encoding with the selected quality
        # This would call the encode function
    
    # Aspect ratio selection
    elif data.startswith("aspect_"):
        aspect = data.replace("aspect_", "")
        await callback_query.answer(f"Cropping to {aspect}...", show_alert=False)
        # Trigger crop with the selected aspect ratio
    
    # Close button
    elif data == "close":
        await callback_query.message.delete()
        await callback_query.answer()
    
    # Save thumbnail from photo
    elif data.startswith("save_thumb_"):
        message_id = int(data.split("_")[2])
        
        # Get the photo message
        try:
            photo_msg = await callback_query.message.chat.get_messages(message_id)
            if photo_msg.photo:
                photo = photo_msg.photo.file_id
                await client.db.set_thumbnail(user_id, photo)
                await callback_query.answer("✅ Thumbnail saved!", show_alert=True)
                await callback_query.message.edit_text("✅ **Thumbnail saved successfully!**")
            else:
                await callback_query.answer("❌ Photo not found!", show_alert=True)
        except Exception as e:
            logger.error(f"Error saving thumbnail: {e}")
            await callback_query.answer("❌ Error saving thumbnail!", show_alert=True)
    
    else:
        await callback_query.answer("Unknown action!", show_alert=True)
