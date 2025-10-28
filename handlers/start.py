from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant, ChatAdminRequired
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
        
        if channels:
            not_joined = []
            
            for channel_id in channels:
                try:
                    member = await client.get_chat_member(channel_id, user_id)
                    # Check if user is actually a member
                    if member.status not in ["member", "administrator", "creator"]:
                        not_joined.append(channel_id)
                except UserNotParticipant:
                    not_joined.append(channel_id)
                except ChatAdminRequired:
                    logger.error(f"Bot is not admin in channel {channel_id}")
                    continue
                except Exception as e:
                    logger.error(f"Error checking membership in {channel_id}: {e}")
                    continue
            
            # If user hasn't joined all required channels
            if not_joined:
                buttons = []
                
                for channel_id in not_joined:
                    try:
                        chat = await client.get_chat(channel_id)
                        # Get invite link
                        if chat.username:
                            invite_link = f"https://t.me/{chat.username}"
                        else:
                            try:
                                invite_link = await client.export_chat_invite_link(channel_id)
                            except:
                                invite_link = chat.invite_link
                        
                        if invite_link:
                            buttons.append([InlineKeyboardButton(
                                f"Join {chat.title}", 
                                url=invite_link
                            )])
                    except Exception as e:
                        logger.error(f"Error getting channel info {channel_id}: {e}")
                        continue
                
                # Add refresh button
                buttons.append([InlineKeyboardButton("✅ Refresh", callback_data="check_fsub")])
                
                await message.reply_text(
                    "⚠️ **You must join these channels to use the bot:**\n\n"
                    "Click the buttons below to join, then click **Refresh** to verify.",
                    reply_markup=InlineKeyboardMarkup(buttons)
                )
                return
    
    # User has joined all channels or fsub is disabled - show main menu
    await show_main_menu(client, message)

async def show_main_menu(client: Client, message):
    """Show main menu to user"""
    user_id = message.from_user.id
    
    # Check if premium user
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
    
    # Get start picture from config
    start_pic = Config.START_PIC
    
    caption = Config.START_MESSAGE + premium_text
    
    # Send with photo if available
    if start_pic:
        try:
            # Check if it's a URL or file_id
            if start_pic.startswith('http://') or start_pic.startswith('https://'):
                # It's a URL
                await message.reply_photo(
                    photo=start_pic,
                    caption=caption,
                    reply_markup=InlineKeyboardMarkup(buttons)
                )
            else:
                # It's a file_id
                await message.reply_photo(
                    photo=start_pic,
                    caption=caption,
                    reply_markup=InlineKeyboardMarkup(buttons)
                )
        except Exception as e:
            logger.error(f"Error sending start picture: {e}")
            # Fallback to text message
            await message.reply_text(
                caption,
                reply_markup=InlineKeyboardMarkup(buttons),
                disable_web_page_preview=True
            )
    else:
        # No picture, send text only
        await message.reply_text(
            caption,
            reply_markup=InlineKeyboardMarkup(buttons),
            disable_web_page_preview=True
        )
    
    await client.db.update_user_activity(user_id)
