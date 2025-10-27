import os
import time
import math
from typing import Union

def human_readable_size(size_bytes: int) -> str:
    """Convert bytes to human readable format"""
    if size_bytes == 0:
        return "0B"
    
    size_names = ("B", "KB", "MB", "GB", "TB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    
    return f"{s} {size_names[i]}"

def format_time(seconds: Union[int, float]) -> str:
    """Format seconds to readable time"""
    seconds = int(seconds)
    
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    if hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"

def format_progress_bar(percentage: float, length: int = 10) -> str:
    """Create a progress bar"""
    filled = int(length * percentage / 100)
    bar = "█" * filled + "░" * (length - filled)
    return f"[{bar}] {percentage:.1f}%"

def clean_filename(filename: str) -> str:
    """Clean filename from invalid characters"""
    invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename

def get_file_extension(filename: str) -> str:
    """Get file extension"""
    return os.path.splitext(filename)[1].lower()

def is_video_file(filename: str) -> bool:
    """Check if file is a video"""
    video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.mpg', '.mpeg']
    return get_file_extension(filename) in video_extensions

def is_audio_file(filename: str) -> bool:
    """Check if file is audio"""
    audio_extensions = ['.mp3', '.aac', '.ogg', '.wav', '.flac', '.m4a', '.wma']
    return get_file_extension(filename) in audio_extensions

def is_subtitle_file(filename: str) -> bool:
    """Check if file is subtitle"""
    subtitle_extensions = ['.srt', '.ass', '.ssa', '.vtt', '.sub']
    return get_file_extension(filename) in subtitle_extensions

def parse_time(time_str: str) -> int:
    """Parse time string to seconds (HH:MM:SS or MM:SS or SS)"""
    try:
        parts = time_str.split(':')
        if len(parts) == 3:  # HH:MM:SS
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        elif len(parts) == 2:  # MM:SS
            return int(parts[0]) * 60 + int(parts[1])
        else:  # SS
            return int(parts[0])
    except:
        return 0

def format_seconds_to_time(seconds: int) -> str:
    """Format seconds to HH:MM:SS"""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

def calculate_bitrate(file_size: int, duration: float) -> str:
    """Calculate bitrate from file size and duration"""
    if duration == 0:
        return "0 kbps"
    
    bitrate_bps = (file_size * 8) / duration
    bitrate_kbps = bitrate_bps / 1000
    
    if bitrate_kbps > 1000:
        return f"{bitrate_kbps / 1000:.2f} Mbps"
    else:
        return f"{bitrate_kbps:.2f} kbps"

def get_readable_file_info(file_path: str) -> dict:
    """Get readable file information"""
    try:
        stat = os.stat(file_path)
        return {
            'size': human_readable_size(stat.st_size),
            'size_bytes': stat.st_size,
            'created': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stat.st_ctime)),
            'modified': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stat.st_mtime))
        }
    except:
        return {}

def create_directory(path: str) -> bool:
    """Create directory if not exists"""
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except:
        return False

def remove_file(file_path: str) -> bool:
    """Remove file safely"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
        return True
    except:
        return False

def get_codec_name(codec: str) -> str:
    """Get readable codec name"""
    codec_names = {
        'libx264': 'H.264/AVC',
        'libx265': 'H.265/HEVC',
        'libvpx-vp9': 'VP9',
        'libvpx': 'VP8',
        'mpeg4': 'MPEG-4',
        'h264': 'H.264',
        'hevc': 'H.265'
    }
    return codec_names.get(codec.lower(), codec.upper())

def validate_resolution(resolution: str) -> bool:
    """Validate resolution format"""
    valid_resolutions = ['144p', '240p', '360p', '480p', '720p', '1080p', '2160p', '4320p']
    return resolution.lower() in valid_resolutions

def validate_aspect_ratio(aspect_ratio: str) -> bool:
    """Validate aspect ratio"""
    valid_ratios = ['16:9', '9:16', '4:3', '3:4', '1:1', '21:9']
    return aspect_ratio in valid_ratios

def estimate_encoding_time(file_size: int, preset: str) -> str:
    """Estimate encoding time based on file size and preset"""
    # Rough estimates in seconds per MB
    preset_speeds = {
        'ultrafast': 0.5,
        'superfast': 1,
        'veryfast': 2,
        'faster': 3,
        'fast': 5,
        'medium': 8,
        'slow': 12,
        'slower': 18,
        'veryslow': 25
    }
    
    speed = preset_speeds.get(preset, 8)
    file_size_mb = file_size / (1024 * 1024)
    estimated_seconds = file_size_mb * speed
    
    return format_time(estimated_seconds)

def get_quality_description(crf: int) -> str:
    """Get quality description for CRF value"""
    if crf <= 17:
        return "Visually Lossless"
    elif crf <= 23:
        return "High Quality"
    elif crf <= 28:
        return "Medium Quality"
    elif crf <= 34:
        return "Low Quality"
    else:
        return "Very Low Quality"
