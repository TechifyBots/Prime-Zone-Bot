from pyrogram import Client, filters
from vars import ADMIN_ID, ADMIN_USERNAME
from pyrogram.types import *
from Database.userdb import udb
from Database.maindb import mdb
import pytz

@Client.on_message(filters.command("myplan") & filters.private)
async def my_plan(client, message):
    if await udb.is_user_banned(message.from_user.id):
        await message.reply("**🚫 You are banned from using this bot**",reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Support 🧑‍💻", url=f"https://t.me/{ADMIN_USERNAME}")]]))
        return
    global_limits = await mdb.get_global_limits()
    FREE_LIMIT = global_limits["free_limit"]
    user_id = message.from_user.id
    user = await mdb.get_user(user_id)
    user = await mdb.get_user(user_id)
    plan = user.get("plan", "free")
    daily_count = user.get("daily_count", 0)
    daily_limit = user.get("daily_limit", FREE_LIMIT)
    prime_expiry = user.get("prime_expiry")
    status_text = f""">**Plan Details**

**User: {message.from_user.mention}**
**User id: {user_id}**
**User Plan: {plan.capitalize()}**
**Daily Limit: {daily_limit}**
**Today used: {daily_count}/{daily_limit}**
**Total Remaining: {daily_limit - daily_count}**\n"""

    if plan == "prime" and prime_expiry:
        IST = pytz.timezone('Asia/Kolkata')
        if prime_expiry and prime_expiry.tzinfo is None:
            prime_expiry = prime_expiry.astimezone(IST)
        status_text += f"\n**Expire Time: {prime_expiry.strftime('%I:%M %p IST')}**"
        status_text += f"\n**Expire Date: {prime_expiry.strftime('%d/%m/%Y')}**"
    if daily_count >= daily_limit and plan == "free":
         status_text += "\n**⚠️ You've reached your daily limit.**"
    await message.reply_text(status_text)

@Client.on_message(filters.command("prime") & filters.private)
async def add_prime(client, message):
    if message.from_user.id != ADMIN_ID:
        await message.delete()
        await message.reply_text("**🚫 You're not authorized to use this command...**")
        return
    if len(message.command) != 3:
        await message.reply_text("**Usage: /prime {user_id} {duration}{unit}\n\nExample: /prime 123456789 2d\n\nUnits:\ns = seconds\nm = minutes\nh = hours\nd = days\ny = years**")
        return
    try:
        user_id = int(message.command[1])
        duration_input = message.command[2]
        import re
        match = re.match(r'(\d+)([smhdy])', duration_input)
        if not match:
            await message.reply_text("**⚠️ Invalid duration format. Use format like: 2d, 30m, 24h**")
            return
        amount, unit = match.groups()
        duration_str = f"{amount} {unit}"
        success = await mdb.add_prime(user_id, duration_str)
        if success:
            await message.reply_text(f"**✅ User {user_id} has been successfully added to the Prime Plan for {duration_str}.**")
            await client.send_message(chat_id=user_id, text="**🎉 Hey, You've been upgraded to a Premier user, check your plan by using /myplan**")
        else:
            await message.reply_text("**❌ Failed to add user to premium plan. Please check the user ID and duration format.**")
    except ValueError:
        await message.reply_text("**⚠️ Invalid user ID or duration format.**")
    except Exception as e:
        await message.reply_text(f"**❌ An error occurred: {str(e)}**")

@Client.on_message(filters.command("remove") & filters.private)
async def remove_prime(client, message):
    if message.from_user.id != ADMIN_ID:
        await message.delete()
        await message.reply_text("**🚫 You're not authorized to use this command...**")
        return
    if len(message.command) != 2:
        await message.reply_text("**Usage: /remove {user_id}**")
        return
    k = int(message.command[1])
    await mdb.remove_premium(k)
    await message.reply_text(f"**User {k} has been removed from the Prime Plan**")
    await client.send_message(chat_id=k, text="**Your premium access has been removed by the admin.**")

@Client.on_message(filters.command("setlimit") & filters.private)
async def set_limit(client, message):
    if message.from_user.id != ADMIN_ID:
        message.delete()
        await message.reply_text("**🚫 You're not authorized to use this command...**")
        return
    if len(message.command) != 3:
        await message.reply_text("**Usage: /setlimit {free / prime} {new_value}**")
        return
    limit_type = message.command[1].lower()
    try:
        new_value = int(message.command[2])
    except ValueError:
        await message.reply_text("**⚠️ Please provide a valid number for the new limit value**")
        return
    if limit_type not in ("free", "prime"):
        await message.reply_text("**⚠️ Invalid limit type. Use 'free' or 'prime'**")
        return
    await mdb.update_global_limit(limit_type, new_value)
    await message.reply_text(f"**✅ {limit_type.capitalize()} limit updated to {new_value} for all users**")
