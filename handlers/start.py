from pyrogram import Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import Config
import os
import logging

logger = logging.getLogger(__name__)

# Import the function to get start pic path
START_PIC_PATH = "./start_pic.jpg"

async def start_command(client: Client, message: Message):
    """Handle /start command with custom start picture support"""
    
    user = message.from_user
    user_id = user.id
    first_name = user.first_name
    
    # Add user to database
    try:
        await client.db.add_user(user_id, first_name, user.username if user.username else "")
    except Exception as e:
        logger.error(f"Error adding user to database: {e}")
    
    # Create inline keyboard
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📚 Help", callback_data="help"),
            InlineKeyboardButton("⚙️ Settings", callback_data="settings")
        ],
        [
            InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/Leoyagamihere"),
            InlineKeyboardButton("📢 Updates", url="https://t.me/yagamimoviez")
        ]
    ])
    
    # Format the start message with user's name
    text = Config.START_MESSAGE.format(first_name=first_name)
    
    # Check if custom start picture exists
    try:
        if os.path.exists(START_PIC_PATH):
            # Send with custom picture
            await client.send_photo(
                chat_id=message.chat.id,
                photo=START_PIC_PATH,
                caption=text,
                reply_markup=keyboard
            )
            logger.info(f"Sent start message with custom picture to user {user_id}")
        else:
            # Send text only (no custom picture set)
            await message.reply_text(
                text=text,
                reply_markup=keyboard,
                disable_web_page_preview=True
            )
            logger.info(f"Sent start message (text only) to user {user_id}")
    
    except Exception as e:
        logger.error(f"Error sending start message with picture: {e}")
        # Fallback to text if image fails
        try:
            await message.reply_text(
                text=text,
                reply_markup=keyboard,
                disable_web_page_preview=True
            )
        except Exception as e2:
            logger.error(f"Error sending fallback start message: {e2}")
