from pyrogram import Client
from pyrogram.types import Message
from utils.helpers import human_readable_size, clean_filename
from utils.enhanced_progress import EnhancedProgress
import logging
import os
import time

logger = logging.getLogger(__name__)

# Store pending rename operations
pending_renames = {}

async def rename_file(client: Client, message: Message):
    """Rename video file"""
    user_id = message.from_user.id
    
    # Check if command has new name
    if len(message.command) < 2:
        await message.reply_text(
            "📝 **Rename File**\n\n"
            "**Usage:** `/rename <new_name>`\n\n"
            "**Examples:**\n"
            "• `/rename My Video.mp4`\n"
            "• `/rename Movie [1080p] [x264].mkv`\n"
            "• `/rename Episode 01.mp4`\n\n"
            "**Note:** Reply to a video with this command\n"
            "Extension will be preserved automatically."
        )
        return
    
    # Check if replied to a video
    if not message.reply_to_message:
        await message.reply_text(
            "❌ **Please reply to a video file!**\n\n"
            "Reply to the video you want to rename with:\n"
            "`/rename <new_name>`"
        )
        return
    
    replied = message.reply_to_message
    
    if not (replied.video or replied.document):
        await message.reply_text("❌ **Please reply to a video or document!**")
        return
    
    # Get new filename
    new_name = message.text.split(None, 1)[1]
    new_name = clean_filename(new_name)
    
    # Get original file info
    if replied.video:
        file = replied.video
        original_name = file.file_name or "video.mp4"
    else:
        file = replied.document
        original_name = file.file_name or "document.mp4"
    
    # Preserve original extension if not provided
    if not any(new_name.lower().endswith(ext) for ext in ['.mp4', '.mkv', '.avi', '.mov', '.webm']):
        original_ext = os.path.splitext(original_name)[1]
        new_name += original_ext
    
    file_size = file.file_size
    
    # Check file size limits
    is_premium = await client.db.is_premium_user(user_id)
    max_size = 4294967296 if is_premium else 2147483648  # 4GB/2GB
    
    if file_size > max_size:
        await message.reply_text(
            f"❌ **File too large!**\n\n"
            f"**Limit:** {human_readable_size(max_size)}\n"
            f"**File:** {human_readable_size(file_size)}"
        )
        return
    
    status = await message.reply_text(
        f"📝 **Renaming File...**\n\n"
        f"**Old Name:** `{original_name}`\n"
        f"**New Name:** `{new_name}`\n"
        f"**Size:** {human_readable_size(file_size)}\n\n"
        f"**Status:** Downloading..."
    )
    
    try:
        download_dir = f"./downloads/{user_id}/"
        os.makedirs(download_dir, exist_ok=True)
        
        # Download with progress
        start_time = time.time()
        progress_tracker = EnhancedProgress(total_size=file_size)
        
        old_path = await replied.download(
            file_name=download_dir,
            progress=lambda c, t: progress_tracker.download_progress(c, t, status, "Downloading")
        )
        
        # Rename file
        new_path = os.path.join(download_dir, new_name)
        os.rename(old_path, new_path)
        
        # Get user settings
        thumbnail = await client.db.get_thumbnail(user_id)
        media_type = await client.db.get_media_type(user_id)
        spoiler = await client.db.get_spoiler(user_id)
        
        # Upload with new name
        await status.edit_text(
            f"📝 **Uploading...**\n\n"
            f"**Name:** `{new_name}`\n"
            f"**Size:** {human_readable_size(file_size)}"
        )
        
        upload_progress = EnhancedProgress(total_size=file_size)
        
        caption = (
            f"✅ **File Renamed Successfully!**\n\n"
            f"**Old Name:** `{original_name}`\n"
            f"**New Name:** `{new_name}`\n"
            f"**Size:** {human_readable_size(file_size)}"
        )
        
        if media_type == "document" or replied.document:
            await message.reply_document(
                document=new_path,
                caption=caption,
                thumb=thumbnail,
                progress=lambda c, t: upload_progress.upload_progress(c, t, status, new_name)
            )
        else:
            await message.reply_video(
                video=new_path,
                caption=caption,
                thumb=thumbnail,
                has_spoiler=spoiler,
                supports_streaming=True,
                progress=lambda c, t: upload_progress.upload_progress(c, t, status, new_name)
            )
        
        await status.delete()
        
        # Cleanup
        if os.path.exists(new_path):
            os.remove(new_path)
            
    except Exception as e:
        logger.error(f"Rename error: {e}")
        await status.edit_text(f"❌ **Error:** {str(e)}")

async def auto_rename(client: Client, message: Message):
    """Auto-rename with pattern"""
    user_id = message.from_user.id
    
    await message.reply_text(
        "🔄 **Auto Rename**\n\n"
        "**Available patterns:**\n"
        "• `{name}` - Original name\n"
        "• `{quality}` - Video quality (480p, 720p, etc.)\n"
        "• `{codec}` - Video codec (H264, HEVC, etc.)\n"
        "• `{size}` - File size\n"
        "• `{date}` - Current date\n\n"
        "**Example:**\n"
        "`/autorename {name} [{quality}] [{codec}]`\n\n"
        "**Coming soon!**"
    )

async def batch_rename(client: Client, message: Message):
    """Batch rename multiple files"""
    await message.reply_text(
        "📦 **Batch Rename**\n\n"
        "Rename multiple files at once.\n\n"
        "**Usage:**\n"
        "1. Forward multiple videos\n"
        "2. Use `/batchrename <pattern>`\n\n"
        "**Coming soon!**"
    )
