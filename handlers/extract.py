from pyrogram import Client
from pyrogram.types import Message
from utils.ffmpeg import FFmpegEncoder
from utils.helpers import human_readable_size
import logging
import os

logger = logging.getLogger(__name__)

async def extract_audio(client: Client, message: Message):
    """Extract audio from video"""
    if not message.reply_to_message:
        await message.reply_text(
            "🎵 **Extract Audio from Video**\n\n"
            "Reply to a video with /extract_audio to get the audio track.\n\n"
            "**Output format:** MP3 (320kbps)\n\n"
            "**Use cases:**\n"
            "• Extract music from music videos\n"
            "• Get audio from movies\n"
            "• Convert video to audio\n"
            "• Create podcasts from video"
        )
        return
    
    replied = message.reply_to_message
    
    if not (replied.video or replied.document):
        await message.reply_text("❌ **Please reply to a video!**")
        return
    
    user_id = message.from_user.id
    status = await message.reply_text("🎵 **Extracting audio...**")
    
    try:
        # Download video
        await status.edit_text("📥 **Downloading video...**")
        video_path = await replied.download(file_name=f"./downloads/{user_id}/")
        
        # Set output path
        output_path = video_path.rsplit(".", 1)[0] + ".mp3"
        
        # Extract audio using FFmpeg
        await status.edit_text("🔄 **Extracting audio track...**")
        encoder = FFmpegEncoder()
        success = await encoder.extract_audio(video_path, output_path, format="mp3")
        
        if not success:
            await status.edit_text("❌ **Failed to extract audio!**")
            return
        
        # Get file size
        file_size = os.path.getsize(output_path)
        
        # Upload audio file
        await status.edit_text("📤 **Uploading audio...**")
        await message.reply_audio(
            audio=output_path,
            caption=f"🎵 **Audio extracted successfully!**\n\n**Size:** {human_readable_size(file_size)}",
            title=os.path.basename(output_path),
            performer="Video Encoder Bot"
        )
        
        await status.delete()
        
        # Cleanup
        if os.path.exists(video_path):
            os.remove(video_path)
        if os.path.exists(output_path):
            os.remove(output_path)
            
    except Exception as e:
        logger.error(f"Error extracting audio: {e}")
        await status.edit_text(f"❌ **Error:** {str(e)}")

