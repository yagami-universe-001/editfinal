import time
import math
from utils.helpers import human_readable_size, format_time

class EnhancedProgress:
    """Enhanced progress tracker with detailed stats"""
    
    def __init__(self, total_size: int = 0, total_frames: int = 0):
        self.total_size = total_size
        self.total_frames = total_frames
        self.start_time = time.time()
        self.last_update = 0
        self.downloaded = 0
        self.last_downloaded = 0
        
    def make_progress_bar(self, percentage: float, length: int = 20) -> str:
        """Create a visual progress bar"""
        filled = int(length * percentage / 100)
        bar = "█" * filled + "░" * (length - filled)
        return f"[{bar}] {percentage:.2f}%"
    
    async def download_progress(self, current: int, total: int, status_msg, action: str = "Downloading"):
        """Enhanced download progress callback"""
        try:
            now = time.time()
            diff = now - self.last_update
            
            # Update every 2 seconds
            if diff < 2:
                return
            
            self.last_update = now
            elapsed = now - self.start_time
            
            percentage = (current / total) * 100 if total > 0 else 0
            speed = current / elapsed if elapsed > 0 else 0
            eta = (total - current) / speed if speed > 0 else 0
            
            # Calculate speed difference for acceleration
            speed_diff = (current - self.last_downloaded) / diff if diff > 0 else 0
            self.last_downloaded = current
            
            progress_bar = self.make_progress_bar(percentage)
            
            text = (
                f"**📥 {action}...**\n\n"
                f"`{progress_bar}`\n\n"
                f"**▸ Progress:** {human_readable_size(current)} / {human_readable_size(total)}\n"
                f"**▸ Speed:** {human_readable_size(speed)}/s\n"
                f"**▸ Time Left:** {format_time(eta)}\n"
                f"**▸ Elapsed:** {format_time(elapsed)}"
            )
            
            try:
                await status_msg.edit_text(text)
            except:
                pass
                
        except Exception as e:
            pass
    
    async def encoding_progress(self, current_frame: int, total_frames: int, status_msg, file_name: str = ""):
        """Enhanced encoding progress with detailed stats"""
        try:
            now = time.time()
            diff = now - self.last_update
            
            # Update every 3 seconds
            if diff < 3:
                return
            
            self.last_update = now
            elapsed = now - self.start_time
            
            percentage = (current_frame / total_frames) * 100 if total_frames > 0 else 0
            fps = current_frame / elapsed if elapsed > 0 else 0
            remaining_frames = total_frames - current_frame
            eta = remaining_frames / fps if fps > 0 else 0
            
            # Calculate processing speed
            speed_multiplier = fps / 24 if fps > 0 else 0  # Assuming 24fps source
            
            progress_bar = self.make_progress_bar(percentage)
            
            # Format time strings
            elapsed_str = format_time(elapsed)
            eta_str = format_time(eta)
            total_time_str = format_time(elapsed + eta)
            
            text = (
                f"**▸ File:** `{file_name[:35]}...`\n\n"
                f"**▸ Status:** `Encoding`\n"
                f"`{progress_bar}`\n\n"
                f"**▸ Processed:** {format_time(current_frame / 24)} / {format_time(total_frames / 24)}\n"
                f"**▸ Speed:** {fps:.2f} fps ({speed_multiplier:.2f}x)\n"
                f"**▸ Time Took:** {elapsed_str}\n"
                f"**▸ Time Left:** {eta_str}\n\n"
                f"**▸ Quality:** Processing"
            )
            
            try:
                await status_msg.edit_text(text)
            except:
                pass
                
        except Exception as e:
            pass
    
    async def upload_progress(self, current: int, total: int, status_msg, file_name: str = ""):
        """Enhanced upload progress"""
        try:
            now = time.time()
            diff = now - self.last_update
            
            if diff < 2:
                return
            
            self.last_update = now
            elapsed = now - self.start_time
            
            percentage = (current / total) * 100 if total > 0 else 0
            speed = current / elapsed if elapsed > 0 else 0
            eta = (total - current) / speed if speed > 0 else 0
            
            progress_bar = self.make_progress_bar(percentage)
            
            text = (
                f"**▸ File:** `{file_name[:35]}...`\n\n"
                f"**▸ Status:** `Uploading`\n"
                f"`{progress_bar}`\n\n"
                f"**▸ Progress:** {human_readable_size(current)} / {human_readable_size(total)}\n"
                f"**▸ Speed:** {human_readable_size(speed)}/s\n"
                f"**▸ Time Left:** {format_time(eta)}\n"
                f"**▸ Elapsed:** {format_time(elapsed)}"
            )
            
            try:
                await status_msg.edit_text(text)
            except:
                pass
                
        except Exception as e:
            pass


# Wrapper functions for easy use
async def download_progress_hook(current, total, status_msg):
    """Simple download progress hook"""
    tracker = EnhancedProgress(total_size=total)
    await tracker.download_progress(current, total, status_msg)

async def encoding_progress_hook(current_frame, total_frames, status_msg, file_name=""):
    """Simple encoding progress hook"""
    tracker = EnhancedProgress(total_frames=total_frames)
    await tracker.encoding_progress(current_frame, total_frames, status_msg, file_name)

async def upload_progress_hook(current, total, status_msg, file_name=""):
    """Simple upload progress hook"""
    tracker = EnhancedProgress(total_size=total)
    await tracker.upload_progress(current, total, status_msg, file_name)
