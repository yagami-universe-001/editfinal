from pyrogram import Client
from pyrogram.types import Message
import os
import time
from utils.fast_encoder import FastEncoder
from utils.enhanced_progress import EnhancedProgress
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

async def fast_encode_video(client: Client, message: Message):
    """Optimized fast video encoding with detailed progress"""
    user_id = message.from_user.id
    command = message.command[0].replace("/", "")
    
    if command not in RESOLUTIONS:
        await message.reply_text("❌ Invalid quality!")
        return
    
    # Check if user has replied to a video
    if not message.reply_to_message:
        await message.reply_text(
            f"⚠️ **Please reply to a video with this command!**\n\n"
            f"Example: Reply to video with `/{command}`"
        )
        return
    
    replied = message.reply_to_message
    
    if not (replied.video or replied.document):
        await message.reply_text("❌ Please reply to a video file!")
        return
    
    # Get file info
    if replied.video:
        file = replied.video
        file_name = file.file_name or f"video_{int(time.time())}.mp4"
    else:
        file = replied.document
        file_name = file.file_name or f"document_{int(time.time())}.mp4"
    
    file_size = file.file_size
    
    # Check file size
    is_premium = await client.db.is_premium_user(user_id)
    max_size = 4294967296 if is_premium else 2147483648  # 4GB for premium, 2GB for free
    
    if file_size > max_size:
        await message.reply_text(
            f"❌ **File size too large!**\n\n"
            f"**Your limit:** {human_readable_size(max_size)}\n"
            f"**File size:** {human_readable_size(file_size)}\n\n"
            "💎 Upgrade to premium for higher limits!"
        )
        return
    
    # Send initial status
    status = await message.reply_text(
        f"**▸ File:** `{file_name[:35]}...`\n\n"
        f"**▸ Status:** `Starting...`\n"
        f"[░░░░░░░░░░░░░░░░░░░░] 0.00%\n\n"
        f"**▸ Preparing to download...**"
    )
    
    try:
        # Create download directory
        download_dir = f"./downloads/{user_id}/"
        os.makedirs(download_dir, exist_ok=True)
        
        # Download video with enhanced progress
        start_time = time.time()
        progress_tracker = EnhancedProgress(total_size=file_size)
        
        download_path = await replied.download(
            file_name=download_dir,
            progress=lambda c, t: progress_tracker.download_progress(c, t, status, "Downloading")
        )
        
        download_time = time.time() - start_time
        
        # Get encoding settings
        resolution = RESOLUTIONS[command]
        codec = await client.db.get_bot_setting("codec", "libx264")
        preset = await client.db.get_bot_setting("preset", "faster")  # Changed to faster
        crf = await client.db.get_bot_setting("crf", 23)
        audio_bitrate = await client.db.get_bot_setting("audio_bitrate", "128k")
        
        # Get user settings
        watermark = await client.db.get_watermark(user_id)
        
        # Encode video with progress
        await status.edit_text(
            f"**▸ File:** `{file_name[:35]}...`\n\n"
            f"**▸ Status:** `Encoding`\n"
            f"[░░░░░░░░░░░░░░░░░░░░] 0.00%\n\n"
            f"**▸ Starting encoding...**\n"
            f"**▸ Quality:** {command}"
        )
        
        output_path = download_path.rsplit(".", 1)[0] + f"_{command}.mp4"
        
        encoder = FastEncoder()
        encoding_start = time.time()
        
        success = await encoder.encode_video_fast(
            input_file=download_path,
            output_file=output_path,
            height=resolution["height"],
            video_bitrate=resolution["bitrate"],
            audio_bitrate=audio_bitrate,
            codec=codec,
            preset=preset,
            crf=crf,
            watermark_text=watermark,
            progress_callback=EnhancedProgress().encoding_progress,
            status_msg=status,
            file_name=file_name
        )
        
        if not success:
            await status.edit_text("❌ Encoding failed!")
            return
        
        encoding_time = time.time() - encoding_start
        
        # Get output file info
        output_size = os.path.getsize(output_path)
        
        # Get user preferences
        thumbnail = await client.db.get_thumbnail(user_id)
        media_type = await client.db.get_media_type(user_id)
        spoiler = await client.db.get_spoiler(user_id)
        
        # Upload video with progress
        await status.edit_text(
            f"**▸ File:** `{file_name[:35]}...`\n\n"
            f"**▸ Status:** `Uploading`\n"
            f"[░░░░░░░░░░░░░░░░░░░░] 0.00%\n\n"
            f"**▸ Preparing upload...**"
        )
        
        upload_start = time.time()
        upload_progress = EnhancedProgress(total_size=output_size)
        
        caption = (
            f"**✅ Video Encoded Successfully!**\n\n"
            f"**▸ Quality:** {command}\n"
            f"**▸ Original Size:** {human_readable_size(file_size)}\n"
            f"**▸ Encoded Size:** {human_readable_size(output_size)}\n"
            f"**▸ Compression:** {((file_size - output_size) / file_size * 100):.1f}%\n"
            f"**▸ Codec:** {codec.upper()}\n"
            f"**▸ Preset:** {preset}\n\n"
            f"**⏱ Time Breakdown:**\n"
            f"**▸ Download:** {format_time(download_time)}\n"
            f"**▸ Encoding:** {format_time(encoding_time)}\n"
            f"**▸ Total:** {format_time(time.time() - start_time)}"
        )
        
        if media_type == "document":
            await message.reply_document(
                document=output_path,
                caption=caption,
                thumb=thumbnail,
                progress=lambda c, t: upload_progress.upload_progress(c, t, status, file_name)
            )
        else:
            await message.reply_video(
                video=output_path,
                caption=caption,
                thumb=thumbnail,
                has_spoiler=spoiler,
                supports_streaming=True,
                progress=lambda c, t: upload_progress.upload_progress(c, t, status, file_name)
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
