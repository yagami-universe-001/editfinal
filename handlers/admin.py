from pyrogram import Client
from pyrogram.types import Message
import subprocess
import os
import sys
import logging

logger = logging.getLogger(__name__)

async def restart_bot(client: Client, message: Message):
    """Restart the bot"""
    await message.reply_text("🔄 **Restarting bot...**")
    os.execl(sys.executable, sys.executable, *sys.argv)

async def check_queue(client: Client, message: Message):
    """Check queue status"""
    total = await client.db.get_total_queue()
    await message.reply_text(
        f"📊 **Queue Status**\n\n"
        f"**Total tasks:** {total}\n"
        f"**Status:** {'Active' if total > 0 else 'Empty'}"
    )

async def clear_queue(client: Client, message: Message):
    """Clear all queue tasks"""
    await client.db.clear_queue()
    await message.reply_text("✅ **Queue cleared successfully!**")

async def set_audio_bitrate(client: Client, message: Message):
    """Set audio bitrate"""
    if len(message.command) < 2:
        current = await client.db.get_bot_setting("audio_bitrate", "128k")
        await message.reply_text(
            f"🎵 **Current Audio Bitrate:** {current}\n\n"
            f"**Usage:** `/audio <bitrate>`\n"
            f"**Example:** `/audio 192k`\n\n"
            f"**Common values:** 96k, 128k, 192k, 256k, 320k"
        )
        return
    
    bitrate = message.command[1]
    await client.db.set_bot_setting("audio_bitrate", bitrate)
    await message.reply_text(f"✅ **Audio bitrate set to:** {bitrate}")

async def set_codec(client: Client, message: Message):
    """Set video codec"""
    if len(message.command) < 2:
        current = await client.db.get_bot_setting("codec", "libx264")
        await message.reply_text(
            f"🎬 **Current Codec:** {current}\n\n"
            f"**Usage:** `/codec <codec_name>`\n\n"
            f"**Available codecs:**\n"
            f"• `libx264` - H.264 (Most compatible)\n"
            f"• `libx265` - H.265 (Better compression)\n"
            f"• `libvpx-vp9` - VP9 (WebM)"
        )
        return
    
    codec = message.command[1]
    valid_codecs = ["libx264", "libx265", "libvpx-vp9"]
    
    if codec not in valid_codecs:
        await message.reply_text("❌ Invalid codec! Use: libx264, libx265, or libvpx-vp9")
        return
    
    await client.db.set_bot_setting("codec", codec)
    await message.reply_text(f"✅ **Codec set to:** {codec}")

async def set_preset(client: Client, message: Message):
    """Set encoding preset"""
    if len(message.command) < 2:
        current = await client.db.get_bot_setting("preset", "medium")
        await message.reply_text(
            f"⚙️ **Current Preset:** {current}\n\n"
            f"**Usage:** `/preset <preset_name>`\n\n"
            f"**Available presets:**\n"
            f"• `ultrafast` - Fastest, largest file\n"
            f"• `superfast`\n"
            f"• `veryfast`\n"
            f"• `faster`\n"
            f"• `fast`\n"
            f"• `medium` - Balanced (default)\n"
            f"• `slow` - Better compression\n"
            f"• `slower`\n"
            f"• `veryslow` - Best compression, slowest"
        )
        return
    
    preset = message.command[1]
    valid_presets = ["ultrafast", "superfast", "veryfast", "faster", "fast", "medium", "slow", "slower", "veryslow"]
    
    if preset not in valid_presets:
        await message.reply_text("❌ Invalid preset!")
        return
    
    await client.db.set_bot_setting("preset", preset)
    await message.reply_text(f"✅ **Preset set to:** {preset}")

async def set_crf(client: Client, message: Message):
    """Set CRF value"""
    if len(message.command) < 2:
        current = await client.db.get_bot_setting("crf", 23)
        await message.reply_text(
            f"🎯 **Current CRF:** {current}\n\n"
            f"**Usage:** `/crf <value>`\n"
            f"**Range:** 0-51\n\n"
            f"**Quality guide:**\n"
            f"• 0-17: Visually lossless\n"
            f"• 18-23: High quality (recommended)\n"
            f"• 24-28: Medium quality\n"
            f"• 29+: Low quality\n\n"
            f"Lower CRF = Better quality, larger file size"
        )
        return
    
    try:
        crf = int(message.command[1])
        if crf < 0 or crf > 51:
            await message.reply_text("❌ CRF must be between 0-51!")
            return
        
        await client.db.set_bot_setting("crf", crf)
        await message.reply_text(f"✅ **CRF set to:** {crf}")
    except:
        await message.reply_text("❌ Invalid CRF value!")

