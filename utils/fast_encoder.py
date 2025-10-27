import subprocess
import os
import json
import re
import asyncio
import logging
from typing import Optional, Callable

logger = logging.getLogger(__name__)

class FastEncoder:
    """Optimized fast video encoder"""
    
    @staticmethod
    async def encode_video_fast(
        input_file: str,
        output_file: str,
        height: int = None,
        video_bitrate: str = "1M",
        audio_bitrate: str = "128k",
        codec: str = "libx264",
        preset: str = "faster",  # Changed from medium to faster
        crf: int = 23,
        watermark_text: str = None,
        progress_callback: Optional[Callable] = None,
        status_msg = None,
        file_name: str = ""
    ) -> bool:
        """
        Fast video encoding with progress tracking
        
        Args:
            input_file: Input video path
            output_file: Output video path
            height: Target height (width auto-calculated)
            video_bitrate: Video bitrate (e.g., "1M", "2M")
            audio_bitrate: Audio bitrate (e.g., "128k", "192k")
            codec: Video codec (libx264, libx265, libvpx-vp9)
            preset: Encoding preset (ultrafast, superfast, veryfast, faster, fast, medium)
            crf: Constant Rate Factor (18-28 recommended)
            watermark_text: Text watermark to add
            progress_callback: Async callback for progress updates
            status_msg: Status message object to update
            file_name: Original file name for display
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get total frames for progress calculation
            total_frames = await FastEncoder.get_total_frames(input_file)
            
            # Build FFmpeg command
            cmd = ["ffmpeg", "-i", input_file, "-y"]
            
            # Hardware acceleration (if available)
            # cmd.extend(["-hwaccel", "auto"])
            
            # Video filters
            filters = []
            
            # Scale filter
            if height:
                filters.append(f"scale=-2:{height}")
            
            # Watermark text
            if watermark_text:
                watermark_text = watermark_text.replace("'", "\\'")
                filters.append(
                    f"drawtext=text='{watermark_text}':"
                    f"fontsize=20:fontcolor=white@0.7:"
                    f"x=10:y=H-th-10:"
                    f"box=1:boxcolor=black@0.4:boxborderw=3"
                )
            
            # Apply filters
            if filters:
                cmd.extend(["-vf", ",".join(filters)])
            
            # Video codec settings
            if codec == "libx264":
                cmd.extend([
                    "-c:v", "libx264",
                    "-preset", preset,
                    "-crf", str(crf),
                    "-profile:v", "high",
                    "-level", "4.1",
                    "-pix_fmt", "yuv420p"
                ])
            elif codec == "libx265":
                cmd.extend([
                    "-c:v", "libx265",
                    "-preset", preset,
                    "-crf", str(crf),
                    "-tag:v", "hvc1"
                ])
            else:
                cmd.extend([
                    "-c:v", codec,
                    "-b:v", video_bitrate
                ])
            
            # Audio settings
            cmd.extend([
                "-c:a", "aac",
                "-b:a", audio_bitrate,
                "-ac", "2"  # Stereo
            ])
            
            # Output settings for faster encoding
            cmd.extend([
                "-movflags", "+faststart",
                "-map", "0:v:0",  # Map first video stream
                "-map", "0:a:0?",  # Map first audio stream if exists
                "-threads", "0",  # Use all CPU cores
                "-max_muxing_queue_size", "1024"
            ])
            
            # Enable progress reporting
            cmd.extend(["-progress", "pipe:1"])
            
            cmd.append(output_file)
            
            logger.info(f"Encoding command: {' '.join(cmd)}")
            
            # Execute FFmpeg with progress tracking
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            current_frame = 0
            
            # Read progress
            while True:
                line = await process.stdout.readline()
                if not line:
                    break
                
                line = line.decode('utf-8').strip()
                
                # Parse frame number
                if line.startswith('frame='):
                    try:
                        frame_match = re.search(r'frame=\s*(\d+)', line)
                        if frame_match:
                            current_frame = int(frame_match.group(1))
                            
                            if progress_callback and status_msg and total_frames > 0:
                                await progress_callback(
                                    current_frame, 
                                    total_frames, 
                                    status_msg,
                                    file_name
                                )
                    except Exception as e:
                        logger.error(f"Progress parsing error: {e}")
            
            await process.wait()
            
            if process.returncode == 0:
                logger.info(f"Encoding successful: {output_file}")
                return True
            else:
                stderr = await process.stderr.read()
                logger.error(f"Encoding failed: {stderr.decode('utf-8')}")
                return False
            
        except Exception as e:
            logger.error(f"Encoding error: {e}")
            return False
    
    @staticmethod
    async def get_total_frames(file_path: str) -> int:
        """Get total number of frames in video"""
        try:
            cmd = [
                "ffprobe",
                "-v", "error",
                "-select_streams", "v:0",
                "-count_packets",
                "-show_entries", "stream=nb_read_packets",
                "-of", "csv=p=0",
                file_path
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, _ = await process.communicate()
            frames = int(stdout.decode('utf-8').strip())
            return frames
            
        except Exception as e:
            logger.error(f"Error getting frame count: {e}")
            # Fallback: calculate from duration and fps
            try:
                duration = await FastEncoder.get_duration(file_path)
                return int(duration * 24)  # Assume 24fps
            except:
                return 0
    
    @staticmethod
    async def get_duration(file_path: str) -> float:
        """Get video duration"""
        try:
            cmd = [
                "ffprobe",
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                file_path
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, _ = await process.communicate()
            return float(stdout.decode('utf-8').strip())
            
        except Exception as e:
            logger.error(f"Error getting duration: {e}")
            return 0.0
    
    @staticmethod
    async def get_video_info(file_path: str) -> dict:
        """Get detailed video information"""
        try:
            cmd = [
                "ffprobe",
                "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                "-show_streams",
                file_path
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, _ = await process.communicate()
            return json.loads(stdout.decode('utf-8'))
            
        except Exception as e:
            logger.error(f"Error getting video info: {e}")
            return {}
