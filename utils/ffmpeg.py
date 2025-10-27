import asyncio
import time
from datetime import timedelta

def format_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

def create_progress_bar(percentage, length=20):
    filled = int(length * percentage / 100)
    bar = '█' * filled + '░' * (length - filled)
    return f"[{bar}]"

async def encode_video_fast(input_file, output_file, quality, progress_msg, file_info=None):
    """Ultra-fast encoding with real-time progress"""
    
    ENCODING_PRESETS = {
        "144p": {"width": 256, "height": 144, "bitrate": "200k"},
        "240p": {"width": 426, "height": 240, "bitrate": "400k"},
        "360p": {"width": 640, "height": 360, "bitrate": "800k"},
        "480p": {"width": 854, "height": 480, "bitrate": "1200k"},
        "720p": {"width": 1280, "height": 720, "bitrate": "2500k"},
        "1080p": {"width": 1920, "height": 1080, "bitrate": "5000k"},
    }
    
    preset = ENCODING_PRESETS.get(quality, ENCODING_PRESETS["480p"])
    
    # Get duration
    duration_cmd = ['ffprobe', '-v', 'error', '-show_entries', 
                    'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', 
                    input_file]
    
    proc = await asyncio.create_subprocess_exec(
        *duration_cmd,
        stdout=asyncio.subprocess.PIPE
    )
    stdout, _ = await proc.communicate()
    duration = float(stdout.decode().strip())
    
    # FAST encoding command
    cmd = [
        'ffmpeg', '-i', input_file,
        '-c:v', 'libx265',
        '-preset', 'ultrafast',  # ⚡ FASTEST PRESET
        '-crf', '23',
        '-vf', f'scale={preset["width"]}:{preset["height"]}',
        '-b:v', preset['bitrate'],
        '-c:a', 'aac',
        '-b:a', '128k',
        '-max_muxing_queue_size', '9999',
        '-progress', 'pipe:1',
        '-y',
        output_file
    ]
    
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    start_time = time.time()
    last_update = 0
    
    async for line in process.stdout:
        line = line.decode().strip()
        
        if line.startswith('out_time_ms='):
            current_time = int(line.split('=')[1]) / 1000000
            percentage = (current_time / duration) * 100
            elapsed = time.time() - start_time
            speed = current_time / elapsed if elapsed > 0 else 0
            eta = (duration - current_time) / speed if speed > 0 else 0
            
            if time.time() - last_update >= 2:
                last_update = time.time()
                
                file_name = file_info.get('name', 'Video') if file_info else 'Video'
                
                progress_text = f"""
▶ **Video Name:** `{file_name}`

▶ **Status:** *Encoding*

{create_progress_bar(percentage)} {percentage:.2f}%

▶ **Processed:** {format_time(current_time)} / {format_time(duration)}
▶ **Speed:** {speed:.2f}x
▶ **Time Took:** {format_time(elapsed)}
▶ **Time Left:** {format_time(eta)}

▶ **Quality:** {quality.upper()}
                """
                
                try:
                    await progress_msg.edit(progress_text)
                except:
                    pass
    
    await process.wait()
    return process.returncode == 0
