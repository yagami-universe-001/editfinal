import time
import asyncio
from utils.helpers import human_readable_size, format_time, format_progress_bar

try:
    main_loop = asyncio.get_running_loop()
except RuntimeError:
    main_loop = None

def sync_progress_callback(current, total, status_message, start_time, action="Processing"):
    """Synchronous wrapper to call the async progress callback"""
    if main_loop:
        asyncio.run_coroutine_threadsafe(
            progress_callback(current, total, status_message, start_time, action),
            main_loop
        )

async def progress_callback(current, total, status_message, start_time, action="Processing"):
    """Progress callback for upload/download"""
    try:
        # Calculate progress
        percentage = (current / total) * 100
        
        # Calculate speed
        elapsed_time = time.time() - start_time
        if elapsed_time > 0:
            speed = current / elapsed_time
            eta = (total - current) / speed if speed > 0 else 0
        else:
            speed = 0
            eta = 0
        
        # Format progress text
        progress_text = (
            f"📊 **{action}...**\n\n"
            f"{format_progress_bar(percentage)}\n\n"
            f"**Progress:** {human_readable_size(current)} / {human_readable_size(total)}\n"
            f"**Speed:** {human_readable_size(speed)}/s\n"
            f"**ETA:** {format_time(eta)}\n"
            f"**Elapsed:** {format_time(elapsed_time)}"
        )
        
        # Update message every 3 seconds
        if int(percentage) % 5 == 0:
            try:
                await status_message.edit_text(progress_text)
            except:
                pass
    except:
        pass

class ProgressTracker:
    """Track encoding progress"""
    
    def __init__(self, total_frames: int = 0):
        self.total_frames = total_frames
        self.start_time = time.time()
        self.last_update = 0
        
    async def update(self, current_frame: int, status_message):
        """Update progress"""
        try:
            # Calculate progress
            if self.total_frames > 0:
                percentage = (current_frame / self.total_frames) * 100
            else:
                percentage = 0
            
            # Calculate time
            elapsed = time.time() - self.start_time
            if current_frame > 0 and self.total_frames > 0:
                fps = current_frame / elapsed
                remaining_frames = self.total_frames - current_frame
                eta = remaining_frames / fps if fps > 0 else 0
            else:
                fps = 0
                eta = 0
            
            # Update every 3 seconds
            current_time = time.time()
            if current_time - self.last_update >= 3:
                self.last_update = current_time
                
                progress_text = (
                    f"🎬 **Encoding...**\n\n"
                    f"{format_progress_bar(percentage)}\n\n"
                    f"**Frame:** {current_frame}/{self.total_frames}\n"
                    f"**FPS:** {fps:.2f}\n"
                    f"**ETA:** {format_time(eta)}\n"
                    f"**Elapsed:** {format_time(elapsed)}"
                )
                
                try:
                    await status_message.edit_text(progress_text)
                except:
                    pass
        except:
            pass
