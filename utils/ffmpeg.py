import subprocess
import os
import json
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class FFmpegEncoder:
    """Handle FFmpeg operations"""
    
    @staticmethod
    async def get_video_info(file_path: str) -> Optional[Dict[str, Any]]:
        """Get video information using ffprobe"""
        try:
            cmd = [
                "ffprobe",
                "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                "-show_streams",
                file_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            return json.loads(result.stdout)
        except Exception as e:
            logger.error(f"Error getting video info: {e}")
            return None
    
    @staticmethod
    async def encode_video(
        input_file: str,
        output_file: str,
        height: int = None,
        width: int = None,
        video_bitrate: str = "1M",
        audio_bitrate: str = "128k",
        codec: str = "libx264",
        preset: str = "medium",
        crf: int = 23,
        watermark_text: str = None,
        watermark_logo: str = None
    ) -> bool:
        """Encode video with specified parameters"""
        try:
            # Build FFmpeg command
            cmd = ["ffmpeg", "-i", input_file]
            
            # Video filters
            filters = []
            
            # Scale filter
            if height:
                filters.append(f"scale=-2:{height}")
            elif width:
                filters.append(f"scale={width}:-2")
            
            # Watermark text
            if watermark_text:
                watermark_text = watermark_text.replace("'", "\\'")
                filters.append(
                    f"drawtext=text='{watermark_text}':"
                    f"fontsize=24:fontcolor=white@0.8:"
                    f"x=10:y=H-th-10:"
                    f"box=1:boxcolor=black@0.5:boxborderw=5"
                )
            
            # Watermark logo
            if watermark_logo and os.path.exists(watermark_logo):
                cmd.extend(["-i", watermark_logo])
                filters.append("overlay=W-w-10:10")
            
            # Apply filters
            if filters:
                cmd.extend(["-vf", ",".join(filters)])
            
            # Video codec settings
            cmd.extend([
                "-c:v", codec,
                "-preset", preset,
                "-crf", str(crf),
                "-b:v", video_bitrate
            ])
            
            # Audio settings
            cmd.extend([
                "-c:a", "aac",
                "-b:a", audio_bitrate,
                "-ar", "48000"
            ])
            
            # Output settings
            cmd.extend([
                "-y",  # Overwrite output file
                "-movflags", "+faststart",  # Enable streaming
                output_file
            ])
            
            # Execute FFmpeg
            process = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            return process.returncode == 0
            
        except Exception as e:
            logger.error(f"Encoding error: {e}")
            return False
    
    @staticmethod
    async def trim_video(
        input_file: str,
        output_file: str,
        start_time: str,
        end_time: str
    ) -> bool:
        """Trim video"""
        try:
            cmd = [
                "ffmpeg",
                "-i", input_file,
                "-ss", start_time,
                "-to", end_time,
                "-c", "copy",
                "-y",
                output_file
            ]
            
            process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return process.returncode == 0
            
        except Exception as e:
            logger.error(f"Trim error: {e}")
            return False
    
    @staticmethod
    async def crop_video(
        input_file: str,
        output_file: str,
        aspect_ratio: str
    ) -> bool:
        """Crop video to aspect ratio"""
        try:
            # Aspect ratio presets
            crop_filters = {
                "16:9": "crop=ih*16/9:ih",
                "9:16": "crop=iw:iw*16/9",
                "1:1": "crop=min(iw\\,ih):min(iw\\,ih)",
                "4:3": "crop=ih*4/3:ih",
                "21:9": "crop=ih*21/9:ih"
            }
            
            if aspect_ratio not in crop_filters:
                return False
            
            cmd = [
                "ffmpeg",
                "-i", input_file,
                "-vf", crop_filters[aspect_ratio],
                "-c:a", "copy",
                "-y",
                output_file
            ]
            
            process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return process.returncode == 0
            
        except Exception as e:
            logger.error(f"Crop error: {e}")
            return False
    
    @staticmethod
    async def merge_videos(
        input_files: list,
        output_file: str
    ) -> bool:
        """Merge multiple videos"""
        try:
            # Create concat file
            concat_file = "concat_list.txt"
            with open(concat_file, "w") as f:
                for file in input_files:
                    f.write(f"file '{file}'\n")
            
            cmd = [
                "ffmpeg",
                "-f", "concat",
                "-safe", "0",
                "-i", concat_file,
                "-c", "copy",
                "-y",
                output_file
            ]
            
            process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Cleanup
            if os.path.exists(concat_file):
                os.remove(concat_file)
            
            return process.returncode == 0
            
        except Exception as e:
            logger.error(f"Merge error: {e}")
            return False
    
    @staticmethod
    async def add_subtitle(
        input_file: str,
        subtitle_file: str,
        output_file: str,
        hard_sub: bool = False
    ) -> bool:
        """Add subtitle to video"""
        try:
            if hard_sub:
                # Hard subtitle (burned in)
                cmd = [
                    "ffmpeg",
                    "-i", input_file,
                    "-vf", f"subtitles={subtitle_file}",
                    "-c:a", "copy",
                    "-y",
                    output_file
                ]
            else:
                # Soft subtitle (embedded)
                cmd = [
                    "ffmpeg",
                    "-i", input_file,
                    "-i", subtitle_file,
                    "-c", "copy",
                    "-c:s", "mov_text",
                    "-y",
                    output_file
                ]
            
            process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return process.returncode == 0
            
        except Exception as e:
            logger.error(f"Subtitle error: {e}")
            return False
    
    @staticmethod
    async def extract_audio(
        input_file: str,
        output_file: str,
        format: str = "mp3"
    ) -> bool:
        """Extract audio from video"""
        try:
            cmd = [
                "ffmpeg",
                "-i", input_file,
                "-vn",  # No video
                "-acodec", "libmp3lame" if format == "mp3" else "copy",
                "-y",
                output_file
            ]
            
            process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return process.returncode == 0
            
        except Exception as e:
            logger.error(f"Extract audio error: {e}")
            return False
    
    @staticmethod
    async def extract_subtitle(
        input_file: str,
        output_file: str
    ) -> bool:
        """Extract subtitle from video"""
        try:
            cmd = [
                "ffmpeg",
                "-i", input_file,
                "-map", "0:s:0",
                "-y",
                output_file
            ]
            
            process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return process.returncode == 0
            
        except Exception as e:
            logger.error(f"Extract subtitle error: {e}")
            return False
    
    @staticmethod
    async def extract_thumbnail(
        input_file: str,
        output_file: str,
        timestamp: str = "00:00:01"
    ) -> bool:
        """Extract thumbnail from video"""
        try:
            cmd = [
                "ffmpeg",
                "-i", input_file,
                "-ss", timestamp,
                "-vframes", "1",
                "-y",
                output_file
            ]
            
            process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return process.returncode == 0
            
        except Exception as e:
            logger.error(f"Extract thumbnail error: {e}")
            return False
    
    @staticmethod
    async def add_audio(
        video_file: str,
        audio_file: str,
        output_file: str
    ) -> bool:
        """Add audio to video"""
        try:
            cmd = [
                "ffmpeg",
                "-i", video_file,
                "-i", audio_file,
                "-c:v", "copy",
                "-c:a", "aac",
                "-map", "0:v:0",
                "-map", "1:a:0",
                "-shortest",
                "-y",
                output_file
            ]
            
            process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return process.returncode == 0
            
        except Exception as e:
            logger.error(f"Add audio error: {e}")
            return False
    
    @staticmethod
    async def remove_audio(
        input_file: str,
        output_file: str
    ) -> bool:
        """Remove audio from video"""
        try:
            cmd = [
                "ffmpeg",
                "-i", input_file,
                "-c:v", "copy",
                "-an",  # No audio
                "-y",
                output_file
            ]
            
            process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return process.returncode == 0
            
        except Exception as e:
            logger.error(f"Remove audio error: {e}")
            return False
    
    @staticmethod
    async def remove_subtitle(
        input_file: str,
        output_file: str
    ) -> bool:
        """Remove all subtitles from video"""
        try:
            cmd = [
                "ffmpeg",
                "-i", input_file,
                "-c", "copy",
                "-sn",  # No subtitle
                "-y",
                output_file
            ]
            
            process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return process.returncode == 0
            
        except Exception as e:
            logger.error(f"Remove subtitle error: {e}")
            return False
    
    @staticmethod
    async def get_duration(file_path: str) -> float:
        """Get video duration in seconds"""
        try:
            cmd = [
                "ffprobe",
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                file_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            return float(result.stdout.strip())
            
        except Exception as e:
            logger.error(f"Get duration error: {e}")
            return 0.0
    
    @staticmethod
    async def get_resolution(file_path: str) -> tuple:
        """Get video resolution (width, height)"""
        try:
            cmd = [
                "ffprobe",
                "-v", "error",
                "-select_streams", "v:0",
                "-show_entries", "stream=width,height",
                "-of", "csv=s=x:p=0",
                file_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            width, height = result.stdout.strip().split('x')
            return int(width), int(height)
            
        except Exception as e:
            logger.error(f"Get resolution error: {e}")
            return 0, 0
    
    @staticmethod
    async def add_watermark_logo(
        input_file: str,
        watermark_file: str,
        output_file: str,
        position: str = "bottom-right"
    ) -> bool:
        """Add logo watermark to video"""
        try:
            # Position mapping
            positions = {
                "top-left": "10:10",
                "top-right": "W-w-10:10",
                "bottom-left": "10:H-h-10",
                "bottom-right": "W-w-10:H-h-10",
                "center": "(W-w)/2:(H-h)/2"
            }
            
            overlay_pos = positions.get(position, "W-w-10:H-h-10")
            
            cmd = [
                "ffmpeg",
                "-i", input_file,
                "-i", watermark_file,
                "-filter_complex",
                f"[1:v]scale=iw*0.2:-1[wm];[0:v][wm]overlay={overlay_pos}",
                "-c:a", "copy",
                "-y",
                output_file
            ]
            
            process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return process.returncode == 0
            
        except Exception as e:
            logger.error(f"Add watermark logo error: {e}")
            return False
