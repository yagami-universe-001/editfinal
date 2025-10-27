import os
import logging
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import Config
from database import Database
from handlers import start, help_command, admin, media, settings, encode, subtitle, extract, merge

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Bot(Client):
    def __init__(self):
        super().__init__(
            name="VideoEncoderBot",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN,
            workers=Config.WORKERS,
            plugins={"root": "plugins"},
            sleep_threshold=15
        )
        self.db = Database(Config.DB_URI)

    async def start(self):
        await super().start()
        me = await self.get_me()
        self.username = me.username
        logger.info(f"{me.first_name} Started ✅")
        
    async def stop(self, *args):
        await super().stop()
        logger.info("Bot Stopped 🛑")

# Initialize bot
bot = Bot()

# Register handlers
@bot.on_message(filters.command("start") & (filters.private | filters.group))
async def start_handler(client, message):
    await start.start_command(client, message)

@bot.on_message(filters.command("help") & (filters.private | filters.group))
async def help_handler(client, message):
    await help_command.help_command(client, message)

# Thumbnail commands
@bot.on_message(filters.command("setthumb") & filters.private)
async def setthumb_handler(client, message):
    await settings.set_thumbnail(client, message)

@bot.on_message(filters.command("getthumb") & filters.private)
async def getthumb_handler(client, message):
    await settings.get_thumbnail(client, message)

@bot.on_message(filters.command("delthumb") & filters.private)
async def delthumb_handler(client, message):
    await settings.delete_thumbnail(client, message)

# Watermark commands
@bot.on_message(filters.command("setwatermark") & filters.private)
async def setwatermark_handler(client, message):
    await settings.set_watermark(client, message)

@bot.on_message(filters.command("getwatermark") & filters.private)
async def getwatermark_handler(client, message):
    await settings.get_watermark(client, message)

@bot.on_message(filters.command("addwatermark") & filters.private)
async def addwatermark_handler(client, message):
    await media.add_watermark(client, message)

# Media settings
@bot.on_message(filters.command("setmedia") & filters.private)
async def setmedia_handler(client, message):
    await settings.set_media_type(client, message)

@bot.on_message(filters.command("spoiler") & filters.private)
async def spoiler_handler(client, message):
    await settings.toggle_spoiler(client, message)

@bot.on_message(filters.command("upload") & filters.private)
async def upload_handler(client, message):
    await settings.set_upload_mode(client, message)

# Encoding commands
@bot.on_message(filters.command(["144p", "240p", "360p", "480p", "720p", "1080p", "2160p"]) & (filters.private | filters.group))
async def encode_handler(client, message):
    await encode.encode_video(client, message)

@bot.on_message(filters.command("all") & (filters.private | filters.group))
async def encode_all_handler(client, message):
    await encode.encode_all_qualities(client, message)

@bot.on_message(filters.command("compress") & (filters.private | filters.group))
async def compress_handler(client, message):
    await encode.compress_video(client, message)

# Video editing commands
@bot.on_message(filters.command("cut") & filters.private)
async def cut_handler(client, message):
    await media.trim_video(client, message)

@bot.on_message(filters.command("crop") & filters.private)
async def crop_handler(client, message):
    await media.crop_video(client, message)

@bot.on_message(filters.command("merge") & filters.private)
async def merge_handler(client, message):
    await merge.merge_videos(client, message)

# Subtitle commands
@bot.on_message(filters.command("sub") & filters.private)
async def soft_sub_handler(client, message):
    await subtitle.add_soft_subtitle(client, message)

@bot.on_message(filters.command("hsub") & filters.private)
async def hard_sub_handler(client, message):
    await subtitle.add_hard_subtitle(client, message)

@bot.on_message(filters.command("rsub") & filters.private)
async def remove_sub_handler(client, message):
    await subtitle.remove_subtitle(client, message)

@bot.on_message(filters.command("extract_sub") & filters.private)
async def extract_sub_handler(client, message):
    await extract.extract_subtitle(client, message)

# Audio commands
@bot.on_message(filters.command("addaudio") & filters.private)
async def add_audio_handler(client, message):
    await media.add_audio(client, message)

@bot.on_message(filters.command("remaudio") & filters.private)
async def remove_audio_handler(client, message):
    await media.remove_audio(client, message)

@bot.on_message(filters.command("extract_audio") & filters.private)
async def extract_audio_handler(client, message):
    await extract.extract_audio(client, message)

# Extract commands
@bot.on_message(filters.command("extract_thumb") & filters.private)
async def extract_thumb_handler(client, message):
    await extract.extract_thumbnail(client, message)

