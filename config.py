import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Bot credentials
    API_ID = int(os.environ.get("API_ID", "0"))
    API_HASH = os.environ.get("API_HASH", "")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
    
    # Database
    DB_URI = os.environ.get("DB_URI", "mongodb://localhost:27017")
    DB_NAME = os.environ.get("DB_NAME", "video_encoder_bot")
    
    # Admin users
    ADMINS = list(set(int(x) for x in os.environ.get("ADMINS", "").split()))
    
    # Download/Upload settings
    DOWNLOAD_DIR = os.environ.get("DOWNLOAD_DIR", "./downloads")
    WORKERS = int(os.environ.get("WORKERS", "4"))
    
    # Encoding settings
    DEFAULT_PRESET = os.environ.get("DEFAULT_PRESET", "medium")
    DEFAULT_CODEC = os.environ.get("DEFAULT_CODEC", "libx264")
    DEFAULT_AUDIO_BITRATE = os.environ.get("DEFAULT_AUDIO_BITRATE", "128k")
    DEFAULT_CRF = int(os.environ.get("DEFAULT_CRF", "23"))
    
    # File size limits (in bytes)
    MAX_FILE_SIZE = int(os.environ.get("MAX_FILE_SIZE", "2147483648"))  # 2GB default
    MAX_FILE_SIZE_PREMIUM = int(os.environ.get("MAX_FILE_SIZE_PREMIUM", "4294967296"))  # 4GB
    
    # Queue settings
    MAX_CONCURRENT_TASKS = int(os.environ.get("MAX_CONCURRENT_TASKS", "2"))
    
    # Force subscribe settings
    FORCE_SUB_CHANNELS = []
    FSUB_MODE = os.environ.get("FSUB_MODE", "off")  # on/off/request
    
    # Shortener settings
    SHORTENER_API1 = os.environ.get("SHORTENER_API1", "")
    SHORTENER_URL1 = os.environ.get("SHORTENER_URL1", "")
    SHORTENER_TUTORIAL1 = os.environ.get("SHORTENER_TUTORIAL1", "")
    
    SHORTENER_API2 = os.environ.get("SHORTENER_API2", "")
    SHORTENER_URL2 = os.environ.get("SHORTENER_URL2", "")
    SHORTENER_TUTORIAL2 = os.environ.get("SHORTENER_TUTORIAL2", "")
    
    # Bot messages
    START_PIC = os.environ.get("START_PIC", "")  # URL or file_id of start picture
    
    START_MESSAGE = """
👋 **Welcome to Video Encoder Bot!**

I can help you encode, compress, and edit videos with various features:

🎬 **Video Encoding**
• Convert to different resolutions (144p - 2160p)
• Compress videos
• Change codec and quality settings

✂️ **Video Editing**
• Trim videos
• Crop videos
• Merge multiple videos
• Add/remove audio
• Add watermarks

📝 **Subtitles**
• Add soft subtitles
• Add hard subtitles
• Extract subtitles

📤 **Upload Options**
• Upload as video or document
• Set custom thumbnails
• Add watermarks

📝 **File Management**
• Rename files easily
• Custom thumbnails
• Batch operations

Use /help to see all available commands!
"""
    
    HELP_MESSAGE = """
📋 **Available Commands:**

**Basic Commands:**
/start - Start the bot
/help - Show this help message

**Settings:**
/setthumb - Set custom thumbnail
/getthumb - View saved thumbnail
/delthumb - Delete saved thumbnail
/setwatermark - Set default watermark
/getwatermark - View current watermark
/setmedia - Set preferred media type
/spoiler - Toggle spoiler mode
/upload - Set upload destination

**Encoding:**
/144p, /240p, /360p, /480p, /720p, /1080p, /2160p - Convert to specific resolution
/all - Encode in all qualities
/compress - Compress video

**Editing:**
/cut - Trim video by time
/crop - Change aspect ratio
/merge - Merge multiple videos
/addwatermark - Add logo watermark

**Audio:**
/addaudio - Add audio to video
/remaudio - Remove audio from video
/extract_audio - Extract audio

**Subtitles:**
/sub - Add soft subtitles
/hsub - Add hard subtitles
/rsub - Remove all subtitles
/extract_sub - Extract subtitles

**Information:**
/mediainfo - Get detailed media info
/extract_thumb - Extract thumbnail from video

Send me a video to get started!
"""
