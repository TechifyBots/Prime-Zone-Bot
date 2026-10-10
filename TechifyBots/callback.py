import random
from pyrogram import Client, enums
from Script import text
from config import ADMIN_ID, PICS, VERSION
from Database.maindb import mdb
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    WebAppInfo,
)

@Client.on_callback_query()
async def callback_query_handler(client, query: CallbackQuery):
    try:
        if query.data == "start":
            await query.message.edit_media(
                InputMediaPhoto(
                    media=random.choice(PICS),
                    caption=text.START.format(query.from_user.mention)
            ),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("ℹ️ 𝖠𝖻𝗈𝗎𝗍", callback_data="about"),
                     InlineKeyboardButton("📚 𝖧𝖾𝗅𝗉", callback_data="help")],
                    [InlineKeyboardButton("🍿 𝖡𝗎𝗒 𝖲𝗎𝖻𝗌𝖼𝗋𝗂𝗉𝗍𝗂𝗈𝗇 🍾", callback_data="pro", style=enums.ButtonStyle.PRIMARY)]
                ])
            )

        elif query.data == "help":
            await query.message.edit_media(
                InputMediaPhoto(
                    media=random.choice(PICS),
                    caption=text.HELP
                ),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("📢 𝖠𝖽𝗆𝗂𝗇 𝖢𝗈𝗆𝗆𝖺𝗇𝖽𝗌", callback_data="admincmds")],
                    [InlineKeyboardButton("↩️ 𝖡𝖺𝖼𝗄", callback_data="start", style=enums.ButtonStyle.PRIMARY),
                     InlineKeyboardButton("❌ 𝖢𝗅𝗈𝗌𝖾", callback_data="close", style=enums.ButtonStyle.DANGER)]
                ])
            )

        elif query.data == "about":
            await query.message.edit_media(
                InputMediaPhoto(
                    media=random.choice(PICS),
                    caption=text.ABOUT.format(VERSION)
                ),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("📂 𝖲𝗈𝗎𝗋𝖼𝖾 𝖢𝗈𝖽𝖾", url="https://github.com/TechifyBots/Prime-Zone-Bot")],
                    [InlineKeyboardButton("☕ 𝖣𝗈𝗇𝖺𝗍𝖾", callback_data="donate"),
                     InlineKeyboardButton("👨‍💻 𝖢𝗋𝖾𝖺𝗍𝗈𝗋", user_id=int(ADMIN_ID))],
                    [InlineKeyboardButton("↩️ 𝖡𝖺𝖼𝗄", callback_data="start", style=enums.ButtonStyle.PRIMARY)]
                ])
            )

        elif query.data == "donate":
            await query.message.edit_media(
                InputMediaPhoto(
                    media=random.choice(PICS),
                    caption=text.DONATE
                ),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("💳 𝖲𝗎𝗉𝗉𝗈𝗋𝗍 𝖳𝗁𝖾 𝖣𝖾𝗏𝖾𝗅𝗈𝗉𝖾𝗋", web_app=WebAppInfo(url="https://techifybots.vercel.app/pay"))],
                    [InlineKeyboardButton("↩️ 𝖡𝖺𝖼𝗄", callback_data="about", style=enums.ButtonStyle.PRIMARY),
                     InlineKeyboardButton("❌ 𝖢𝗅𝗈𝗌𝖾", callback_data="close", style=enums.ButtonStyle.DANGER)]
                ])
            )

        elif query.data == "pro":
            current_limits = await mdb.get_global_limits()
            pro_text = text.PRO.format(free_limit=current_limits['free_limit'], prime_limit=current_limits['prime_limit'])
            await query.message.edit_media(
                InputMediaPhoto(
                    media=random.choice(PICS),
                    caption=pro_text
                ),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("💳 𝖴𝗉𝗀𝗋𝖺𝖽𝖾 / 𝖯𝖺𝗒𝗆𝖾𝗇𝗍", user_id=int(ADMIN_ID))],
                    [InlineKeyboardButton("↩️ 𝖡𝖺𝖼𝗄", callback_data="start", style=enums.ButtonStyle.PRIMARY),
                     InlineKeyboardButton("❌ 𝖢𝗅𝗈𝗌𝖾", callback_data="close", style=enums.ButtonStyle.DANGER)]
                ])
            )

        elif query.data == "admincmds":
            if query.from_user.id != ADMIN_ID:
                await query.answer("You are not my admin ❌", show_alert=True)
            else:
                await query.message.edit_media(
                    InputMediaPhoto(
                        media=random.choice(PICS),
                        caption=text.ADMIN_COMMANDS
                    ),
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("↩️ 𝖡𝖺𝖼𝗄", callback_data="help", style=enums.ButtonStyle.PRIMARY)]
                    ])
                )

        elif query.data == "close":
            await query.message.delete()

    except Exception as e:
        print(f"Callback error: {e}")
        await query.answer("⚠️ An error occurred. Try again later.", show_alert=True)
