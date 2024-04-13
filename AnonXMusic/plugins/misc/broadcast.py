import asyncio

from pyrogram import filters
from pyrogram.enums import ChatMembersFilter
from pyrogram.errors import FloodWait

from AnonXMusic import app
from config import adminlist
from AnonXMusic.misc import SUDOERS
from AnonXMusic.utils.database import (
    get_active_chats,
    get_authuser_names,
    get_served_chats,
    get_served_users,
)
from AnonXMusic.utils.decorators.language import language
from AnonXMusic.utils.formatters import alpha_to_int

IS_BROADCASTING = False


@app.on_message(filters.command("broadcast") & SUDOERS)
@language
async def braodcast_message(client, message, _):
    global IS_BROADCASTING
    if message.reply_to_message:
        x = message.reply_to_message.id
        y = message.chat.id
    else:
        if len(message.command) < 2:
            return await message.reply_text(_["broad_1"])
        query = message.text.split(None, 1)[1]
        if "-pin" in query:
            query = query.replace("-pin", "")
        if "-nobot" in query:
            query = query.replace("-nobot", "")
        if "-pinloud" in query:
            query = query.replace("-pinloud", "")
        if "-user" in query:
            query = query.replace("-user", "")
        if "-noforward" in query:
            query = query.replace("-noforward", "")
        if query == "":
            return await message.reply_text(_["broad_1"])

    IS_BROADCASTING = True

    if "-nobot" not in message.text:
        sent = 0
        pin = 0
        chats = []
        schats = await get_served_chats()
        for chat in schats:
            chats.append(int(chat["chat_id"]))
        for i in chats:
            try:
                if "-noforward" in message.text and message.reply_to_message:
                    m = await app.copy_message(
                        chat_id=i,
                        from_chat_id=y,
                        message_id=x,
                        reply_markup=message.reply_to_message.reply_markup,
                    )
                    if "-pin" in message.text:
                        try:
                            await m.pin(disable_notification=True)
                            pin += 1
                        except:
                            continue
                    elif "-pinloud" in message.text:
                        try:
                            await m.pin(disable_notification=False)
                            pin += 1
                        except:
                            continue
                    sent += 1
                else:
                    m = (
                        await app.forward_messages(i, y, x)
                        if message.reply_to_message
                        else await app.send_message(i, text=query)
                    )
                    if "-pin" in message.text:
                        try:
                            await m.pin(disable_notification=True)
                            pin += 1
                        except:
                            continue
                    elif "-pinloud" in message.text:
                        try:
                            await m.pin(disable_notification=False)
                            pin += 1
                        except:
                            continue
                    sent += 1
            except FloodWait as e:
                flood_time = int(e.value)
                if flood_time > 200:
                    continue
                await asyncio.sleep(flood_time)
            except:
                continue
        try:
            await message.reply_text(_["broad_2"].format(sent, pin))
        except:
            pass

    if "-user" in message.text:
        susr = 0
        served_users = []
        susers = await get_served_users()
        for user in susers:
            served_users.append(int(user["user_id"]))
        for i in served_users:
            try:
                if "-noforward" in message.text and message.reply_to_message:
                    await app.copy_message(
                        chat_id=i,
                        from_chat_id=y,
                        message_id=x,
                        reply_markup=message.reply_to_message.reply_markup,
                    )
                    susr += 1
                else:
                    m = (
                        await app.forward_messages(i, y, x)
                        if message.reply_to_message
                        else await app.send_message(i, text=query)
                    )
                    susr += 1
            except FloodWait as e:
                flood_time = int(e.value)
                if flood_time > 200:
                    continue
                await asyncio.sleep(flood_time)
            except:
                continue
        try:
            await message.reply_text(_["broad_3"].format(susr))
        except:
            pass
    IS_BROADCASTING = False


async def auto_clean():
    while not await asyncio.sleep(10):
        try:
            served_chats = await get_active_chats()
            for chat_id in served_chats:
                if chat_id not in adminlist:
                    adminlist[chat_id] = []
                    async for user in app.get_chat_members(
                        chat_id, filter=ChatMembersFilter.ADMINISTRATORS
                    ):
                        if user.privileges.can_manage_video_chats:
                            adminlist[chat_id].append(user.user.id)
                    authusers = await get_authuser_names(chat_id)
                    for user in authusers:
                        user_id = await alpha_to_int(user)
                        adminlist[chat_id].append(user_id)
        except:
            continue


asyncio.create_task(auto_clean())
