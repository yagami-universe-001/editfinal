from pyrogram import Client
from pyrogram.types import Message
from utils.ffmpeg import FFmpegEncoder
from utils.helpers import is_subtitle_file, human_readable_size
from utils.progress import sync_progress_callback
import logging
import os
import time

logger = logging.getLogger(__name__)

# Store pending subtitle operations
pending_subtitles = {}

async def add_soft_subtitle(client: Client, message: Message):
    """Add soft subtitle to video"""
    user_id = message.from_user.id
    
    if not message.reply_to_message:
        await message.reply_text(
            "📝 **Add Soft Subtitle**\n\n"
            "**What are soft subtitles?**\n"
            "Subtitles embedded in video that can be turned on/off by the viewer.\n\n"
            "**How to use:**\n"
            "1. Reply to a video with /sub\n"
            "2. Send a subtitle file (SRT, ASS, VTT)\n"
            "3. Subtitle will be embedded in video\n\n"
            "**Supported formats:**\n"
            "• SRT (SubRip)\n"
            "• ASS (Advanced SubStation Alpha)\n"
            "• VTT (WebVTT)\n"
            "• SUB (MicroDVD)"
        )
        return
    
    replied = message.reply_to_message
    
    if not (replied.video or replied.document):
        await message.reply_text("❌ **Please reply to a video!**")
        return
    
    # Store video info for later
    pending_subtitles[user_id] = {
        'video_message': replied,
        'type': 'soft'
    }
    
    await message.reply_text(
        "📝 **Send subtitle file now**\n\n"
        "Send a subtitle file (SRT, ASS, VTT, or SUB)\n"
        "The subtitle will be embedded in the video as a soft subtitle."
    )

async def add_hard_subtitle(client: Client, message: Message):
    """Add hard subtitle (burned-in) to video"""
    user_id = message.from_user.id
    
    if not message.reply_to_message:
        await message.reply_text(
            "📝 **Add Hard Subtitle**\n\n"
            "**What are hard subtitles?**\n"
            "Subtitles permanently burned into the video. Cannot be turned off.\n\n"
            "**How to use:**\n"
            "1. Reply to a video with /hsub\n"
            "2. Send a subtitle file (SRT, ASS, VTT)\n"
            "3. Subtitle will be burned into video\n\n"
            "**Note:**\n"
            "• Cannot be removed later\n"
            "• Increases encoding time\n"
            "• Works on all players\n"
            "• Good for compatibility\n\n"
            "**Supported formats:**\n"
            "• SRT (SubRip)\n"
            "• ASS (Advanced SubStation Alpha) - with styling\n"
            "• VTT (WebVTT)\n"
            "• SUB (MicroDVD)"
        )
        return
    
    replied = message.reply_to_message
    
    if not (replied.video or replied.document):
        await message.reply_text("❌ **Please reply to a video!**")
        return
    
    # Store video info for later
    pending_subtitles[user_id] = {
        'video_message': replied,
        'type': 'hard'
    }
    
    await message.reply_text(
        "📝 **Send subtitle file now**\n\n"
        "Send a subtitle file to burn into the video.\n\n"
        "⚠️ **Note:** This process takes longer as subtitles are rendered into video."
    )

