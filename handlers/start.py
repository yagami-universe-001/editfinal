from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import Config
import logging

logger = logging.getLogger(__name__)

async def start_command(client: Client, message):
    """Handle /start command"""
    user_id = message.from_user.id
    
    # Add user to database
    if not await client.db.is_user_exist(user_id):
        await client.db.add_user(user_id)
        logger.info(f"New user: {user_id}")
    
    # Check force subscribe
    fsub_mode = await client.db.get_bot_setting("fsub_mode", "off")
    if fsub_mode in ["on", "request"]:
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
            buttons = []
            for channel_id in not_joined:
                try:
                    chat = await client.get_chat(channel_id)
                    invite_link = chat.invite_link or f"https://t.me/{chat.username}"
                    buttons.append([InlineKeyboardButton(f"Join {chat.title}", url=invite_link)])
                except:
                    pass
            
            buttons.append([InlineKeyboardButton("✅ Refresh", callback_data="check_fsub")])
            
            await message.reply_text(
                "⚠️ **You must join these channels to use the bot:**\n\n"
                "Click the buttons below to join, then click Refresh.",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
            return
    
    # Check if premium user
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
    
    await message.reply_text(
        Config.START_MESSAGE + f"\n\n{premium_text}",
        reply_markup=InlineKeyboardMarkup(buttons),
        disable_web_page_preview=True
    )
    
    await client.db.update_user_activity(user_id)
