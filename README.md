# Telegram Video Encoder Bot

A powerful and feature-rich Telegram bot for video encoding, compression, and editing with advanced features like watermarking, subtitle management, and multi-quality encoding.

## ✨ Features

### 🎬 Video Encoding
- Convert videos to multiple resolutions (144p to 2160p)
- Batch encode in all qualities at once
- Compress videos with customizable settings
- Support for multiple codecs (H.264, H.265, VP9)
- Adjustable CRF and preset settings

### ✂️ Video Editing
- Trim videos by time range
- Crop videos with custom aspect ratios
- Merge multiple videos
- Add/remove audio tracks
- Add logo watermarks

### 📝 Subtitle Management
- Add soft subtitles (SRT, ASS, VTT)
- Add hard-coded subtitles
- Extract subtitles from videos
- Remove all subtitles

### 📤 Upload Options
- Upload as video or document
- Custom thumbnail support
- Spoiler mode
- Flexible upload destinations

### 🔐 Premium Features
- Higher file size limits
- Priority queue processing
- Advanced encoding options

### 👥 Admin Features
- User management
- Queue management
- Force subscribe channels
- URL shortener integration
- Encoding settings control
- Premium user management

## 📋 Requirements

- Python 3.9+
- FFmpeg 4.4+
- MongoDB 4.4+
- Telegram Bot API credentials

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/telegram-video-encoder-bot.git
cd telegram-video-encoder-bot
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Install FFmpeg

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
Download from [ffmpeg.org](https://ffmpeg.org/download.html)

### 4. Setup MongoDB

**Using Docker:**
```bash
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

**Or install locally:**
- [MongoDB Installation Guide](https://docs.mongodb.com/manual/installation/)

### 5. Configure the bot

Create a `.env` file in the root directory:

```env
# Bot Configuration
API_ID=your_api_id
API_HASH=your_api_hash
BOT_TOKEN=your_bot_token

# Database
DB_URI=mongodb://localhost:27017
DB_NAME=video_encoder_bot

# Admin Users (comma-separated user IDs)
ADMINS=123456789,987654321

# Directories
DOWNLOAD_DIR=./downloads

# Workers
WORKERS=4

# Encoding Settings
DEFAULT_PRESET=medium
DEFAULT_CODEC=libx264
DEFAULT_AUDIO_BITRATE=128k
DEFAULT_CRF=23

# File Size Limits (in bytes)
MAX_FILE_SIZE=2147483648
MAX_FILE_SIZE_PREMIUM=4294967296

# Queue Settings
MAX_CONCURRENT_TASKS=2

# Force Subscribe (optional)
FSUB_MODE=off

# Shortener Settings (optional)
SHORTENER_API1=
SHORTENER_URL1=
SHORTENER_TUTORIAL1=

SHORTENER_API2=
SHORTENER_URL2=
SHORTENER_TUTORIAL2=
```

### 6. Get Telegram API Credentials

1. Go to [my.telegram.org](https://my.telegram.org)
2. Log in with your phone number
3. Click on "API Development Tools"
4. Create a new application
5. Copy `API_ID` and `API_HASH`

### 7. Create a Telegram Bot

1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot` and follow instructions
3. Copy the bot token
4. Set your bot token in `.env` file

## 🎯 Usage

### Starting the Bot

```bash
python bot.py
```

### User Commands

**Basic Commands:**
- `/start` - Start the bot and get welcome message
- `/help` - Show all available commands

**Settings:**
- `/setthumb` - Set a custom thumbnail
- `/getthumb` - View saved thumbnail
- `/delthumb` - Delete saved thumbnail
- `/setwatermark` - Set default watermark text
- `/getwatermark` - Get current watermark
- `/addwatermark` - Add logo watermark to video
- `/setmedia` - Set preferred media type (video/document)
- `/spoiler` - Enable/disable spoiler mode
- `/upload` - Set upload destination

**Encoding Commands:**
- `/144p`, `/240p`, `/360p`, `/480p`, `/720p`, `/1080p`, `/2160p` - Convert to specific resolution
- `/all` - Encode in all qualities at once
- `/compress` - Compress video

**Video Editing:**
- `/cut` - Trim video by time (e.g., `/cut 00:00:10 00:01:30`)
- `/crop` - Change video aspect ratio
- `/merge` - Merge multiple videos

**Audio Management:**
- `/addaudio` - Add audio track to video
- `/remaudio` - Remove audio from video
- `/extract_audio` - Extract audio track

**Subtitle Management:**
- `/sub` - Add soft subtitles
- `/hsub` - Add hard-coded subtitles
- `/rsub` - Remove all subtitles
- `/extract_sub` - Extract subtitles from video

**Information:**
- `/mediainfo` - Get detailed media information
- `/extract_thumb` - Extract thumbnail from video

### Admin Commands

- `/restart` - Restart the bot
- `/queue` - Check total queue
- `/clear` - Clear all queue tasks
- `/audio` - Set audio bitrate
- `/codec` - Set video codec (libx264/libx265/libvpx-vp9)
- `/preset` - Change encoding preset (ultrafast/fast/medium/slow/veryslow)
- `/crf` - Set CRF value (0-51, lower = better quality)
- `/addchnl` - Add force subscribe channel
- `/delchnl` - Delete force subscribe channel
- `/listchnl` - List all force subscribe channels
- `/fsub_mode` - Change force subscribe mode (on/off/request)
- `/shortner` - View shortener settings
- `/shortlink1` - Set shortlink 1
- `/tutorial1` - Set tutorial for shortener 1
- `/shortlink2` - Set shortlink 2
- `/tutorial2` - Set tutorial for shortener 2
- `/shortner1` - View shortener 1 config
- `/shortner2` - View shortener 2 config
- `/addpaid` - Add premium user
- `/listpaid` - List premium users
- `/rempaid` - Remove premium user
- `/update` - Git pull latest updates

## 📁 Project Structure

```
telegram-video-encoder-bot/
├── bot.py                 # Main bot file
├── config.py             # Configuration settings
├── database.py           # Database operations
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables
├── .gitignore           # Git ignore file
├── README.md            # Documentation
│
├── handlers/            # Command handlers
│   ├── __init__.py
│   ├── start.py         # Start command
│   ├── help_command.py  # Help command
│   ├── admin.py         # Admin commands
│   ├── media.py         # Media handling
│   ├── settings.py      # User settings
│   ├── encode.py        # Encoding functions
│   ├── subtitle.py      # Subtitle operations
│   ├── extract.py       # Extract operations
│   ├── merge.py         # Merge operations
│   └── callbacks.py     # Callback handlers
│
├── utils/               # Utility functions
│   ├── __init__.py
│   ├── ffmpeg.py        # FFmpeg operations
│   ├── progress.py      # Progress tracking
│   ├── helpers.py       # Helper functions
│   └── shortener.py     # URL shortener
│
└── downloads/           # Temporary download directory
```

## 🔧 Configuration Options

### Encoding Presets
- `ultrafast` - Fastest encoding, larger file size
- `fast` - Fast encoding, good for streaming
- `medium` - Balanced (default)
- `slow` - Better compression
- `veryslow` - Best compression, slowest

### Video Codecs
- `libx264` - H.264/AVC (most compatible)
- `libx265` - H.265/HEVC (better compression)
- `libvpx-vp9` - VP9 (WebM)

### CRF Values
- `0-17` - Visually lossless
- `18-23` - High quality (default: 23)
- `24-28` - Medium quality
- `29+` - Low quality

## 🎨 Customization

### Custom Start Message

Edit `config.py` to customize the start message:

```python
START_MESSAGE = """
Your custom welcome message here
"""
```

### Custom Watermark Position

Modify `utils/ffmpeg.py` to change watermark position:

```python
# Top-left
overlay=10:10

# Top-right
overlay=W-w-10:10

# Bottom-left
overlay=10:H-h-10

# Bottom-right
overlay=W-w-10:H-h-10

# Center
overlay=(W-w)/2:(H-h)/2
```

## 🔐 Security

- Never commit `.env` file to repository
- Keep your bot token secure
- Regularly update dependencies
- Use strong MongoDB authentication in production
- Implement rate limiting for public bots

## 🐛 Troubleshooting

### FFmpeg Not Found
```bash
# Check if FFmpeg is installed
ffmpeg -version

# Add to PATH if needed
export PATH=$PATH:/path/to/ffmpeg
```

### MongoDB Connection Error
```bash
# Check if MongoDB is running
sudo systemctl status mongod

# Start MongoDB
sudo systemctl start mongod
```

### Permission Denied
```bash
# Give execute permissions
chmod +x bot.py

# Create downloads directory
mkdir -p downloads
chmod 755 downloads
```

### Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

## 📊 Performance Tips

1. **Use SSD storage** for faster encoding
2. **Adjust workers** based on CPU cores
3. **Enable hardware acceleration** if available
4. **Use Redis** for better queue management
5. **Implement caching** for frequently accessed data

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Pyrogram](https://github.com/pyrogram/pyrogram) - Telegram MTProto API framework
- [FFmpeg](https://ffmpeg.org/) - Multimedia processing
- [MongoDB](https://www.mongodb.com/) - Database

## 📧 Support

- Create an issue on GitHub
- Join our Telegram support group: [Add your group link]
- Email: [your-email@example.com]

## 🔄 Updates

Check the [CHANGELOG.md](CHANGELOG.md) for version history and updates.

## ⚠️ Disclaimer

This bot is for educational purposes. Users are responsible for complying with copyright laws and Telegram's Terms of Service.

---

Made with ❤️ by [Your Name]