async def process_subtitle_file(client: Client, message: Message):
    """Process subtitle file sent by user"""
    user_id = message.from_user.id
    
    # Check if user has pending subtitle operation
    if user_id not in pending_subtitles:
        return
    
    # Check if message contains a document (subtitle file)
    if not message.document:
        return
    
    # Validate subtitle file
    filename = message.document.file_name
    if not is_subtitle_file(filename):
        await message.reply_text(
            "❌ **Invalid file format!**\n\n"
            "Please send a subtitle file in one of these formats:\n"
            "• SRT\n• ASS\n• VTT\n• SUB"
        )
        return
    
    pending_data = pending_subtitles[user_id]
    video_message = pending_data['video_message']
    subtitle_type = pending_data['type']
    
    status = await message.reply_text(
        f"📝 **Processing {'hard' if subtitle_type == 'hard' else 'soft'} subtitle...**"
    )
    
    try:
        download_dir = f"./downloads/{user_id}/"
        os.makedirs(download_dir, exist_ok=True)
        
        # Download video
        await status.edit_text("📥 **Downloading video...**")
        start_time = time.time()
        
        video_path = await video_message.download(
            file_name=download_dir,
            progress=sync_progress_callback,
            progress_args=(status, start_time, "Downloading video")
        )
        
        # Download subtitle
        await status.edit_text("📥 **Downloading subtitle...**")
        subtitle_path = await message.download(file_name=download_dir)
        
        # Process subtitle
        output_path = video_path.rsplit(".", 1)[0] + f"_with_sub.mp4"
        
        await status.edit_text(
            f"🔄 **Adding {'hard' if subtitle_type == 'hard' else 'soft'} subtitle...**\n\n"
            f"This may take a while..."
        )
        
        encoder = FFmpegEncoder()
        success = await encoder.add_subtitle(
            video_path,
            subtitle_path,
            output_path,
            hard_sub=(subtitle_type == 'hard')
        )
        
        if not success:
            await status.edit_text("❌ **Failed to add subtitle!**")
            return
        
        # Get output file info
        output_size = os.path.getsize(output_path)
        
        # Get user settings
        media_type = await client.db.get_media_type(user_id)
        thumbnail = await client.db.get_thumbnail(user_id)
        spoiler = await client.db.get_spoiler(user_id)
        
        # Upload result
        await status.edit_text("📤 **Uploading...**")
        
        caption = (
            f"✅ **{'Hard' if subtitle_type == 'hard' else 'Soft'} subtitle added!**\n\n"
            f"**Size:** {human_readable_size(output_size)}\n"
            f"**Subtitle:** {filename}"
        )
        
        start_time = time.time()
        
        if media_type == "document":
            await message.reply_document(
                document=output_path,
                caption=caption,
                thumb=thumbnail,
                progress=sync_progress_callback,
                progress_args=(status, start_time, "Uploading")
            )
        else:
            await message.reply_video(
                video=output_path,
                caption=caption,
                thumb=thumbnail,
                has_spoiler=spoiler,
                supports_streaming=True,
                progress=sync_progress_callback,
                progress_args=(status, start_time, "Uploading")
            )
        
        await status.delete()
        
        # Cleanup
        if os.path.exists(video_path):
            os.remove(video_path)
        if os.path.exists(subtitle_path):
            os.remove(subtitle_path)
        if os.path.exists(output_path):
            os.remove(output_path)
        
        # Clear pending operation
        del pending_subtitles[user_id]
        
        # Update stats
        await client.db.increment_encoding_count(user_id)
        
    except Exception as e:
        logger.error(f"Error processing subtitle: {e}")
        await status.edit_text(f"❌ **Error:** {str(e)}")
        
        # Clear pending operation
        if user_id in pending_subtitles:
            del pending_subtitles[user_id]

