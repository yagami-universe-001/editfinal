from pyrogram import Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from utils.ffmpeg import FFmpegEncoder
from utils.helpers import human_readable_size, format_time, parse_time
import logging
import os
import time

logger = logging.getLogger(__name__)

async def handle_media(client: Client, message: Message):
    """Handle incoming video/document uploads"""
    user_id = message.from_user.id
    
    # Get file info
    if message.video:
        file = message.video
        file_type = "Video"
    elif message.document:
        file = message.document
        file_type = "Document"
    else:
        return
    
    file_size = human_readable_size(file.file_size)
    duration = format_time(file.duration) if hasattr(file, 'duration') and file.duration else "Unknown"
    
    # Create action buttons
    buttons = [
        [
            InlineKeyboardButton("720p", callback_data="quality_720p"),
            InlineKeyboardButton("1080p", callback_data="quality_1080p")
        ],
        [
            InlineKeyboardButton("480p", callback_data="quality_480p"),
            InlineKeyboardButton("360p", callback_data="quality_360p")
        ],
        [
            InlineKeyboardButton("✂️ Trim", callback_data="action_trim"),
            InlineKeyboardButton("📐 Crop", callback_data="action_crop")
        ],
        [
            InlineKeyboardButton("ℹ️ Media Info", callback_data="action_mediainfo"),
            InlineKeyboardButton("❌ Close", callback_data="close")
        ]
    ]
    
    await message.reply_text(
        f"📹 **{file_type} Received!**\n\n"
        f"**File Name:** `{file.file_name}`\n"
        f"**Size:** {file_size}\n"
        f"**Duration:** {duration}\n\n"
        f"**Choose an action:**\n"
        f"• Select quality to encode\n"
        f"• Use buttons for quick actions\n"
        f"• Or use commands like /720p, /compress, /cut, etc.",
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    
    # Update user activity
    await client.db.update_user_activity(user_id)

async def add_watermark(client: Client, message: Message):
    """Add logo watermark to video"""
    if not message.reply_to_message:
        await message.reply_text(
            "💧 **Add Logo Watermark**\n\n"
            "**How to use:**\n"
            "1. Reply to a video with /addwatermark\n"
            "2. Send a logo image (PNG with transparency recommended)\n"
            "3. Select watermark position\n\n"
            "The logo will be added to your video."
        )
        return
    
    replied = message.reply_to_message
    
    if not (replied.video or replied.document):
        await message.reply_text("❌ **Please reply to a video!**")
        return
    
    await message.reply_text(
        "📸 **Send your logo image**\n\n"
        "Send a photo to use as watermark.\n"
        "PNG with transparency works best!"
    )

async def trim_video(client: Client, message: Message):
    """Trim video by time range"""
    if not message.reply_to_message:
        await message.reply_text(
            "✂️ **Trim Video**\n\n"
            "**Usage:** `/cut <start_time> <end_time>`\n\n"
            "**Time Format:**\n"
            "• HH:MM:SS (01:30:00)\n"
            "• MM:SS (90:00)\n"
            "• SS (5400)\n\n"
            "**Examples:**\n"
            "• `/cut 00:00:10 00:01:30` - From 10s to 1m30s\n"
            "• `/cut 30 90` - From 30s to 90s\n"
            "• `/cut 01:00:00 02:30:00` - From 1h to 2h30m\n\n"
            "Reply to a video with this command."
        )
        return
    
    if len(message.command) < 3:
        await message.reply_text(
            "❌ **Invalid format!**\n\n"
            "**Usage:** `/cut <start> <end>`\n"
            "**Example:** `/cut 00:00:10 00:01:30`"
        )
        return
    
    start_time = message.command[1]
    end_time = message.command[2]
    
    # Validate time format
    start_seconds = parse_time(start_time)
    end_seconds = parse_time(end_time)
    
    if start_seconds >= end_seconds:
        await message.reply_text("❌ **Start time must be before end time!**")
        return
    
    await message.reply_text(
        f"✂️ **Trimming video...**\n\n"
        f"**From:** {start_time}\n"
        f"**To:** {end_time}\n\n"
        f"Please wait..."
    )

async def crop_video(client: Client, message: Message):
    """Crop video to different aspect ratio"""
    if not message.reply_to_message:
        buttons = [
            [
                InlineKeyboardButton("16:9 Widescreen", callback_data="aspect_16:9"),
                InlineKeyboardButton("9:16 Vertical", callback_data="aspect_9:16")
            ],
            [
                InlineKeyboardButton("1:1 Square", callback_data="aspect_1:1"),
                InlineKeyboardButton("4:3 Classic", callback_data="aspect_4:3")
            ],
            [
                InlineKeyboardButton("21:9 Cinematic", callback_data="aspect_21:9")
            ]
        ]
        
        await message.reply_text(
            "📐 **Crop Video**\n\n"
            "**Available Aspect Ratios:**\n"
            "• 16:9 - Standard widescreen (YouTube)\n"
            "• 9:16 - Vertical (Stories, Reels)\n"
            "• 1:1 - Square (Instagram feed)\n"
            "• 4:3 - Classic TV\n"
            "• 21:9 - Cinematic widescreen\n\n"
            "Reply to a video and select ratio:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return
    
    replied = message.reply_to_message
    
    if not (replied.video or replied.document):
        await message.reply_text("❌ **Please reply to a video!**")
        return
    
    buttons = [
        [
            InlineKeyboardButton("16:9", callback_data="crop_16:9"),
            InlineKeyboardButton("9:16", callback_data="crop_9:16")
        ],
        [
            InlineKeyboardButton("1:1", callback_data="crop_1:1"),
            InlineKeyboardButton("4:3", callback_data="crop_4:3")
        ],
        [
            InlineKeyboardButton("21:9", callback_data="crop_21:9")
        ]
    ]
    
    await message.reply_text(
        "📐 **Select Aspect Ratio:**",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def add_audio(client: Client, message: Message):
    """Add audio track to video"""
    if not message.reply_to_message:
        await message.reply_text(
            "🎵 **Add Audio to Video**\n\n"
            "**How to use:**\n"
            "1. Reply to a video with /addaudio\n"
            "2. Send an audio file\n"
            "3. Audio will be added to the video\n\n"
            "**Note:** Original audio will be replaced.\n"
            "Use /merge to keep both audio tracks."
        )
        return
    
    replied = message.reply_to_message
    
    if not (replied.video or replied.document):
        await message.reply_text("❌ **Please reply to a video!**")
        return
    
    await message.reply_text(
        "🎵 **Send audio file**\n\n"
        "Send an audio file (MP3, AAC, OGG, etc.)\n"
        "The audio will replace the video's original audio."
    )

async def remove_audio(client: Client, message: Message):
    """Remove audio from video"""
    if not message.reply_to_message:
        await message.reply_text(
            "🔇 **Remove Audio from Video**\n\n"
            "Reply to a video with /remaudio to create a silent video.\n\n"
            "This removes all audio tracks from the video."
        )
        return
    
    replied = message.reply_to_message
    
    if not (replied.video or replied.document):
        await message.reply_text("❌ **Please reply to a video!**")
        return
    
    await message.reply_text(
        "🔇 **Removing audio...**\n\n"
        "Creating silent video. Please wait..."
    )

async def get_media_info(client: Client, message: Message):
    """Get detailed media information"""
    if not message.reply_to_message:
        await message.reply_text(
            "📊 **Get Media Information**\n\n"
            "Reply to a video with /mediainfo to get detailed information:\n\n"
            "• Resolution and dimensions\n"
            "• Duration\n"
            "• File size\n"
            "• Video codec\n"
            "• Audio codec\n"
            "• Bitrate\n"
            "• Frame rate\n"
            "• And more..."
        )
        return
    
    replied = message.reply_to_message
    
    if not (replied.video or replied.document):
        await message.reply_text("❌ **Please reply to a video!**")
        return
    
    status = await message.reply_text("📊 **Fetching media information...**")
    
    try:
        # Download file temporarily
        file_path = await replied.download()
        
        # Get video info using FFmpeg
        encoder = FFmpegEncoder()
        info = await encoder.get_video_info(file_path)
        
        if not info:
            await status.edit_text("❌ **Failed to get media info!**")
            return
        
        # Parse video stream info
        video_stream = next((s for s in info['streams'] if s['codec_type'] == 'video'), None)
        audio_stream = next((s for s in info['streams'] if s['codec_type'] == 'audio'), None)
        
        # Build info message
        info_text = "📊 **Media Information**\n\n"
        
        if video_stream:
            width = video_stream.get('width', 'Unknown')
            height = video_stream.get('height', 'Unknown')
            codec = video_stream.get('codec_name', 'Unknown')
            fps = video_stream.get('r_frame_rate', 'Unknown')
            
            info_text += f"**Video:**\n"
            info_text += f"• Resolution: {width}x{height}\n"
            info_text += f"• Codec: {codec.upper()}\n"
            info_text += f"• FPS: {fps}\n\n"
        
        if audio_stream:
            audio_codec = audio_stream.get('codec_name', 'Unknown')
            sample_rate = audio_stream.get('sample_rate', 'Unknown')
            channels = audio_stream.get('channels', 'Unknown')
            
            info_text += f"**Audio:**\n"
            info_text += f"• Codec: {audio_codec.upper()}\n"
            info_text += f"• Sample Rate: {sample_rate} Hz\n"
            info_text += f"• Channels: {channels}\n\n"
        
        # Format info
        format_info = info.get('format', {})
        duration = float(format_info.get('duration', 0))
        size = int(format_info.get('size', 0))
        bitrate = int(format_info.get('bit_rate', 0))
        
        info_text += f"**General:**\n"
        info_text += f"• Duration: {format_time(duration)}\n"
        info_text += f"• Size: {human_readable_size(size)}\n"
        info_text += f"• Bitrate: {bitrate // 1000} kbps\n"
        info_text += f"• Format: {format_info.get('format_name', 'Unknown').upper()}"
        
        await status.edit_text(info_text)
        
        # Cleanup
        if os.path.exists(file_path):
            os.remove(file_path)
            
    except Exception as e:
        logger.error(f"Error getting media info: {e}")
        await status.edit_text(f"❌ **Error:** {str(e)}")
