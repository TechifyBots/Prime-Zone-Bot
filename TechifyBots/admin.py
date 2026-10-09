import asyncio
import re
import time
from pyrogram import Client, filters, enums
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from pyrogram.errors import (
    UserIsBlocked,
    PeerIdInvalid,
    InputUserDeactivated,
    FloodWait,
)
from Database.userdb import udb
from Database.maindb import mdb
from config import ADMIN_ID
from bot import bot
from collections import defaultdict

def parse_button_markup(text: str):
    lines = text.split("\n")
    buttons = []
    final_text_lines = []
    for line in lines:
        row = []
        parts = line.split("||")
        is_button_line = True
        for part in parts:
            match = re.fullmatch(r"\[(.+?)\]\((https?://[^\s]+)\)", part.strip())
            if match:
                row.append(InlineKeyboardButton(match[1], url=match[2]))
            else:
                is_button_line = False
                break
        if is_button_line and row:
            buttons.append(row)
        else:
            final_text_lines.append(line)
    return InlineKeyboardMarkup(buttons) if buttons else None, "\n".join(final_text_lines).strip()

async def get_readable_time(seconds: int) -> str:
    time_data = []
    for unit, div in [("d", 86400), ("h", 3600), ("m", 60), ("s", 1)]:
        value, seconds = divmod(seconds, div)
        if value > 0 or unit == "s":
            time_data.append(f"{int(value)}{unit}")
    return " ".join(time_data)

@Client.on_message(filters.command("stats") & filters.private)
async def stats_command(client, message):
    if message.from_user.id != ADMIN_ID:
        await message.delete()
        await message.reply_text("**🚫 You’re not authorized to use this command...**")
        return
    video_count = await mdb.count_all_videos()
    total_users = await udb.get_all_users()
    bot_uptime = int(time.time() - bot.START_TIME)
    uptime = await get_readable_time(bot_uptime)
    STATS = ">**🤖 Bot Statistics**\n\n"
    STATS += f"**Total Users: {len(total_users)}\n**"
    STATS += f"**Total Files in DB: {video_count}\n**"
    STATS += f"**BOT Uptime: {uptime}**"
    await message.reply_text(STATS)

@Client.on_message(filters.command("ban") & filters.private & filters.user(ADMIN_ID))
async def ban_user_cmd(client: Client, message: Message):
    try:
        command_parts = message.text.split()
        if len(command_parts) < 2:
            await message.reply_text("Usage: /ban user_id")
            return
        user_id = int(command_parts[1])
        reason = " ".join(command_parts[2:]) if len(command_parts) > 2 else None
        try:
            user = await client.get_users(user_id)
        except Exception:
            await message.reply_text("Unable to find user.")
            return
        if await udb.ban_user(user_id, reason):
            ban_message = f"User {user.mention} has been banned."
            if reason:
                ban_message += f"\nReason: {reason}"
            await message.reply_text(ban_message)
        else:
            await message.reply_text("Failed to ban user.")
    except ValueError:
        await message.reply_text("Please provide a valid user ID.")
    except Exception as e:
        await message.reply_text(f"An error occurred: {str(e)}")

@Client.on_message(filters.command("maintenance") & filters.private & filters.user(ADMIN_ID))
async def maintenance_mode(client: Client, message: Message):
    try:
        args = message.text.split()
        if len(args) < 2:
            await message.reply_text("Usage: /maintenance [on/off]")
            return
        status = args[1].lower()
        if status not in ["on", "off"]:
            await message.reply_text("Invalid status. Use 'on' or 'off'")
            return
        await mdb.set_maintenance_status(status == "on")
        await message.reply_text(f"Maintenance mode {'activated' if status == 'on' else 'deactivated'}")
    except Exception as e:
        await message.reply_text(f"Error: {str(e)}")

@Client.on_message(filters.command("unban") & filters.private & filters.user(ADMIN_ID))
async def unban_user_cmd(client: Client, message: Message):
    try:
        command_parts = message.text.split()
        if len(command_parts) < 2:
            await message.reply_text("Usage: /unban user_id")
            return
        user_id = int(command_parts[1])
        try:
            user = await client.get_users(user_id)
        except Exception:
            await message.reply_text("Unable to find user.")
            return
        if await udb.unban_user(user_id):
            await message.reply_text(f"User {user.mention} has been unbanned.")
        else:
            await message.reply_text("Failed to unban user or user was not banned.")
    except ValueError:
        await message.reply_text("Please provide a valid user ID.")
    except Exception as e:
        await message.reply_text(f"An error occurred: {str(e)}")

