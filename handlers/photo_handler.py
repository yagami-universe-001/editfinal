from pyrogram import Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import logging

logger = logging.getLogger(__name__)

# Track if user is in thumbnail setting mode
thumbnail_mode = {}

async def handle_photo(client: Client, message: Message):
    """Handle photo messages for thumbnail setting"""
    user_id = message.from_user.id
    
    # Check if photo has caption with /setthumb command
    if message.caption and message.caption.startswith('/setthumb'):
        photo = message.photo.file_id
        await client.db.set_thumbnail(user_id, photo)
        await message.reply_text("✅ **Thumbnail saved successfully!**")
        return
    
    # Check if user is in thumbnail setting mode
    if user_id in thumbnail_mode and thumbnail_mode[user_id]:
        photo = message.photo.file_id
        await client.db.set_thumbnail(user_id, photo)
        thumbnail_mode[user_id] = False
        await message.reply_text(
            "✅ **Thumbnail saved successfully!**\n\n"
            "This thumbnail will be used for all your encoded videos."
        )
        return
    
    # Ask if user wants to save as thumbnail
    buttons = [
        [
            InlineKeyboardButton("✅ Save as Thumbnail", callback_data=f"save_thumb_{message.id}"),
            InlineKeyboardButton("❌ Cancel", callback_data="close")
        ]
    ]
    
    await message.reply_text(
        "📸 **Photo Received**\n\n"
        "Do you want to save this as your default thumbnail?",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def enable_thumbnail_mode(user_id: int):
    """Enable thumbnail setting mode for user"""
    thumbnail_mode[user_id] = True

async def disable_thumbnail_mode(user_id: int):
    """Disable thumbnail setting mode for user"""
    if user_id in thumbnail_mode:
        thumbnail_mode[user_id] = False