@bot.on_message(filters.command("mediainfo") & filters.private)
async def mediainfo_handler(client, message):
    await media.get_media_info(client, message)

# Admin commands
@bot.on_message(filters.command("restart") & filters.private & filters.user(Config.ADMINS))
async def restart_handler(client, message):
    await admin.restart_bot(client, message)

@bot.on_message(filters.command("queue") & filters.private & filters.user(Config.ADMINS))
async def queue_handler(client, message):
    await admin.check_queue(client, message)

@bot.on_message(filters.command("clear") & filters.private & filters.user(Config.ADMINS))
async def clear_handler(client, message):
    await admin.clear_queue(client, message)

@bot.on_message(filters.command("audio") & filters.private & filters.user(Config.ADMINS))
async def audio_bitrate_handler(client, message):
    await admin.set_audio_bitrate(client, message)

@bot.on_message(filters.command("codec") & filters.private & filters.user(Config.ADMINS))
async def codec_handler(client, message):
    await admin.set_codec(client, message)

@bot.on_message(filters.command("preset") & filters.private & filters.user(Config.ADMINS))
async def preset_handler(client, message):
    await admin.set_preset(client, message)

@bot.on_message(filters.command("crf") & filters.private & filters.user(Config.ADMINS))
async def crf_handler(client, message):
    await admin.set_crf(client, message)

# Force subscribe commands
@bot.on_message(filters.command("addchnl") & filters.private & filters.user(Config.ADMINS))
async def add_channel_handler(client, message):
    await admin.add_fsub_channel(client, message)

@bot.on_message(filters.command("delchnl") & filters.private & filters.user(Config.ADMINS))
async def del_channel_handler(client, message):
    await admin.delete_fsub_channel(client, message)

@bot.on_message(filters.command("listchnl") & filters.private & filters.user(Config.ADMINS))
async def list_channel_handler(client, message):
    await admin.list_fsub_channels(client, message)

@bot.on_message(filters.command("fsub_mode") & filters.private & filters.user(Config.ADMINS))
async def fsub_mode_handler(client, message):
    await admin.fsub_mode(client, message)

# Shortener commands
@bot.on_message(filters.command("shortner") & filters.private & filters.user(Config.ADMINS))
async def shortner_handler(client, message):
    await admin.view_shortener(client, message)

@bot.on_message(filters.command("shortlink1") & filters.private & filters.user(Config.ADMINS))
async def shortlink1_handler(client, message):
    await admin.set_shortlink1(client, message)

@bot.on_message(filters.command("tutorial1") & filters.private & filters.user(Config.ADMINS))
async def tutorial1_handler(client, message):
    await admin.set_tutorial1(client, message)

@bot.on_message(filters.command("shortlink2") & filters.private & filters.user(Config.ADMINS))
async def shortlink2_handler(client, message):
    await admin.set_shortlink2(client, message)

@bot.on_message(filters.command("tutorial2") & filters.private & filters.user(Config.ADMINS))
async def tutorial2_handler(client, message):
    await admin.set_tutorial2(client, message)

@bot.on_message(filters.command("shortner1") & filters.private & filters.user(Config.ADMINS))
async def shortner1_config_handler(client, message):
    await admin.view_shortener1_config(client, message)

@bot.on_message(filters.command("shortner2") & filters.private & filters.user(Config.ADMINS))
async def shortner2_config_handler(client, message):
    await admin.view_shortener2_config(client, message)

# Premium commands
@bot.on_message(filters.command("addpaid") & filters.private & filters.user(Config.ADMINS))
async def add_premium_handler(client, message):
    await admin.add_premium_user(client, message)

@bot.on_message(filters.command("listpaid") & filters.private & filters.user(Config.ADMINS))
async def list_premium_handler(client, message):
    await admin.list_premium_users(client, message)

@bot.on_message(filters.command("rempaid") & filters.private & filters.user(Config.ADMINS))
async def remove_premium_handler(client, message):
    await admin.remove_premium_user(client, message)

@bot.on_message(filters.command("update") & filters.private & filters.user(Config.ADMINS))
async def update_handler(client, message):
    await admin.git_update(client, message)

# Media handler
@bot.on_message((filters.video | filters.document) & (filters.private | filters.group))
async def media_handler(client, message):
    await media.handle_media(client, message)

# Callback query handler
@bot.on_callback_query()
async def callback_handler(client, callback_query):
    from handlers.callbacks import handle_callback
    await handle_callback(client, callback_query)

if __name__ == "__main__":
    bot.run()