async def add_fsub_channel(client: Client, message: Message):
    """Add force subscribe channel"""
    if len(message.command) < 2:
        await message.reply_text(
            "**Usage:** `/addchnl <channel_id>`\n"
            "**Example:** `/addchnl -1001234567890`\n\n"
            "**Important:**\n"
            "• Bot must be admin in the channel\n"
            "• Channel ID must include -100 prefix\n"
            "• Use @username_to_id_bot to get channel ID"
        )
        return
    
    try:
        channel_id = int(message.command[1])
        
        # Verify bot is admin in the channel
        try:
            bot_member = await client.get_chat_member(channel_id, "me")
            if bot_member.status not in ["administrator", "creator"]:
                await message.reply_text(
                    "❌ **Bot is not an admin in this channel!**\n\n"
                    "Please make the bot an admin in the channel first."
                )
                return
        except Exception as e:
            await message.reply_text(
                f"❌ **Cannot access channel!**\n\n"
                f"**Error:** {str(e)}\n\n"
                f"Make sure:\n"
                f"• Bot is added to the channel\n"
                f"• Bot has admin rights\n"
                f"• Channel ID is correct"
            )
            return
        
        # Get channel info
        chat = await client.get_chat(channel_id)
        
        # Add to database
        await client.db.add_fsub_channel(channel_id)
        
        await message.reply_text(
            f"✅ **Force Subscribe Channel Added!**\n\n"
            f"**Channel:** {chat.title}\n"
            f"**ID:** `{channel_id}`\n"
            f"**Username:** @{chat.username if chat.username else 'Private'}\n\n"
            f"Users will need to join this channel to use the bot."
        )
    except ValueError:
        await message.reply_text("❌ Invalid channel ID! Must be a number.")
    except Exception as e:
        logger.error(f"Error adding fsub channel: {e}")
        await message.reply_text(f"❌ **Error:** {str(e)}")

async def delete_fsub_channel(client: Client, message: Message):
    """Delete force subscribe channel"""
    if len(message.command) < 2:
        await message.reply_text(
            "**Usage:** `/delchnl <channel_id>`\n"
            "**Example:** `/delchnl -1001234567890`"
        )
        return
    
    try:
        channel_id = int(message.command[1])
        await client.db.delete_fsub_channel(channel_id)
        await message.reply_text(f"✅ **Channel removed:** {channel_id}")
    except:
        await message.reply_text("❌ Invalid channel ID!")

async def list_fsub_channels(client: Client, message: Message):
    """List all force subscribe channels"""
    channels = await client.db.get_fsub_channels()
    
    if not channels:
        await message.reply_text("📝 **No force subscribe channels configured**")
        return
    
    text = "📋 **Force Subscribe Channels:**\n\n"
    for channel_id in channels:
        try:
            chat = await client.get_chat(channel_id)
            text += f"• {chat.title} (`{channel_id}`)\n"
        except:
            text += f"• Unknown (`{channel_id}`)\n"
    
    await message.reply_text(text)

async def fsub_mode(client: Client, message: Message):
    """Change force subscribe mode"""
    if len(message.command) < 2:
        current = await client.db.get_bot_setting("fsub_mode", "off")
        await message.reply_text(
            f"🔐 **Current Mode:** {current}\n\n"
            f"**Usage:** `/fsub_mode <mode>`\n\n"
            f"**Modes:**\n"
            f"• `off` - Disabled\n"
            f"• `on` - Force join before using bot\n"
            f"• `request` - Request to join"
        )
        return
    
    mode = message.command[1].lower()
    if mode not in ["off", "on", "request"]:
        await message.reply_text("❌ Invalid mode! Use: off, on, or request")
        return
    
    await client.db.set_bot_setting("fsub_mode", mode)
    await message.reply_text(f"✅ **Force subscribe mode:** {mode}")

