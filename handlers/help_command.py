from pyrogram import Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import Config
import logging

logger = logging.getLogger(__name__)

async def help_command(client: Client, message: Message):
    """Handle /help command"""
    
    # Create help buttons
    buttons = [
        [
            InlineKeyboardButton("🎬 Encoding", callback_data="help_encoding"),
            InlineKeyboardButton("✂️ Editing", callback_data="help_editing")
        ],
        [
            InlineKeyboardButton("📝 Subtitles", callback_data="help_subtitles"),
            InlineKeyboardButton("🎵 Audio", callback_data="help_audio")
        ],
        [
            InlineKeyboardButton("⚙️ Settings", callback_data="help_settings"),
            InlineKeyboardButton("ℹ️ Info", callback_data="help_info")
        ],
        [
            InlineKeyboardButton("🔙 Back", callback_data="start")
        ]
    ]
    
    await message.reply_text(
        Config.HELP_MESSAGE,
        reply_markup=InlineKeyboardMarkup(buttons),
        disable_web_page_preview=True
    )

async def show_encoding_help(client: Client, callback_query):
    """Show encoding commands help"""
    text = """
🎬 **Encoding Commands**

**Quality Commands:**
/144p - Convert to 144p
/240p - Convert to 240p
/360p - Convert to 360p
/480p - Convert to 480p
/720p - Convert to 720p (HD)
/1080p - Convert to 1080p (Full HD)
/2160p - Convert to 2160p (4K)

**Other Commands:**
/all - Encode in all qualities (Premium)
/compress <percentage> - Compress video

**Usage:**
Reply to a video with the quality command.

**Example:**
1. Send or forward a video
2. Reply to that video with /720p
3. Wait for encoding to complete
"""
    
    buttons = [[InlineKeyboardButton("🔙 Back to Help", callback_data="help")]]
    
    await callback_query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def show_editing_help(client: Client, callback_query):
    """Show editing commands help"""
    text = """
✂️ **Editing Commands**

/cut - Trim video by time
/crop - Change video aspect ratio
/merge - Merge multiple videos
/addwatermark - Add logo watermark

**Examples:**

**Trim Video:**
Reply to video: `/cut 00:00:10 00:01:30`
This trims from 10 seconds to 1 minute 30 seconds

**Crop Video:**
Use /crop and select aspect ratio:
• 16:9 - Widescreen
• 9:16 - Vertical (Stories)
• 1:1 - Square (Instagram)
• 4:3 - Classic TV
• 21:9 - Cinematic

**Merge Videos:**
1. Send multiple videos
2. Use /merge command
3. Videos merge in order sent
"""
    
    buttons = [[InlineKeyboardButton("🔙 Back to Help", callback_data="help")]]
    
    await callback_query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def show_subtitles_help(client: Client, callback_query):
    """Show subtitle commands help"""
    text = """
📝 **Subtitle Commands**

/sub - Add soft subtitles
/hsub - Add hard subtitles (burned in)
/rsub - Remove all subtitles
/extract_sub - Extract subtitles from video

**Soft Subtitles:**
• Can be turned on/off by viewer
• Reply to video, then send subtitle file (SRT/ASS/VTT)

**Hard Subtitles:**
• Permanently burned into video
• Reply to video, then send subtitle file

**Supported Formats:**
• SRT (SubRip)
• ASS (Advanced SubStation Alpha)
• VTT (WebVTT)
• SUB (MicroDVD)

**Extract Subtitles:**
Reply to a video with /extract_sub to get subtitle file
"""
    
    buttons = [[InlineKeyboardButton("🔙 Back to Help", callback_data="help")]]
    
    await callback_query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def show_audio_help(client: Client, callback_query):
    """Show audio commands help"""
    text = """
🎵 **Audio Commands**

/addaudio - Add audio track to video
/remaudio - Remove audio from video
/extract_audio - Extract audio from video

**Add Audio:**
1. Reply to a video with /addaudio
2. Send an audio file
3. Audio will be added to video

**Remove Audio:**
Reply to a video with /remaudio to create silent video

**Extract Audio:**
Reply to a video with /extract_audio to get audio file in MP3 format

**Supported Audio Formats:**
• MP3
• AAC
• OGG
• WAV
• FLAC
• M4A
"""
    
    buttons = [[InlineKeyboardButton("🔙 Back to Help", callback_data="help")]]
    
    await callback_query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def show_settings_help(client: Client, callback_query):
    """Show settings commands help"""
    text = """
⚙️ **Settings Commands**

/setthumb - Set custom thumbnail
/getthumb - View saved thumbnail
/delthumb - Delete saved thumbnail

/setwatermark <text> - Set watermark text
/getwatermark - View current watermark

/setmedia <type> - Set upload type (video/document)
/spoiler - Toggle spoiler mode
/upload <mode> - Set upload destination

**Examples:**

**Set Thumbnail:**
Send a photo to use as thumbnail for all videos

**Set Watermark:**
/setwatermark @YourChannel
This adds "@YourChannel" text to all encoded videos

**Media Type:**
• video - Upload as video (with player)
• document - Upload as file

**Spoiler Mode:**
Enable to hide video preview with spoiler
"""
    
    buttons = [[InlineKeyboardButton("🔙 Back to Help", callback_data="help")]]
    
    await callback_query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def show_info_help(client: Client, callback_query):
    """Show info commands help"""
    text = """
ℹ️ **Information Commands**

/mediainfo - Get detailed media information
/extract_thumb - Extract thumbnail from video

**Media Info:**
Shows detailed information about video:
• Resolution (width x height)
• Duration
• File size
• Codec information
• Bitrate
• Frame rate
• Audio information

**Extract Thumbnail:**
Reply to a video with /extract_thumb to get a thumbnail image from the video

**Other Info:**
• Reply to any video with quality command
• Bot will show estimated encoding time
• Progress updates every few seconds
• Get notification when complete
"""
    
    buttons = [[InlineKeyboardButton("🔙 Back to Help", callback_data="help")]]
    
    await callback_query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(buttons)
    )