async def remove_subtitle(client: Client, message: Message):
    """Remove all subtitles from video"""
    if not message.reply_to_message:
        await message.reply_text(
            "🗑️ **Remove Subtitles**\n\n"
            "Reply to a video with /rsub to remove all embedded subtitles.\n\n"
            "**Note:**\n"
            "• Only removes soft subtitles\n"
            "• Cannot remove hard (burned-in) subtitles\n"
            "• Creates new video without subtitle tracks"
        )
        return
    
    replied = message.reply_to_message
    
    if not (replied.video or replied.document):
        await message.reply_text("❌ **Please reply to a video!**")
        return
    
    user_id = message.from_user.id
    status = await message.reply_text("🗑️ **Removing subtitles...**")
    
    try:
        download_dir = f"./downloads/{user_id}/"
        os.makedirs(download_dir, exist_ok=True)
        
        # Download video
        await status.edit_text("📥 **Downloading video...**")
        start_time = time.time()
        
        video_path = await replied.download(
            file_name=download_dir,
            progress=sync_progress_callback,
            progress_args=(status, start_time, "Downloading")
        )
        
        output_path = video_path.rsplit(".", 1)[0] + "_no_sub.mp4"
        
        # Remove subtitles using FFmpeg
        await status.edit_text("🔄 **Processing...**")
        encoder = FFmpegEncoder()
        success = await encoder.remove_subtitle(video_path, output_path)
        
        if not success:
            await status.edit_text("❌ **Failed to remove subtitles!**")
            return
        
        # Get output file info
        output_size = os.path.getsize(output_path)
        
        # Get user settings
        media_type = await client.db.get_media_type(user_id)
        thumbnail = await client.db.get_thumbnail(user_id)
        spoiler = await client.db.get_spoiler(user_id)
        
        # Upload result
        await status.edit_text("📤 **Uploading...**")
        
        caption = (
            f"✅ **Subtitles removed successfully!**\n\n"
            f"**Size:** {human_readable_size(output_size)}"
        )
        
        start_time = time.time()
        
        if media_type == "document":
            await message.reply_document(
                document=output_path,
                caption=caption,
                thumb=thumbnail,
                progress=sync_progress_callback,
                progress_args=(status, start_time, "Uploading")
            )
        else:
            await message.reply_video(
                video=output_path,
                caption=caption,
                thumb=thumbnail,
                has_spoiler=spoiler,
                supports_streaming=True,
                progress=sync_progress_callback,
                progress_args=(status, start_time, "Uploading")
            )
        
        await status.delete()
        
        # Cleanup
        if os.path.exists(video_path):
            os.remove(video_path)
        if os.path.exists(output_path):
            os.remove(output_path)
        
        # Update stats
        await client.db.increment_encoding_count(user_id)
            
    except Exception as e:
        logger.error(f"Error removing subtitles: {e}")
        await status.edit_text(f"❌ **Error:** {str(e)}")

async def extract_subtitle(client: Client, message: Message):
    """Extract subtitle from video"""
    if not message.reply_to_message:
        await message.reply_text(
            "📤 **Extract Subtitle**\n\n"
            "Reply to a video with /extract_sub to extract embedded subtitles.\n\n"
            "**Note:**\n"
            "• Only works with soft subtitles\n"
            "• Cannot extract hard (burned-in) subtitles\n"
            "• Extracts first subtitle track\n"
            "• Output format: SRT"
        )
        return
    
    replied = message.reply_to_message
    
    if not (replied.video or replied.document):
        await message.reply_text("❌ **Please reply to a video!**")
        return
    
    user_id = message.from_user.id
    status = await message.reply_text("📤 **Extracting subtitle...**")
    
    try:
        download_dir = f"./downloads/{user_id}/"
        os.makedirs(download_dir, exist_ok=True)
        
        # Download video
        await status.edit_text("📥 **Downloading video...**")
        start_time = time.time()
        
        video_path = await replied.download(
            file_name=download_dir,
            progress=sync_progress_callback,
            progress_args=(status, start_time, "Downloading")
        )
        
        output_path = video_path.rsplit(".", 1)[0] + ".srt"
        
        # Extract subtitle using FFmpeg
        await status.edit_text("🔄 **Extracting...**")
        encoder = FFmpegEncoder()
        success = await encoder.extract_subtitle(video_path, output_path)
        
        if not success:
            await status.edit_text(
                "❌ **No subtitles found in video!**\n\n"
                "The video doesn't contain any embedded subtitle tracks."
            )
            
            # Cleanup
            if os.path.exists(video_path):
                os.remove(video_path)
            return
        
        # Upload subtitle file
        await status.edit_text("📤 **Uploading subtitle...**")
        file_size = os.path.getsize(output_path)
        
        await message.reply_document(
            document=output_path,
            caption=f"📝 **Subtitle extracted successfully!**\n\n**Size:** {human_readable_size(file_size)}"
        )
        
        await status.delete()
        
        # Cleanup
        if os.path.exists(video_path):
            os.remove(video_path)
        if os.path.exists(output_path):
            os.remove(output_path)
            
    except Exception as e:
        logger.error(f"Error extracting subtitle: {e}")
        await status.edit_text(f"❌ **Error:** {str(e)}")