async def view_shortener(client: Client, message: Message):
    """View shortener settings"""
    api1 = await client.db.get_bot_setting("shortener_api1", "Not set")
    url1 = await client.db.get_bot_setting("shortener_url1", "Not set")
    api2 = await client.db.get_bot_setting("shortener_api2", "Not set")
    url2 = await client.db.get_bot_setting("shortener_url2", "Not set")
    
    await message.reply_text(
        f"🔗 **Shortener Configuration**\n\n"
        f"**Shortener 1:**\n"
        f"• API: `{api1[:20]}...`\n"
        f"• URL: `{url1}`\n\n"
        f"**Shortener 2:**\n"
        f"• API: `{api2[:20]}...`\n"
        f"• URL: `{url2}`"
    )

async def set_shortlink1(client: Client, message: Message):
    """Set shortlink 1 API and URL"""
    if len(message.command) < 3:
        await message.reply_text(
            "**Usage:** `/shortlink1 <api_key> <url>`\n"
            "**Example:** `/shortlink1 your_api_key https://shortener.com`"
        )
        return
    
    api_key = message.command[1]
    url = message.command[2]
    
    await client.db.set_bot_setting("shortener_api1", api_key)
    await client.db.set_bot_setting("shortener_url1", url)
    await message.reply_text("✅ **Shortlink 1 configured!**")

async def set_tutorial1(client: Client, message: Message):
    """Set tutorial for shortener 1"""
    if len(message.command) < 2:
        await message.reply_text(
            "**Usage:** `/tutorial1 <tutorial_url>`\n"
            "**Example:** `/tutorial1 https://t.me/your_tutorial`"
        )
        return
    
    tutorial_url = message.command[1]
    await client.db.set_bot_setting("tutorial1", tutorial_url)
    await message.reply_text("✅ **Tutorial 1 set!**")

async def set_shortlink2(client: Client, message: Message):
    """Set shortlink 2 API and URL"""
    if len(message.command) < 3:
        await message.reply_text(
            "**Usage:** `/shortlink2 <api_key> <url>`\n"
            "**Example:** `/shortlink2 your_api_key https://shortener.com`"
        )
        return
    
    api_key = message.command[1]
    url = message.command[2]
    
    await client.db.set_bot_setting("shortener_api2", api_key)
    await client.db.set_bot_setting("shortener_url2", url)
    await message.reply_text("✅ **Shortlink 2 configured!**")

async def set_tutorial2(client: Client, message: Message):
    """Set tutorial for shortener 2"""
    if len(message.command) < 2:
        await message.reply_text(
            "**Usage:** `/tutorial2 <tutorial_url>`\n"
            "**Example:** `/tutorial2 https://t.me/your_tutorial`"
        )
        return
    
    tutorial_url = message.command[1]
    await client.db.set_bot_setting("tutorial2", tutorial_url)
    await message.reply_text("✅ **Tutorial 2 set!**")

async def view_shortener1_config(client: Client, message: Message):
    """View shortener 1 config"""
    api = await client.db.get_bot_setting("shortener_api1", "Not set")
    url = await client.db.get_bot_setting("shortener_url1", "Not set")
    tutorial = await client.db.get_bot_setting("tutorial1", "Not set")
    
    await message.reply_text(
        f"🔗 **Shortener 1 Configuration**\n\n"
        f"**API Key:** `{api}`\n"
        f"**URL:** `{url}`\n"
        f"**Tutorial:** `{tutorial}`"
    )

async def view_shortener2_config(client: Client, message: Message):
    """View shortener 2 config"""
    api = await client.db.get_bot_setting("shortener_api2", "Not set")
    url = await client.db.get_bot_setting("shortener_url2", "Not set")
    tutorial = await client.db.get_bot_setting("tutorial2", "Not set")
    
    await message.reply_text(
        f"🔗 **Shortener 2 Configuration**\n\n"
        f"**API Key:** `{api}`\n"
        f"**URL:** `{url}`\n"
        f"**Tutorial:** `{tutorial}`"
    )

async def add_premium_user(client: Client, message: Message):
    """Add premium user"""
    if len(message.command) < 3:
        await message.reply_text(
            "**Usage:** `/addpaid <user_id> <days>`\n"
            "**Example:** `/addpaid 123456789 30`"
        )
        return
    
    try:
        user_id = int(message.command[1])
        days = int(message.command[2])
        
        await client.db.add_premium_user(user_id, days)
        await message.reply_text(
            f"✅ **Premium added!**\n\n"
            f"**User ID:** {user_id}\n"
            f"**Duration:** {days} days"
        )
    except:
        await message.reply_text("❌ Invalid user ID or days!")

