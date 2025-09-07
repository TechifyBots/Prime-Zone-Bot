from pyrogram.types import *
from Database.userdb import udb
from Database.maindb import mdb
from vars import ADMIN_ID
import asyncio
from pyrogram.errors import *
from pyrogram import *
from bot import bot
import time
import re

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

@Client.on_message(filters.command("broadcast") & filters.private & filters.user(ADMIN_ID))
async def broadcasting_func(client: Client, message: Message):
    if not message.reply_to_message:
        return await message.reply("<b>Reply to a message to broadcast.</b>")
    msg = await message.reply_text("Processing broadcast...")
    to_copy_msg = message.reply_to_message
    users_list = await udb.get_all_users()
    completed = 0
    failed = 0
    raw_text = to_copy_msg.caption or to_copy_msg.text or ""
    reply_markup, cleaned_text = parse_button_markup(raw_text)
    for i, user in enumerate(users_list):
        user_id = user.get("user_id")
        if not user_id:
            continue
        try:
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
            completed += 1
        except (UserIsBlocked, PeerIdInvalid, InputUserDeactivated):
            await tb.delete_user(user_id)
            failed += 1
        except FloodWait as e:
            await asyncio.sleep(e.value)
            try:
                await to_copy_msg.copy(user_id)
                completed += 1
            except:
                failed += 1
        except Exception as e:
            print(f"Broadcast to {user_id} failed: {e}")
            failed += 1
        await msg.edit(f"Total: {i + 1}\nCompleted: {completed}\nFailed: {failed}")
        await asyncio.sleep(0.1)
    await msg.edit(
        f"😶‍🌫 <b>Broadcast Completed</b>\n\n👥 Total Users: <code>{len(users_list)}</code>\n✅ Successful: <code>{completed}</code>\n🤯 Failed: <code>{failed}</code>",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🎭 𝖢𝗅𝗈𝗌𝖾", callback_data="close")]])
    )

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
    if len(message.command) < 2:return
    await message.reply_text("⚠️ Please provide a video ID to delete.")
    video_id = int(message.command[1])
    deleted = await mdb.delete_video_by_id(video_id)
    if deleted:
        await message.reply_text(f"✅ Deleted video with ID `{video_id}`")
    else:
        await message.reply_text(f"⚠️ Video ID `{video_id}` not found.")
