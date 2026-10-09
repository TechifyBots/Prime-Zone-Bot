from pyrogram import Client, filters
from pyrogram.types import Message
from config import DATABASE_CHANNEL_ID, DATABASE_CHANNEL_LOG, FREE_VIDEO_DURATION
from Database.maindb import mdb

@Client.on_message(filters.chat(DATABASE_CHANNEL_ID) & filters.video)
async def save_video(client: Client, message: Message):
    try:
        video_id = message.id
        video_duration = message.video.duration
        is_premium = video_duration > FREE_VIDEO_DURATION
        await mdb.save_video_id(video_id, video_duration, is_premium)
        text = f"**✅ Saved | ID: {video_id} | ⏱️ {video_duration}s | 💎 {is_premium}**"
        await client.send_message(chat_id=DATABASE_CHANNEL_LOG, text=text)
    except Exception as t:
        print(f"Error: {str(t)}")