@Client.on_message(filters.command('banlist') & filters.private & filters.user(ADMIN_ID))
async def banlist(client, message):
    response = await message.reply("<b>Fetching banned users...</b>")
    try:
        banned_users = await udb.banned_users.find().to_list(length=None)
        if not banned_users:
            return await response.edit("<b>No users are currently banned.</b>")
        text = "<b>🚫 Banned Users:</b>\n\n"
        for user in banned_users:
            user_id = user.get("user_id")
            reason = user.get("reason", "No reason provided")
            text += f"• <code>{user_id}</code> — {reason}\n"
        await response.edit(text)
    except Exception as e:
        await response.edit(f"<b>Error:</b> <code>{str(e)}</code>")

@Client.on_message(filters.command("deleteall") & filters.private & filters.user(ADMIN_ID))
async def delete_all_videos_command(client, message):
    try:
        t = await message.reply_text("**Proceed to delete all videos ♻️**")
        await mdb.delete_all_videos()
        await t.edit_text("**✅ All videos have been deleted from the database**")
    except Exception as e:
        await message.reply_text(f"**Error: {str(e)}*")

@Client.on_message(filters.command("delete") & filters.private & filters.user(ADMIN_ID))
async def delete_video_by_id_command(client, message):
    if len(message.command) < 2:
        await message.reply_text("⚠️ Please provide a video ID to delete.")
        return
    video_id = int(message.command[1])
    deleted = await mdb.delete_video_by_id(video_id)
    if deleted:
        await message.reply_text(f"✅ Deleted video with ID `{video_id}`")
    else:
        await message.reply_text(f"⚠️ Video ID `{video_id}` not found.")

@Client.on_message(filters.command("broadcast") & filters.private & filters.user(ADMIN_ID))
async def broadcasting_func(client: Client, message: Message):
    if not message.reply_to_message:
        return await message.reply("<b>Reply to a message to broadcast.</b>")
    msg = await message.reply_text("📢 Starting broadcast...")
    to_copy_msg = message.reply_to_message
    users_list = await udb.get_all_users()
    total_before = len(users_list)
    completed_users = set()
    failed = 0
    raw_text = to_copy_msg.caption or to_copy_msg.text or ""
    reply_markup, cleaned_text = parse_button_markup(raw_text)
    for i, user in enumerate(users_list, start=1):
        user_id = user.get("user_id")
        if not user_id:
            if await udb.delete_user(user.get("_id")):
                failed += 1
            continue
        try:
            user_id = int(user_id)  # normalize to int
            if to_copy_msg.text:
                await client.send_message(user_id, cleaned_text, reply_markup=reply_markup)
            elif to_copy_msg.photo:
                await client.send_photo(user_id, to_copy_msg.photo.file_id, caption=cleaned_text, reply_markup=reply_markup)
            elif to_copy_msg.video:
                await client.send_video(user_id, to_copy_msg.video.file_id, caption=cleaned_text, reply_markup=reply_markup)
            elif to_copy_msg.document:
                await client.send_document(user_id, to_copy_msg.document.file_id, caption=cleaned_text, reply_markup=reply_markup)
            else:
                await to_copy_msg.copy(user_id)
            completed_users.add(user_id)
        except (UserIsBlocked, PeerIdInvalid, InputUserDeactivated):
            if await udb.delete_user(user_id):
                failed += 1
        except FloodWait as e:
            await asyncio.sleep(e.value)
            try:
                await to_copy_msg.copy(user_id)
                completed_users.add(user_id)
            except Exception:
                if await udb.delete_user(user_id):
                    failed += 1
        except Exception:
            if await udb.delete_user(user_id):
                failed += 1
        if i % 20 == 0 or i == total_before:
            try:
                await msg.edit(
                    f"😶‍🌫 Broadcasting...\n\n"
                    f"👥 Total Users: {total_before}\n"
                    f"✅ Successful: <code>{len(completed_users)}</code>\n"
                    f"❌ Failed/Removed: <code>{failed}</code>\n"
                    f"⚙️ Progress: {i}/{total_before}"
                )
            except Exception:
                pass
        await asyncio.sleep(0.05)
    all_users = await udb.get_all_users()
    users_by_id = defaultdict(list)
    for user in all_users:
        uid = user.get("user_id")
        if not uid:
            if await udb.delete_user(user.get("_id")):
                failed += 1
            continue
        users_by_id[uid].append(user)
    for uid, docs in users_by_id.items():
        if uid in completed_users:
            for duplicate in docs[1:]:
                if await udb.delete_user(duplicate.get("user_id")):
                    failed += 1
        else:
            for doc in docs:
                if await udb.delete_user(doc.get("user_id")):
                    failed += 1
    active_users = len(completed_users)
    await msg.edit(
        f"🎯 <b>Broadcast Completed</b>\n\n"
        f"👥 Total Users (Before): <code>{total_before}</code>\n"
        f"✅ Successful: <code>{len(completed_users)}</code>\n"
        f"❌ Failed/Removed: <code>{failed}</code>\n"
        f"📊 Active Users (Now): <code>{active_users}</code>",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🎭 𝖢𝗅𝗈𝗌𝖾", callback_data="close", style=enums.ButtonStyle.DANGER)]])
    )
