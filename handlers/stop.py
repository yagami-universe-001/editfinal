from pyrogram import Client
from pyrogram.types import Message
from utils.progress_display import cancel_task, get_user_tasks
from utils.helpers import format_time
import time
import logging

logger = logging.getLogger(__name__)

async def stop_task(client: Client, message: Message):
    """Stop/cancel ongoing task - FIXED VERSION"""
    user_id = message.from_user.id
    
    # Parse the command - it can be /stop2bCD3QTTP or /stop 2bCD3QTTP
    full_command = message.text.strip()
    
    # Extract task ID
    task_id = None
    
    # Method 1: Check if there's a space (e.g., "/stop 2bCD3QTTP")
    if len(message.command) > 1:
        task_id = message.command[1]
    # Method 2: Check if task ID is attached to command (e.g., "/stop2bCD3QTTP")
    elif len(full_command) > 5:  # "/stop" is 5 characters
        task_id = full_command[5:]  # Extract everything after "/stop"
    
    # If no task ID found, show usage
    if not task_id:
        await message.reply_text(
            "⚠️ **How to Stop a Task**\n\n"
            "**Usage:** `/stop<task_id>` or `/stop <task_id>`\n\n"
            "**Examples:**\n"
            "• `/stop2bCD3QTTP`\n"
            "• `/stop 2bCD3QTTP`\n\n"
            "**To see your active tasks:** Use `/tasks` command\n\n"
            "The task ID is shown in the progress message."
        )
        return
    
    logger.info(f"User {user_id} attempting to stop task: {task_id}")
    
    # Try to cancel the task
    try:
        success = cancel_task(user_id, task_id)
        
        if success:
            await message.reply_text(
                f"✅ **Task Cancelled Successfully!**\n\n"
                f"**Task ID:** `{task_id}`\n"
                f"**User:** {user_id}\n\n"
                f"The encoding/processing has been stopped and files are being cleaned up."
            )
            logger.info(f"Task {task_id} cancelled successfully for user {user_id}")
        else:
            await message.reply_text(
                f"❌ **Task Not Found!**\n\n"
                f"**Task ID:** `{task_id}`\n\n"
                f"**Possible reasons:**\n"
                f"• Task already completed\n"
                f"• Invalid task ID (check spelling)\n"
                f"• Task belongs to another user\n"
                f"• Task was already cancelled\n\n"
                f"Use `/tasks` to see your active tasks."
            )
            logger.warning(f"Failed to cancel task {task_id} for user {user_id}")
    except Exception as e:
        logger.error(f"Error stopping task {task_id}: {e}")
        await message.reply_text(
            f"❌ **Error Stopping Task**\n\n"
            f"**Error:** {str(e)}\n\n"
            f"Please try again or contact support if the issue persists."
        )

async def list_tasks(client: Client, message: Message):
    """List all active tasks for user"""
    user_id = message.from_user.id
    
    try:
        tasks = get_user_tasks(user_id)
        
        if not tasks:
            await message.reply_text(
                "📝 **No Active Tasks**\n\n"
                "You don't have any ongoing encoding or processing tasks.\n\n"
                "Send a video to start processing!"
            )
            return
        
        text = f"📋 **Your Active Tasks** ({len(tasks)} task{'s' if len(tasks) > 1 else ''})\n\n"
        
        for i, task in enumerate(tasks, 1):
            elapsed = time.time() - task.start_time
            elapsed_str = format_time(elapsed)
            
            text += f"**{i}.** Task ID: `/stop{task.task_id}`\n"
            text += f"   ⏱ Running for: {elapsed_str}\n"
            
            # Add task type if available
            if hasattr(task, 'task_type'):
                text += f"   📝 Type: {task.task_type}\n"
            
            text += "\n"
        
        text += "\n**To stop a task:** Tap on the task ID above or use `/stop<task_id>`"
        
        await message.reply_text(text)
        logger.info(f"Listed {len(tasks)} tasks for user {user_id}")
        
    except Exception as e:
        logger.error(f"Error listing tasks for user {user_id}: {e}")
        await message.reply_text(
            f"❌ **Error Getting Tasks**\n\n"
            f"**Error:** {str(e)}\n\n"
            f"Please try again later."
        )
