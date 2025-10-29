from pyrogram import Client
from pyrogram.types import Message
import os
import zipfile
import tarfile
try:
    import rarfile
    RAR_AVAILABLE = True
except ImportError:
    RAR_AVAILABLE = False
try:
    import py7zr
    SEVENZ_AVAILABLE = True
except ImportError:
    SEVENZ_AVAILABLE = False

from utils.helpers import human_readable_size
from utils.enhanced_progress import EnhancedProgress
import logging

logger = logging.getLogger(__name__)

async def unzip_file(client: Client, message: Message):
    """Unzip/Extract archive files"""
    if not message.reply_to_message:
        supported = ["• ZIP (.zip)", "• TAR (.tar, .tar.gz, .tgz)"]
        if RAR_AVAILABLE:
            supported.append("• RAR (.rar)")
        if SEVENZ_AVAILABLE:
            supported.append("• 7Z (.7z)")
            
        await message.reply_text(
            "📦 **Unzip/Extract Files**\n\n"
            "**Supported formats:**\n" + "\n".join(supported) + "\n\n"
            "**Usage:**\n"
            "Reply to a compressed file with `/unzip`\n\n"
            "**Example:**\n"
            "Reply to file.zip with `/unzip`"
        )
        return
    
    replied = message.reply_to_message
    
    if not replied.document:
        await message.reply_text("❌ **Please reply to a compressed file!**")
        return
    
    file_name = replied.document.file_name
    file_size = replied.document.file_size
    
    # Check file extension
    supported_formats = ['.zip', '.tar', '.tar.gz', '.tgz']
    if RAR_AVAILABLE:
        supported_formats.append('.rar')
    if SEVENZ_AVAILABLE:
        supported_formats.append('.7z')
        
    if not any(file_name.lower().endswith(ext) for ext in supported_formats):
        await message.reply_text(
            f"❌ **Unsupported format!**\n\n"
            f"**File:** `{file_name}`\n\n"
            f"**Supported formats:**\n"
            + '\n'.join(f"• {ext}" for ext in supported_formats)
        )
        return
    
    # Check for RAR without library
    if file_name.lower().endswith('.rar') and not RAR_AVAILABLE:
        await message.reply_text(
            "❌ **RAR support not available!**\n\n"
            "RAR extraction is not installed on this server.\n"
            "Please use ZIP or 7Z format instead."
        )
        return
    
    # Check for 7Z without library  
    if file_name.lower().endswith('.7z') and not SEVENZ_AVAILABLE:
        await message.reply_text(
            "❌ **7Z support not available!**\n\n"
            "7Z extraction is not installed on this server.\n"
            "Please use ZIP format instead."
        )
        return
    
    user_id = message.from_user.id
    status = await message.reply_text(
        f"📦 **Extracting Archive**\n\n"
        f"**File:** `{file_name}`\n"
        f"**Size:** {human_readable_size(file_size)}\n\n"
        f"**Status:** Downloading..."
    )
    
    try:
        download_dir = f"./downloads/{user_id}/"
        extract_dir = f"./downloads/{user_id}/extracted/"
        os.makedirs(download_dir, exist_ok=True)
        os.makedirs(extract_dir, exist_ok=True)
        
        # Download file
        await status.edit_text(
            f"📦 **Extracting Archive**\n\n"
            f"**File:** `{file_name}`\n"
            f"[●●●○○○○○○○] Downloading...\n\n"
            f"**Please wait...**"
        )
        
        progress = EnhancedProgress(total_size=file_size)
        archive_path = await replied.download(
            file_name=download_dir,
            progress=lambda c, t: progress.download_progress(c, t, status, "Downloading")
        )
        
        # Extract based on format
        await status.edit_text(
            f"📦 **Extracting Archive**\n\n"
            f"**File:** `{file_name}`\n"
            f"[●●●●●●●○○○] Extracting...\n\n"
            f"**This may take a while...**"
        )
        
        extracted_files = []
        
        if file_name.lower().endswith('.zip'):
            # Extract ZIP
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
                extracted_files = zip_ref.namelist()
                
        elif file_name.lower().endswith('.rar') and RAR_AVAILABLE:
            # Extract RAR
            with rarfile.RarFile(archive_path, 'r') as rar_ref:
                rar_ref.extractall(extract_dir)
                extracted_files = rar_ref.namelist()
                
        elif file_name.lower().endswith('.7z') and SEVENZ_AVAILABLE:
            # Extract 7Z
            with py7zr.SevenZipFile(archive_path, 'r') as seven_ref:
                seven_ref.extractall(extract_dir)
                extracted_files = seven_ref.getnames()
        
        elif file_name.lower().endswith(('.tar', '.tar.gz', '.tgz')):
            # Extract TAR
            with tarfile.open(archive_path, 'r:*') as tar_ref:
                tar_ref.extractall(extract_dir)
                extracted_files = tar_ref.getnames()
        
        if not extracted_files:
            await status.edit_text("❌ **No files found in archive!**")
            return
        
        # Get extracted file sizes
        total_size = 0
        file_count = 0
        for root, dirs, files in os.walk(extract_dir):
            for file in files:
                file_path = os.path.join(root, file)
                total_size += os.path.getsize(file_path)
                file_count += 1
        
        # Send extracted files
        await status.edit_text(
            f"📦 **Extraction Complete!**\n\n"
            f"**Files extracted:** {file_count}\n"
            f"**Total size:** {human_readable_size(total_size)}\n\n"
            f"**Uploading files...**"
        )
        
        uploaded = 0
        for root, dirs, files in os.walk(extract_dir):
            for file in files:
                try:
                    file_path = os.path.join(root, file)
                    file_size = os.path.getsize(file_path)
                    
                    # Skip if file too large (2GB limit)
                    if file_size > 2147483648:
                        continue
                    
                    uploaded += 1
                    await status.edit_text(
                        f"📤 **Uploading Files**\n\n"
                        f"**Progress:** {uploaded}/{file_count}\n"
                        f"**Current:** `{file}`"
                    )
                    
                    # Get user settings
                    thumbnail = await client.db.get_thumbnail(user_id)
                    media_type = await client.db.get_media_type(user_id)
                    
                    # Download thumbnail if exists
                    thumb_path = None
                    if thumbnail:
                        try:
                            thumb_path = f"{download_dir}thumb.jpg"
                            await client.download_media(thumbnail, file_name=thumb_path)
                        except:
                            thumb_path = None
                    
                    # Check if video file
                    video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.webm', '.flv']
                    is_video = any(file.lower().endswith(ext) for ext in video_extensions)
                    
                    if is_video and media_type == "video":
                        await message.reply_video(
                            video=file_path,
                            caption=f"📁 **Extracted:** `{file}`\n**Size:** {human_readable_size(file_size)}",
                            thumb=thumb_path,
                            supports_streaming=True
                        )
                    else:
                        await message.reply_document(
                            document=file_path,
                            caption=f"📁 **Extracted:** `{file}`\n**Size:** {human_readable_size(file_size)}",
                            thumb=thumb_path
                        )
                    
                    # Cleanup uploaded file
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        
                except Exception as e:
                    logger.error(f"Error uploading {file}: {e}")
                    continue
        
        await status.edit_text(
            f"✅ **Extraction Complete!**\n\n"
            f"**Files uploaded:** {uploaded}/{file_count}\n"
            f"**Total size:** {human_readable_size(total_size)}"
        )
        
        # Cleanup
        if os.path.exists(archive_path):
            os.remove(archive_path)
        
        # Remove extract directory
        import shutil
        if os.path.exists(extract_dir):
            shutil.rmtree(extract_dir)
            
    except zipfile.BadZipFile:
        await status.edit_text("❌ **Invalid or corrupted ZIP file!**")
    except Exception as e:
        logger.error(f"Unzip error: {e}")
        await status.edit_text(f"❌ **Error:** {str(e)}")
    
    replied = message.reply_to_message
    
    if not replied.document:
        await message.reply_text("❌ **Please reply to a compressed file!**")
        return
    
    file_name = replied.document.file_name
    file_size = replied.document.file_size
    
    # Check file extension
    supported_formats = ['.zip', '.rar', '.7z', '.tar', '.tar.gz', '.tgz']
    if not any(file_name.lower().endswith(ext) for ext in supported_formats):
        await message.reply_text(
            f"❌ **Unsupported format!**\n\n"
            f"**File:** `{file_name}`\n\n"
            f"**Supported formats:**\n"
            + '\n'.join(f"• {ext}" for ext in supported_formats)
        )
        return
    
    user_id = message.from_user.id
    status = await message.reply_text(
        f"📦 **Extracting Archive**\n\n"
        f"**File:** `{file_name}`\n"
        f"**Size:** {human_readable_size(file_size)}\n\n"
        f"**Status:** Downloading..."
    )
    
    try:
        download_dir = f"./downloads/{user_id}/"
        extract_dir = f"./downloads/{user_id}/extracted/"
        os.makedirs(download_dir, exist_ok=True)
        os.makedirs(extract_dir, exist_ok=True)
        
        # Download file
        await status.edit_text(
            f"📦 **Extracting Archive**\n\n"
            f"**File:** `{file_name}`\n"
            f"[●●●○○○○○○○] Downloading...\n\n"
            f"**Please wait...**"
        )
        
        progress = EnhancedProgress(total_size=file_size)
        archive_path = await replied.download(
            file_name=download_dir,
            progress=lambda c, t: progress.download_progress(c, t, status, "Downloading")
        )
        
        # Extract based on format
        await status.edit_text(
            f"📦 **Extracting Archive**\n\n"
            f"**File:** `{file_name}`\n"
            f"[●●●●●●●○○○] Extracting...\n\n"
            f"**This may take a while...**"
        )
        
        extracted_files = []
        
        if file_name.lower().endswith('.zip'):
            # Extract ZIP
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
                extracted_files = zip_ref.namelist()
                
        elif file_name.lower().endswith('.rar'):
            # Extract RAR
            with rarfile.RarFile(archive_path, 'r') as rar_ref:
                rar_ref.extractall(extract_dir)
                extracted_files = rar_ref.namelist()
                
        elif file_name.lower().endswith('.7z'):
            # Extract 7Z
            with py7zr.SevenZipFile(archive_path, 'r') as seven_ref:
                seven_ref.extractall(extract_dir)
                extracted_files = seven_ref.getnames()
        
        elif file_name.lower().endswith(('.tar', '.tar.gz', '.tgz')):
            # Extract TAR
            import tarfile
            with tarfile.open(archive_path, 'r:*') as tar_ref:
                tar_ref.extractall(extract_dir)
                extracted_files = tar_ref.getnames()
        
        if not extracted_files:
            await status.edit_text("❌ **No files found in archive!**")
            return
        
        # Get extracted file sizes
        total_size = 0
        file_count = 0
        for root, dirs, files in os.walk(extract_dir):
            for file in files:
                file_path = os.path.join(root, file)
                total_size += os.path.getsize(file_path)
                file_count += 1
        
        # Send extracted files
        await status.edit_text(
            f"📦 **Extraction Complete!**\n\n"
            f"**Files extracted:** {file_count}\n"
            f"**Total size:** {human_readable_size(total_size)}\n\n"
            f"**Uploading files...**"
        )
        
        uploaded = 0
        for root, dirs, files in os.walk(extract_dir):
            for file in files:
                try:
                    file_path = os.path.join(root, file)
                    file_size = os.path.getsize(file_path)
                    
                    # Skip if file too large (2GB limit)
                    if file_size > 2147483648:
                        continue
                    
                    uploaded += 1
                    await status.edit_text(
                        f"📤 **Uploading Files**\n\n"
                        f"**Progress:** {uploaded}/{file_count}\n"
                        f"**Current:** `{file}`"
                    )
                    
                    # Get user settings
                    thumbnail = await client.db.get_thumbnail(user_id)
                    media_type = await client.db.get_media_type(user_id)
                    
                    # Download thumbnail if exists
                    thumb_path = None
                    if thumbnail:
                        try:
                            thumb_path = f"{download_dir}thumb.jpg"
                            await client.download_media(thumbnail, file_name=thumb_path)
                        except:
                            thumb_path = None
                    
                    # Check if video file
                    video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.webm', '.flv']
                    is_video = any(file.lower().endswith(ext) for ext in video_extensions)
                    
                    if is_video and media_type == "video":
                        await message.reply_video(
                            video=file_path,
                            caption=f"📁 **Extracted:** `{file}`\n**Size:** {human_readable_size(file_size)}",
                            thumb=thumb_path,
                            supports_streaming=True
                        )
                    else:
                        await message.reply_document(
                            document=file_path,
                            caption=f"📁 **Extracted:** `{file}`\n**Size:** {human_readable_size(file_size)}",
                            thumb=thumb_path
                        )
                    
                    # Cleanup uploaded file
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        
                except Exception as e:
                    logger.error(f"Error uploading {file}: {e}")
                    continue
        
        await status.edit_text(
            f"✅ **Extraction Complete!**\n\n"
            f"**Files uploaded:** {uploaded}/{file_count}\n"
            f"**Total size:** {human_readable_size(total_size)}"
        )
        
        # Cleanup
        if os.path.exists(archive_path):
            os.remove(archive_path)
        
        # Remove extract directory
        import shutil
        if os.path.exists(extract_dir):
            shutil.rmtree(extract_dir)
            
    except zipfile.BadZipFile:
        await status.edit_text("❌ **Invalid or corrupted ZIP file!**")
    except rarfile.BadRarFile:
        await status.edit_text("❌ **Invalid or corrupted RAR file!**")
    except Exception as e:
        logger.error(f"Unzip error: {e}")
        await status.edit_text(f"❌ **Error:** {str(e)}")
