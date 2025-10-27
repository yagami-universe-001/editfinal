from pyrogram import Client
from pyrogram.types import Message, User
import os
import time
from utils.ffmpeg import FFmpegEncoder
from utils.progress import progress_callback
from utils.helpers import human_readable_size, format_time
import logging

logger = logging.getLogger(__name__)

# Resolution configurations
RESOLUTIONS = {
    "144p": {"height": 144, "bitrate": "128k"},
    "240p": {"height": 240, "bitrate": "256k"},
    "360p": {"height": 360, "bitrate": "512k"},
    "480p": {"height": 480, "bitrate": "1M"},
    "720p": {"height": 720, "bitrate": "2M"},
    "1080p": {"height": 1080, "bitrate": "4M"},
    "2160p": {"height": 2160, "bitrate": "8M"}
}

async def encode_video(client: Client, message: Message, from_user: User = None):
    """Encode video to specific quality"""
    user = from_user or message.from_user
    user_id = user.id
    command = message.command[0].replace("/", "")
    
    if command not in RESOLUTIONS:
        await message.reply_text("❌ Invalid quality!")
        return
    
    # Check if user has replied to a video
    if not message.reply_to_message:
        await message.reply_text(
            "⚠️ **Please reply to a video with this command!**\n\n"
            f"Example: Reply to video with `/{command}`"
        )
        return
    
    replied = message.reply_to_message
    
    if not (replied.video or replied.document):
        await message.reply_text("❌ Please reply to a video file!")
        return
    
    # Check file size
    is_premium = await client.db.is_premium_user(user_id)
    max_size = 4294967296 if is_premium else 2147483648  # 4GB for premium, 2GB for free
    
    file_size = replied.video.file_size if replied.video else replied.document.file_size
    
    if file_size > max_size:
        await message.reply_text(
            f"❌ File size too large!\n\n"
            f"**Your limit:** {human_readable_size(max_size)}\n"
            f"**File size:** {human_readable_size(file_size)}\n\n"
            "💎 Upgrade to premium for higher limits!"
        )
        return
    
    # Send processing message
    status = await message.reply_text("📥 **Downloading video...**")
    
    try:
        # Download video
        start_time = time.time()
        download_path = await replied.download(
            file_name=f"./downloads/{user_id}/",
            progress=progress_callback,
            progress_args=(status, start_time, "Downloading")
        )
        
        # Get encoding settings
        resolution = RESOLUTIONS[command]
        codec = await client.db.get_bot_setting("codec", "libx264")
        preset = await client.db.get_bot_setting("preset", "medium")
        crf = await client.db.get_bot_setting("crf", 23)
        audio_bitrate = await client.db.get_bot_setting("audio_bitrate", "128k")
        
        # Get user settings
        watermark = await client.db.get_watermark(user_id)
        
        # Encode video
        await status.edit_text(f"🔄 **Encoding to {command}...**\n\nThis may take a while...")
        
        output_path = download_path.rsplit(".", 1)[0] + f"_{command}.mp4"
        
        encoder = FFmpegEncoder()
        success = await encoder.encode_video(
            input_file=download_path,
            output_file=output_path,
            height=resolution["height"],
            video_bitrate=resolution["bitrate"],
            audio_bitrate=audio_bitrate,
            codec=codec,
            preset=preset,
            crf=crf,
            watermark_text=watermark
        )
        
        if not success:
            await status.edit_text("❌ Encoding failed!")
            return
        
        # Get output file info
        output_size = os.path.getsize(output_path)
        encoding_time = time.time() - start_time
        
        # Get thumbnail
        thumbnail = await client.db.get_thumbnail(user_id)
        
        # Get media type preference
        media_type = await client.db.get_media_type(user_id)
        spoiler = await client.db.get_spoiler(user_id)
        
        # Upload video
        await status.edit_text(f"📤 **Uploading {command} video...**")
        
        caption = (
            f"📹 **Video Encoded**\n\n"
            f"**Quality:** {command}\n"
            f"**Size:** {human_readable_size(output_size)}\n"
            f"**Time:** {format_time(encoding_time)}\n"
            f"**Codec:** {codec.upper()}\n"
            f"**Preset:** {preset}"
        )
        
        start_time = time.time()
        
        if media_type == "document":
            await message.reply_document(
                document=output_path,
                caption=caption,
                thumb=thumbnail,
                progress=progress_callback,
                progress_args=(status, start_time, "Uploading")
            )
        else:
            await message.reply_video(
                video=output_path,
                caption=caption,
                thumb=thumbnail,
                has_spoiler=spoiler,
                supports_streaming=True,
                progress=progress_callback,
                progress_args=(status, start_time, "Uploading")
            )
        
        await status.delete()
        
        # Cleanup
        try:
            os.remove(download_path)
            os.remove(output_path)
        except:
            pass
        
        # Update stats
        await client.db.increment_encoding_count(user_id)
        
    except Exception as e:
        logger.error(f"Encoding error: {e}")
        await status.edit_text(f"❌ **Error:** {str(e)}")

