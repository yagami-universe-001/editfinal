import time
import asyncio
from utils.helpers import human_readable_size, format_time

# Store active tasks for cancellation
active_tasks = {}

class ProfessionalProgress:
    """Professional progress display like Echo Encoder"""
    
    def __init__(self, user_id: int, task_id: str):
        self.user_id = user_id
        self.task_id = task_id
        self.start_time = time.time()
        self.last_update = 0
        self.cancelled = False
        
        # Store in active tasks
        active_tasks[f"{user_id}_{task_id}"] = self
    
    def make_progress_bar(self, percentage: float) -> str:
        """Create progress bar like [ ●●●●●●●●○○ ]"""
        total_blocks = 15
        filled = int((percentage / 100) * total_blocks)
        bar = "●" * filled + "○" * (total_blocks - filled)
        return f"[ {bar} ] >> {percentage:.1f}%"
    
    async def download_progress(self, current: int, total: int, status_msg, file_name: str, username: str):
        """Downloading progress display"""
        try:
            if self.cancelled:
                raise asyncio.CancelledError("Task cancelled by user")
                
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
                f"**1. Downloading**\n\n"
                f"`{file_name}`\n\n"
                f"`{progress_bar}`\n"
                f"├ **Speed:** {human_readable_size(speed)}/s\n"
                f"├ **Size:** {human_readable_size(current)} / {human_readable_size(total)}\n"
                f"├ **ETA:** {format_time(eta)}\n"
                f"├ **Elapsed:** {format_time(elapsed)}\n"
                f"├ **Task By:** {username}\n"
                f"└ **User ID:** `{self.user_id}`\n\n"
                f"`/stop{self.task_id}`"
            )
            
            try:
                await status_msg.edit_text(text)
            except:
                pass
                
        except asyncio.CancelledError:
            raise
        except Exception as e:
            pass
    
    async def encoding_progress(self, current_frame: int, total_frames: int, status_msg, file_name: str, username: str, quality: str):
        """Encoding progress display"""
        try:
            if self.cancelled:
                raise asyncio.CancelledError("Task cancelled by user")
                
            now = time.time()
            diff = now - self.last_update
            
            if diff < 3:
                return
            
            self.last_update = now
            elapsed = now - self.start_time
            
            percentage = (current_frame / total_frames) * 100 if total_frames > 0 else 0
            fps = current_frame / elapsed if elapsed > 0 else 0
            remaining_frames = total_frames - current_frame
            eta = remaining_frames / fps if fps > 0 else 0
            
            # Calculate time processed
            processed_time = format_time(current_frame / 24)  # Assuming 24fps
            total_time = format_time(total_frames / 24)
            
            progress_bar = self.make_progress_bar(percentage)
            
            text = (
                f"**2. Encoding**\n\n"
                f"`{file_name}`\n\n"
                f"`{progress_bar}`\n"
                f"├ **Processed:** {processed_time} / {total_time}\n"
                f"├ **Speed:** {fps:.2f}x\n"
                f"├ **Time Took:** {format_time(elapsed)}\n"
                f"├ **Time Left:** {format_time(eta)}\n"
                f"├ **Task By:** {username}\n"
                f"└ **User ID:** `{self.user_id}`\n\n"
                f"**▸ Quality:** {quality}\n\n"
                f"`/stop{self.task_id}`"
            )
            
            try:
                await status_msg.edit_text(text)
            except:
                pass
                
        except asyncio.CancelledError:
            raise
        except Exception as e:
            pass
    
    async def uploading_progress(self, current: int, total: int, status_msg, file_name: str, username: str):
        """Uploading progress display"""
        try:
            if self.cancelled:
                raise asyncio.CancelledError("Task cancelled by user")
                
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
                f"**3. Uploading**\n\n"
                f"`{file_name}`\n\n"
                f"`{progress_bar}`\n"
                f"├ **Speed:** {human_readable_size(speed)}/s\n"
                f"├ **Size:** {human_readable_size(current)} / {human_readable_size(total)}\n"
                f"├ **ETA:** {format_time(eta)}\n"
                f"├ **Elapsed:** {format_time(elapsed)}\n"
                f"├ **Task By:** {username}\n"
                f"└ **User ID:** `{self.user_id}`\n\n"
                f"`/stop{self.task_id}`"
            )
            
            try:
                await status_msg.edit_text(text)
            except:
                pass
                
        except asyncio.CancelledError:
            raise
        except Exception as e:
            pass
    
    def cancel(self):
        """Cancel this task"""
        self.cancelled = True
        # Remove from active tasks
        task_key = f"{self.user_id}_{self.task_id}"
        if task_key in active_tasks:
            del active_tasks[task_key]


def get_task(user_id: int, task_id: str):
    """Get active task"""
    task_key = f"{user_id}_{task_id}"
    return active_tasks.get(task_key)

def cancel_task(user_id: int, task_id: str):
    """Cancel a task"""
    task = get_task(user_id, task_id)
    if task:
        task.cancel()
        return True
    return False

def get_user_tasks(user_id: int):
    """Get all tasks for a user"""
    return [task for key, task in active_tasks.items() if str(user_id) in key]