async def extract_subtitle(client: Client, message: Message):
    """Extract subtitle from video"""
    if not message.reply_to_message:
        await message.reply_text(
            "📝 **Extract Subtitle from Video**\n\n"
            "Reply to a video with /extract_sub to extract embedded subtitles.\n\n"
            "**Note:**\n"
            "• Only extracts soft subtitles\n"
            "• Cannot extract hard (burned-in) subtitles\n"
            "• Extracts first subtitle track\n"
            "• Output format: SRT\n\n"
            "**Tip:** If video has multiple subtitle tracks, you'll get the first one."
        )
        return
    
    replied = message.reply_to_message
    
    if not (replied.video or replied.document):
        await message.reply_text("❌ **Please reply to a video!**")
        return
    
    user_id = message.from_user.id
    status = await message.reply_text("📝 **Extracting subtitle...**")
    
    try:
        # Download video
        await status.edit_text("📥 **Downloading video...**")
        video_path = await replied.download(file_name=f"./downloads/{user_id}/")
        
        output_path = video_path.rsplit(".", 1)[0] + ".srt"
        
        # Extract subtitle using FFmpeg
        await status.edit_text("🔄 **Extracting subtitle track...**")
        encoder = FFmpegEncoder()
        success = await encoder.extract_subtitle(video_path, output_path)
        
        if not success:
            await status.edit_text(
                "❌ **No subtitles found!**\n\n"
                "The video doesn't contain any embedded subtitle tracks.\n\n"
                "**Possible reasons:**\n"
                "• Video has no subtitles\n"
                "• Subtitles are hard-coded (burned-in)\n"
                "• Subtitle format not supported"
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

async def extract_thumbnail(client: Client, message: Message):
    """Extract thumbnail/screenshot from video"""
    if not message.reply_to_message:
        await message.reply_text(
            "📸 **Extract Thumbnail from Video**\n\n"
            "Reply to a video with /extract_thumb to get a screenshot.\n\n"
            "**Default:** Screenshot at 1 second\n"
            "**Custom time:** `/extract_thumb 00:01:30`\n\n"
            "**Time format:**\n"
            "• HH:MM:SS (00:01:30)\n"
            "• MM:SS (01:30)\n"
            "• SS (90)\n\n"
            "**Examples:**\n"
            "• `/extract_thumb` - At 1 second\n"
            "• `/extract_thumb 00:05:00` - At 5 minutes\n"
            "• `/extract_thumb 30` - At 30 seconds"
        )
        return
    
    replied = message.reply_to_message
    
    if not (replied.video or replied.document):
        await message.reply_text("❌ **Please reply to a video!**")
        return
    
    # Get timestamp if provided
    timestamp = "00:00:01"  # Default
    if len(message.command) > 1:
        timestamp = message.command[1]
    
    user_id = message.from_user.id
    status = await message.reply_text(f"📸 **Extracting thumbnail at {timestamp}...**")
    
    try:
        # Download video
        await status.edit_text("📥 **Downloading video...**")
        video_path = await replied.download(file_name=f"./downloads/{user_id}/")
        
        output_path = video_path.rsplit(".", 1)[0] + "_thumb.jpg"
        
        # Extract thumbnail using FFmpeg
        await status.edit_text("🔄 **Capturing screenshot...**")
        encoder = FFmpegEncoder()
        success = await encoder.extract_thumbnail(video_path, output_path, timestamp)
        
        if not success:
            await status.edit_text(
                "❌ **Failed to extract thumbnail!**\n\n"
                "**Possible reasons:**\n"
                "• Invalid timestamp\n"
                "• Timestamp beyond video duration\n"
                "• Video format not supported"
            )
            return
        
        # Upload thumbnail
        await status.edit_text("📤 **Uploading thumbnail...**")
        file_size = os.path.getsize(output_path)
        
        await message.reply_photo(
            photo=output_path,
            caption=f"📸 **Thumbnail extracted successfully!**\n\n**Timestamp:** {timestamp}\n**Size:** {human_readable_size(file_size)}"
        )
        
        await status.delete()
        
        # Cleanup
        if os.path.exists(video_path):
            os.remove(video_path)
        if os.path.exists(output_path):
            os.remove(output_path)
            
    except Exception as e:
        logger.error(f"Error extracting thumbnail: {e}")
        await status.edit_text(f"❌ **Error:** {str(e)}")

async def extract_all(client: Client, message: Message):
    """Extract everything from video (audio, subtitles, thumbnail)"""
    if not message.reply_to_message:
        await message.reply_text(
            "📦 **Extract Everything**\n\n"
            "Reply to a video with /extract_all to extract:\n"
            "• Audio track (MP3)\n"
            "• Subtitle tracks (SRT)\n"
            "• Thumbnail (JPG)\n\n"
            "All available components will be extracted and sent to you."
        )
        return
    
    replied = message.reply_to_message
    
    if not (replied.video or replied.document):
        await message.reply_text("❌ **Please reply to a video!**")
        return
    
    user_id = message.from_user.id
    status = await message.reply_text("📦 **Extracting all components...**")
    
    try:
        # Download video
        await status.edit_text("📥 **Downloading video...**")
        video_path = await replied.download(file_name=f"./downloads/{user_id}/")
        
        encoder = FFmpegEncoder()
        base_name = video_path.rsplit(".", 1)[0]
        extracted = []
        
        # Extract audio
        await status.edit_text("🎵 **Extracting audio...**")
        audio_path = base_name + ".mp3"
        if await encoder.extract_audio(video_path, audio_path, format="mp3"):
            extracted.append(("audio", audio_path))
        
        # Extract subtitle
        await status.edit_text("📝 **Extracting subtitles...**")
        subtitle_path = base_name + ".srt"
        if await encoder.extract_subtitle(video_path, subtitle_path):
            extracted.append(("subtitle", subtitle_path))
        
        # Extract thumbnail
        await status.edit_text("📸 **Extracting thumbnail...**")
        thumb_path = base_name + "_thumb.jpg"
        if await encoder.extract_thumbnail(video_path, thumb_path, "00:00:01"):
            extracted.append(("thumbnail", thumb_path))
        
        if not extracted:
            await status.edit_text("❌ **Could not extract any components from video!**")
            return
        
        # Upload all extracted files
        await status.edit_text(f"📤 **Uploading {len(extracted)} extracted files...**")
        
        for item_type, item_path in extracted:
            try:
                if item_type == "audio":
                    await message.reply_audio(audio=item_path, caption="🎵 **Audio Track**")
                elif item_type == "subtitle":
                    await message.reply_document(document=item_path, caption="📝 **Subtitle File**")
                elif item_type == "thumbnail":
                    await message.reply_photo(photo=item_path, caption="📸 **Thumbnail**")
                
                # Remove file after upload
                if os.path.exists(item_path):
                    os.remove(item_path)
            except Exception as e:
                logger.error(f"Error uploading {item_type}: {e}")
        
        await status.edit_text(f"✅ **Extracted {len(extracted)} components successfully!**")
        
        # Cleanup
        if os.path.exists(video_path):
            os.remove(video_path)
            
    except Exception as e:
        logger.error(f"Error in extract_all: {e}")
        await status.edit_text(f"❌ **Error:** {str(e)}")