async def encode_all_qualities(client: Client, message: Message):
    """Encode video in all qualities"""
    await message.reply_text(
        "🎬 **Encode All Qualities**\n\n"
        "This will encode your video in all available qualities:\n"
        "144p, 240p, 360p, 480p, 720p, 1080p\n\n"
        "⚠️ This process takes a long time!\n\n"
        "Reply to a video to start."
    )
    
    if not message.reply_to_message:
        return
    
    replied = message.reply_to_message
    if not (replied.video or replied.document):
        await message.reply_text("❌ Please reply to a video!")
        return
    
    user_id = message.from_user.id
    
    # Check premium status
    is_premium = await client.db.is_premium_user(user_id)
    if not is_premium:
        await message.reply_text(
            "💎 **Premium Feature**\n\n"
            "The 'Encode All' feature is only available for premium users!\n\n"
            "Contact admin to get premium access."
        )
        return
    
    status = await message.reply_text("📥 **Starting batch encoding...**")
    
    qualities = ["144p", "240p", "360p", "480p", "720p", "1080p"]
    completed = 0
    
    for quality in qualities:
        try:
            await status.edit_text(f"🔄 **Encoding {quality}... ({completed + 1}/{len(qualities)})**")
            
            # Create temporary message for encoding
            temp_msg = await message.reply_to_message.reply_text(f"/{quality}")
            temp_msg.command = [quality]
            temp_msg.reply_to_message = message.reply_to_message
            
            await encode_video(client, temp_msg, from_user=message.from_user)
            await temp_msg.delete()
            
            completed += 1
            
        except Exception as e:
            logger.error(f"Error encoding {quality}: {e}")
            continue
    
    await status.edit_text(f"✅ **Batch encoding completed!**\n\nEncoded {completed}/{len(qualities)} qualities.")

async def compress_video(client: Client, message: Message):
    """Compress video"""
    await message.reply_text(
        "🗜️ **Video Compression**\n\n"
        "Reply to a video with:\n"
        "`/compress <percentage>`\n\n"
        "**Example:**\n"
        "`/compress 50` - Reduce size by 50%\n"
        "`/compress 75` - Reduce size by 75%\n\n"
        "⚠️ Higher compression = lower quality"
    )
    
    if not message.reply_to_message:
        return
    
    if len(message.command) < 2:
        await message.reply_text("❌ Please specify compression percentage!\n\nExample: `/compress 50`")
        return
    
    try:
        compression = int(message.command[1])
        if compression < 10 or compression > 90:
            await message.reply_text("❌ Compression must be between 10-90%")
            return
    except:
        await message.reply_text("❌ Invalid compression value!")
        return
    
    # Calculate CRF based on compression
    crf = int(18 + (compression / 100) * 33)  # Scale from 18-51
    
    await message.reply_text(
        f"🗜️ **Compressing video...**\n\n"
        f"**Compression:** {compression}%\n"
        f"**CRF Value:** {crf}\n\n"
        "Please wait..."
    )
    
    # Use encode_video function with custom CRF
    # Implementation similar to encode_video but with custom CRF