async def list_premium_users(client: Client, message: Message):
    """List all premium users"""
    users = await client.db.get_premium_users()
    
    if not users:
        await message.reply_text("📝 **No premium users**")
        return
    
    text = "👑 **Premium Users:**\n\n"
    for user in users:
        expiry = user['expiry_date'].strftime('%Y-%m-%d %H:%M:%S')
        text += f"• User ID: `{user['user_id']}`\n  Expires: {expiry}\n\n"
    
    await message.reply_text(text)

async def remove_premium_user(client: Client, message: Message):
    """Remove premium user"""
    if len(message.command) < 2:
        await message.reply_text(
            "**Usage:** `/rempaid <user_id>`\n"
            "**Example:** `/rempaid 123456789`"
        )
        return
    
    try:
        user_id = int(message.command[1])
        await client.db.remove_premium_user(user_id)
        await message.reply_text(f"✅ **Premium removed for:** {user_id}")
    except:
        await message.reply_text("❌ Invalid user ID!")

async def git_update(client: Client, message: Message):
    """Pull latest updates from git"""
    status = await message.reply_text("🔄 **Pulling latest updates...**")
    
    try:
        result = subprocess.run(
            ["git", "pull"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        output = result.stdout + result.stderr
        
        if result.returncode == 0:
            await status.edit_text(
                f"✅ **Update successful!**\n\n"
                f"```\n{output[:1000]}\n```\n\n"
                f"Use /restart to apply changes"
            )
        else:
            await status.edit_text(
                f"❌ **Update failed!**\n\n"
                f"```\n{output[:1000]}\n```"
            )
    except subprocess.TimeoutExpired:
        await status.edit_text("❌ **Update timeout!**")
    except Exception as e:
        await status.edit_text(f"❌ **Error:** {str(e)}")

async def set_start_pic(client: Client, message: Message):
    """Set start picture for bot"""
    if len(message.command) < 2:
        current_pic = await client.db.get_bot_setting("start_pic", "Not set")
        
        await message.reply_text(
            "🖼️ **Start Picture Settings**\n\n"
            f"**Current:** {'Set' if current_pic != 'Not set' else 'Not set'}\n\n"
            "**To set a new picture:**\n\n"
            "**Method 1 - Reply to photo:**\n"
            "Reply to a photo with `/setstartpic`\n\n"
            "**Method 2 - Use URL:**\n"
            "`/setstartpic <image_url>`\n\n"
            "**Method 3 - Use file_id:**\n"
            "`/setstartpic <file_id>`\n\n"
            "**To remove:**\n"
            "`/delstartpic`"
        )
        return
    
    # Check if replied to a photo
    if message.reply_to_message and message.reply_to_message.photo:
        photo_id = message.reply_to_message.photo.file_id
        await client.db.set_bot_setting("start_pic", photo_id)
        
        # Update config
        Config.START_PIC = photo_id
        
        await message.reply_text(
            "✅ **Start picture set successfully!**\n\n"
            "The new picture will be shown on /start command."
        )
        return
    
    # Get URL or file_id from command
    pic_input = message.command[1]
    
    # Validate if URL or file_id
    if pic_input.startswith('http://') or pic_input.startswith('https://'):
        # It's a URL
        await client.db.set_bot_setting("start_pic", pic_input)
        Config.START_PIC = pic_input
        await message.reply_text("✅ **Start picture URL set successfully!**")
    else:
        # Assume it's a file_id
        await client.db.set_bot_setting("start_pic", pic_input)
        Config.START_PIC = pic_input
        await message.reply_text("✅ **Start picture file_id set successfully!**")

async def delete_start_pic(client: Client, message: Message):
    """Delete start picture"""
    await client.db.set_bot_setting("start_pic", "")
    Config.START_PIC = ""
    await message.reply_text("✅ **Start picture removed!**")

async def view_start_pic(client: Client, message: Message):
    """View current start picture"""
    start_pic = await client.db.get_bot_setting("start_pic", "")
    
    if not start_pic:
        await message.reply_text("❌ **No start picture set!**")
        return
    
    try:
        await message.reply_photo(
            photo=start_pic,
            caption="🖼️ **Current Start Picture**"
        )
    except Exception as e:
        await message.reply_text(
            f"❌ **Error displaying picture!**\n\n"
            f"**Error:** {str(e)}\n"
            f"**Picture:** `{start_pic}`"
        )
