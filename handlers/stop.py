from pyrogram import Client
from pyrogram.types import Message
from utils.progress_display import cancel_task, get_user_tasks
import logging

logger = logging.getLogger(__name__)

async def stop_task(client: Client, message: Message):
    """Stop/cancel ongoing task"""
    user_id = message.from_user.id
    
    # Check if command has task ID
    if len(message.command) > 1:
        task_id = message.command[1]
    else:
        # Extract task ID from command (e.g., /stop2bCD3QTTP)
        full_command = message.text.strip()
        if len(full_command) > 5:  # /stop + task_id
            task_id = full_command[5:]  # Remove '/stop'
        else:
            await message.reply_text(
                "⚠️ **Usage:** `/stop<task_id>`\n\n"
                "**Example:** `/stop2bCD3QTTP`\n\n"
                "Task ID is shown in progress message."
            )
            return
    
    # Try to cancel the task
    success = cancel_task(user_id, task_id)
    
    if success:
        await message.reply_text(
            f"✅ **Task Cancelled!**\n\n"
            f"**Task ID:** `{task_id}`\n"
            f"**User ID:** `{user_id}`\n\n"
            f"The ongoing operation has been stopped."
        )
    else:
        await message.reply_text(
            f"❌ **Task Not Found!**\n\n"
            f"**Task ID:** `{task_id}`\n\n"
            f"**Possible reasons:**\n"
            f"• Task already completed\n"
            f"• Invalid task ID\n"
            f"• Task belongs to another user"
        )

async def list_tasks(client: Client, message: Message):
    """List all active tasks for user"""
    user_id = message.from_user.id
    tasks = get_user_tasks(user_id)
    
    if not tasks:
        await message.reply_text(
            "📝 **No Active Tasks**\n\n"
            "You don't have any ongoing tasks."
        )
        return
    
    text = f"📋 **Your Active Tasks ({len(tasks)})**\n\n"
    
    for task in tasks:
        text += f"• Task ID: `{task.task_id}`\n"
        text += f"  Started: {format_time(time.time() - task.start_time)} ago\n\n"
    
    text += "\n**To stop a task:** `/stop<task_id>`"
    
    await message.reply_text(text)
