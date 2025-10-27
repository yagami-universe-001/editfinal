from pyrogram import Client
from pyrogram.types import Message
from utils.ffmpeg import FFmpegEncoder
from utils.helpers import human_readable_size, format_time
import logging
import os
import time

logger = logging.getLogger(__name__)

# Store video queue for merging
merge_queue = {}

async def merge_videos(client: Client, message: Message):
    """Merge multiple videos into one"""
    user_id = message.from_user.id
    
    if not message.reply_to_message:
        await message.reply_text(
            "🔗 **Merge Multiple Videos**\n\n"
            "**How to use:**\n"
            "1. Send multiple videos (2 or more)\n"
            "2. Use /merge command\n"
            "3. Videos will be merged in order sent\n\n"
            "**Notes:**\n"
            "• All videos must have same resolution\n"
            "• All videos must have same codec\n"
            "• Maximum 10 videos can be merged\n"
            "• Videos are merged without re-encoding (fast)\n\n"
            "**Example:**\n"
            "Send video1.mp4, video2.mp4, video3.mp4\n"
            "Then use /merge"
        )
        return
    
    # Check if user has videos in queue
    if user_id not in merge_queue:
        merge_queue[user_id] = []
    
    replied = message.reply_to_message
    
    # Add video to queue
    if replied.video or replied.document:
        video_info = {
            "file_id": replied.video.file_id if replied.video else replied.document.file_id,
            "file_name": replied.video.file_name if replied.video else replied.document.file_name,
            "file_size": replied.video.file_size if replied.video else replied.document.file_size,
            "message_id": replied.id
        }
        
        merge_queue[user_id].append(video_info)
        
        queue_count = len(merge_queue[user_id])
        
        await message.reply_text(
            f"✅ **Video added to merge queue!**\n\n"
            f"**Videos in queue:** {queue_count}\n"
            f"**File:** `{video_info['file_name']}`\n"
            f"**Size:** {human_readable_size(video_info['file_size'])}\n\n"
            f"{'Send more videos or use /merge_start to begin merging!' if queue_count < 10 else '⚠️ Maximum 10 videos reached. Use /merge_start now.'}\n"
            f"Use /merge_clear to clear queue."
        )
        return
    
    await message.reply_text("❌ **Please reply to a video!**")

async def merge_start(client: Client, message: Message):
    """Start merging queued videos"""
    user_id = message.from_user.id
    
    # Check if user has videos in queue
    if user_id not in merge_queue or len(merge_queue[user_id]) < 2:
        await message.reply_text(
            "❌ **Not enough videos in queue!**\n\n"
            "You need at least 2 videos to merge.\n"
            "Reply to videos with /merge to add them to queue."
        )
        return
    
    videos = merge_queue[user_id]
    video_count = len(videos)
    
    status = await message.reply_text(
        f"🔗 **Starting merge process...**\n\n"
        f"**Videos to merge:** {video_count}\n"
        f"**This may take a while...**"
    )
    
    try:
        download_dir = f"./downloads/{user_id}/merge/"
        os.makedirs(download_dir, exist_ok=True)
        
        downloaded_files = []
        
        # Download all videos
        for idx, video in enumerate(videos, 1):
            await status.edit_text(
                f"📥 **Downloading videos...**\n\n"
                f"**Progress:** {idx}/{video_count}\n"
                f"**Current:** {video['file_name']}"
            )
            
            try:
                file_path = await client.download_media(
                    video['file_id'],
                    file_name=f"{download_dir}video_{idx:03d}.mp4"
                )
                downloaded_files.append(file_path)
            except Exception as e:
                logger.error(f"Error downloading video {idx}: {e}")
                await status.edit_text(f"❌ **Failed to download video {idx}!**")
                return
        
        # Merge videos
        await status.edit_text("🔄 **Merging videos...**\n\nThis may take several minutes...")
        
        output_path = f"{download_dir}merged_output.mp4"
        
        encoder = FFmpegEncoder()
        success = await encoder.merge_videos(downloaded_files, output_path)
        
        if not success:
            await status.edit_text("❌ **Failed to merge videos!**\n\nMake sure all videos have compatible formats.")
            return
        
        # Get output file info
        output_size = os.path.getsize(output_path)
        
        # Get user settings
        media_type = await client.db.get_media_type(user_id)
        thumbnail = await client.db.get_thumbnail(user_id)
        spoiler = await client.db.get_spoiler(user_id)
        
        # Upload merged video
        await status.edit_text("📤 **Uploading merged video...**")
        
        caption = (
            f"🔗 **Videos merged successfully!**\n\n"
            f"**Input videos:** {video_count}\n"
            f"**Output size:** {human_readable_size(output_size)}"
        )
        
        if media_type == "document":
            await message.reply_document(
                document=output_path,
                caption=caption,
                thumb=thumbnail
            )
        else:
            await message.reply_video(
                video=output_path,
                caption=caption,
                thumb=thumbnail,
                has_spoiler=spoiler,
                supports_streaming=True
            )
        
        await status.delete()
        
        # Clear queue
        merge_queue[user_id] = []
        
        # Cleanup
        for file in downloaded_files:
            if os.path.exists(file):
                os.remove(file)
        if os.path.exists(output_path):
            os.remove(output_path)
        
        # Remove directory
        try:
            os.rmdir(download_dir)
        except:
            pass
            
    except Exception as e:
        logger.error(f"Error merging videos: {e}")
        await status.edit_text(f"❌ **Error:** {str(e)}")

async def merge_clear(client: Client, message: Message):
    """Clear merge queue"""
    user_id = message.from_user.id
    
    if user_id in merge_queue and merge_queue[user_id]:
        count = len(merge_queue[user_id])
        merge_queue[user_id] = []
        await message.reply_text(f"✅ **Cleared {count} videos from merge queue!**")
    else:
        await message.reply_text("❌ **Merge queue is already empty!**")

async def merge_list(client: Client, message: Message):
    """List videos in merge queue"""
    user_id = message.from_user.id
    
    if user_id not in merge_queue or not merge_queue[user_id]:
        await message.reply_text(
            "📋 **Merge queue is empty!**\n\n"
            "Reply to videos with /merge to add them to queue."
        )
        return
    
    videos = merge_queue[user_id]
    total_size = sum(v['file_size'] for v in videos)
    
    text = f"📋 **Merge Queue ({len(videos)} videos)**\n\n"
    
    for idx, video in enumerate(videos, 1):
        text += f"{idx}. `{video['file_name']}`\n"
        text += f"   Size: {human_readable_size(video['file_size'])}\n\n"
    
    text += f"**Total size:** {human_readable_size(total_size)}\n\n"
    text += "Use /merge_start to merge all videos\n"
    text += "Use /merge_clear to clear queue"
    
    await message.reply_text(text)
