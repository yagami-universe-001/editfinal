from pyrogram import Client
from pyrogram.types import Message
import logging
import os

logger = logging.getLogger(__name__)

async def set_thumbnail(client: Client, message: Message):
    """Set custom thumbnail"""
    user_id = message.from_user.id
    
    # Check if user replied with a photo
    if message.reply_to_message and message.reply_to_message.photo:
        # Download and save thumbnail
        photo = message.reply_to_message.photo.file_id
        await client.db.set_thumbnail(user_id, photo)
        await message.reply_text("✅ **Thumbnail saved successfully!**")
    else:
        await message.reply_text(
            "📸 **Set Custom Thumbnail**\n\n"
            "Reply to this message with a photo to set as your default thumbnail.\n\n"
            "The thumbnail will be used for all your encoded videos."
        )

async def get_thumbnail(client: Client, message: Message):
    """Get saved thumbnail"""
    user_id = message.from_user.id
    thumb = await client.db.get_thumbnail(user_id)
    
    if not thumb:
        await message.reply_text(
            "❌ **No thumbnail saved!**\n\n"
            "Use /setthumb to set a custom thumbnail."
        )
        return
    
    try:
        await message.reply_photo(
            photo=thumb,
            caption="📸 **Your Saved Thumbnail**\n\nUse /delthumb to remove it."
        )
    except Exception as e:
        logger.error(f"Error sending thumbnail: {e}")
        await message.reply_text("❌ **Error retrieving thumbnail!**")

async def delete_thumbnail(client: Client, message: Message):
    """Delete saved thumbnail"""
    user_id = message.from_user.id
    
    thumb = await client.db.get_thumbnail(user_id)
    if not thumb:
        await message.reply_text("❌ **No thumbnail to delete!**")
        return
    
    await client.db.delete_thumbnail(user_id)
    await message.reply_text("✅ **Thumbnail deleted successfully!**")

async def set_watermark(client: Client, message: Message):
    """Set watermark text"""
    user_id = message.from_user.id
    
    if len(message.command) < 2:
        current = await client.db.get_watermark(user_id)
        await message.reply_text(
            f"💧 **Watermark Settings**\n\n"
            f"**Current:** {current if current else 'Not set'}\n\n"
            f"**Usage:** `/setwatermark <text>`\n"
            f"**Example:** `/setwatermark @YourChannel`\n\n"
            f"The watermark text will appear on all encoded videos."
        )
        return
    
    # Get watermark text (everything after command)
    watermark = message.text.split(None, 1)[1]
    
    if len(watermark) > 50:
        await message.reply_text("❌ **Watermark text too long!** (Max 50 characters)")
        return
    
    await client.db.set_watermark(user_id, watermark)
    await message.reply_text(
        f"✅ **Watermark set successfully!**\n\n"
        f"**Text:** {watermark}\n\n"
        f"This will appear on all your encoded videos."
    )

async def get_watermark(client: Client, message: Message):
    """Get current watermark"""
    user_id = message.from_user.id
    watermark = await client.db.get_watermark(user_id)
    
    if not watermark:
        await message.reply_text(
            "❌ **No watermark set!**\n\n"
            "Use `/setwatermark <text>` to set a watermark.\n"
            "Example: `/setwatermark @MyChannel`"
        )
        return
    
    await message.reply_text(
        f"💧 **Your Current Watermark**\n\n"
        f"**Text:** {watermark}\n\n"
        f"This appears on all your encoded videos.\n"
        f"Use `/setwatermark <new_text>` to change it."
    )

async def set_media_type(client: Client, message: Message):
    """Set preferred media type"""
    user_id = message.from_user.id
    
    if len(message.command) < 2:
        current = await client.db.get_media_type(user_id)
        await message.reply_text(
            f"📹 **Media Type Settings**\n\n"
            f"**Current:** {current.title()}\n\n"
            f"**Usage:** `/setmedia <type>`\n\n"
            f"**Options:**\n"
            f"• `video` - Upload as video (with player)\n"
            f"• `document` - Upload as document/file\n\n"
            f"**Example:** `/setmedia video`"
        )
        return
    
    media_type = message.command[1].lower()
    
    if media_type not in ["video", "document"]:
        await message.reply_text(
            "❌ **Invalid media type!**\n\n"
            "Choose either:\n"
            "• `video`\n"
            "• `document`"
        )
        return
    
    await client.db.set_media_type(user_id, media_type)
    await message.reply_text(
        f"✅ **Media type set to:** {media_type.title()}\n\n"
        f"All encoded videos will be uploaded as {media_type}."
    )

async def toggle_spoiler(client: Client, message: Message):
    """Toggle spoiler mode"""
    user_id = message.from_user.id
    
    new_state = await client.db.toggle_spoiler(user_id)
    
    status_emoji = "✅" if new_state else "❌"
    status_text = "Enabled" if new_state else "Disabled"
    
    description = (
        "Videos will be sent with spoiler effect (blurred preview)."
        if new_state else
        "Videos will be sent normally without spoiler."
    )
    
    await message.reply_text(
        f"{status_emoji} **Spoiler Mode: {status_text}**\n\n"
        f"{description}\n\n"
        f"Use /spoiler again to toggle."
    )

async def set_upload_mode(client: Client, message: Message):
    """Set upload mode"""
    user_id = message.from_user.id
    
    if len(message.command) < 2:
        current = await client.db.get_upload_mode(user_id)
        await message.reply_text(
            f"📤 **Upload Mode Settings**\n\n"
            f"**Current:** {current.title()}\n\n"
            f"**Usage:** `/upload <mode>`\n\n"
            f"**Options:**\n"
            f"• `default` - Upload directly to chat\n"
            f"• `channel` - Upload to specified channel\n\n"
            f"**Example:** `/upload default`"
        )
        return
    
    mode = message.command[1].lower()
    
    valid_modes = ["default", "channel"]
    if mode not in valid_modes:
        await message.reply_text(
            f"❌ **Invalid upload mode!**\n\n"
            f"Valid options: {', '.join(valid_modes)}"
        )
        return
    
    await client.db.set_upload_mode(user_id, mode)
    await message.reply_text(
        f"✅ **Upload mode set to:** {mode.title()}\n\n"
        f"Encoded videos will be uploaded using this mode."
  )
