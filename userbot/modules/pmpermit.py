# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.b (the "License");
# you may not use this file except in compliance with the License.
#

""" Userbot module for keeping control who PM you. """

from telethon.tl.functions.contacts import BlockRequest, UnblockRequest
from telethon.tl.functions.messages import ReportSpamRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import User

from userbot import (COUNT_PM, CMD_HELP, BOTLOG, BOTLOG_CHATID,
                     PM_AUTO_BAN, BRAIN_CHECKER, LASTMSG, LOGS, is_mongo_alive, is_redis_alive)

from userbot.modules.dbhelper import approval, approve, block_pm, notif_state, notif_off, notif_on

from userbot.events import register

# ========================= CONSTANTS ============================
UNAPPROVED_MSG = ("`Bleep blop! This is a bot. Don't fret.`\n\n"
                  "`My master hasn't approved you to PM.`"
                  "`Please wait for my master to look in, he mostly approves PMs.`\n\n"
                  "`As far as I know, he doesn't usually approve retards though.`")
# =================================================================


@register(incoming=True, disable_edited=True)
async def permitpm(event):
    """ Permits people from PMing you without approval. \
        Will block retarded nibbas automatically. """
    if PM_AUTO_BAN:
        if event.sender_id in BRAIN_CHECKER:
            return
        if event.is_private and not (await event.get_sender()).bot:
            if not is_mongo_alive() or not is_redis_alive():
                return
            apprv = await approval(event.chat_id)

            # This part basically is a sanity check
            # If the message that sent before is Unapproved Message
            # then stop sending it again to prevent FloodHit
            if not apprv and event.text != UNAPPROVED_MSG:
                if event.chat_id in LASTMSG:
                    prevmsg = LASTMSG[event.chat_id]
                    # If the message doesn't same as previous one
                    # Send the Unapproved Message again
                    if event.text != prevmsg:
                        await event.reply(UNAPPROVED_MSG)
                    LASTMSG.update({event.chat_id: event.text})
                else:
                    await event.reply(UNAPPROVED_MSG)
                    LASTMSG.update({event.chat_id: event.text})

                if await notif_state() is False:
                    await event.client.send_read_acknowledge(event.chat_id)
                if event.chat_id not in COUNT_PM:
                    COUNT_PM.update({event.chat_id: 1})
                else:
                    COUNT_PM[event.chat_id] = COUNT_PM[event.chat_id] + 1

                if COUNT_PM[event.chat_id] > 4:
                    await event.respond(
                        "`You were spamming my master's PM, which I don't like.`"
                        " `I'mma Report Spam.`"
                    )

                    try:
                        del COUNT_PM[event.chat_id]
                        del LASTMSG[event.chat_id]
                    except KeyError:
                        if BOTLOG:
                             await event.client.send_message(
                              BOTLOG_CHATID,
                              "Count PM is seemingly going retard, plis restart bot!",
                              )
                        LOGS.info("CountPM wen't rarted boi")
                        return

                    await event.client(BlockRequest(event.chat_id))
                    await event.client(ReportSpamRequest(peer=event.chat_id))

                    if BOTLOG:
                        name = await event.client.get_entity(event.chat_id)
                        name0 = str(name.first_name)
                        await event.client.send_message(
                            BOTLOG_CHATID,
                            "["
                            + name0
                            + "](tg://user?id="
                            + str(event.chat_id)
                            + ")"
                            + " was just another retarded nibba",
                        )

@register(disable_edited=True, outgoing=True)
async def auto_accept(event):
    """ Will approve automatically if you texted them first. """
    if event.is_private and not (await event.get_sender()).bot:
        if not is_mongo_alive() or not is_redis_alive():
            return
        chat = await event.get_chat()
        if isinstance(chat, User):
            if is_approved(event.chat_id):
                return
            async for message in event.client.iter_messages(chat.id, reverse=True, limit=1):
                if message.from_id == (await event.client.get_me()).id:
                    approve(chat.id)
                if BOTLOG:
                    await event.client.send_message(
                        BOTLOG_CHATID,
                        "#AUTO-APPROVED\n"
                        + "User: " + f"[{chat.first_name}](tg://user?id={chat.id})",
                    )

@register(outgoing=True, pattern="^.notifoff$")
async def notifoff(noff_event):
    """ For .notifoff command, stop getting notifications from unapproved PMs. """
    if not noff_event.text[0].isalpha() and noff_event.text[0] not in ("/", "#", "@", "!"):
        if await notif_off() is False:
            return await noff_event.edit('`Notifications already silenced!`')
        else:
            return await noff_event.edit("`Notifications silenced!`")


@register(outgoing=True, pattern="^.notifon$")
async def notifon(non_event):
    """ For .notifoff command, get notifications from unapproved PMs. """
    if not non_event.text[0].isalpha() and non_event.text[0] not in ("/", "#", "@", "!"):
        if await notif_on() is False:
            return await non_event.edit("`Notifications ain't muted!")
        else:
            return await non_event.edit("`Notifications unmuted!`")


@register(outgoing=True, pattern="^.approve$")
async def approvepm(apprvpm):
    """ For .approve command, give someone the permissions to PM you. """
    if not apprvpm.text[0].isalpha() and apprvpm.text[0] not in ("/", "#", "@", "!"):
        if not is_mongo_alive() or not is_redis_alive():
            await apprvpm.edit("`Database connections failing!`")
            return

        if await approve(apprvpm.chat_id) == False:
            return await apprvpm.edit("`User was already approved!`")
        else:
            if apprvpm.reply_to_msg_id:
                reply = await apprvpm.get_reply_message()
                replied_user = await apprvpm.client(GetFullUserRequest(reply.from_id))
                aname = replied_user.user.id
                name0 = str(replied_user.user.first_name)
                uid = replied_user.user.id
    
            else:
                aname = await apprvpm.client.get_entity(apprvpm.chat_id)
                name0 = str(aname.first_name)
                uid = apprvpm.chat_id
    
            await apprvpm.edit(
                    f"[{name0}](tg://user?id={uid}) `approved to PM!`"
            )
    
            if BOTLOG:
                await apprvpm.client.send_message(
                    BOTLOG_CHATID,
                    "#APPROVED\n"
                    + "User: " + f"[{name0}](tg://user?id={uid})",
                )


@register(outgoing=True, pattern="^.block$")
async def blockpm(block):
    """ For .block command, block people from PMing you! """
    if not block.text[0].isalpha() and block.text[0] not in ("/", "#", "@", "!"):
        await block.edit("`You are gonna be blocked from PM-ing my Master!`")

        if await block_pm(block.chat_id) is False:
            return await block.edit("`First approve, before blocc'ing`")
        else:
            return await block.edit("`Blocked.`")

            if block.reply_to_msg_id:
                reply = await block.get_reply_message()
                replied_user = await block.client(GetFullUserRequest(reply.from_id))
                aname = replied_user.user.id
                name0 = str(replied_user.user.first_name)
                await block.client(BlockRequest(replied_user.user.id))
                uid = replied_user.user.id
            else:
                await block.client(BlockRequest(block.chat_id))
                aname = await block.client.get_entity(block.chat_id)
                name0 = str(aname.first_name)
                uid = block.chat_id
    
            if not is_mongo_alive() or not is_redis_alive():
                await block.edit("`Database connections failing!`")
                return
            if BOTLOG:
                await block.client.send_message(
                    BOTLOG_CHATID,
                    "#BLOCKED\n"
                    + "User: " + f"[{name0}](tg://user?id={uid})",
                )


@register(outgoing=True, pattern="^.unblock$")
async def unblockpm(unblock):
    """ For .unblock command, let people PMing you again! """
    if not unblock.text[0].isalpha() and unblock.text[0] \
            not in ("/", "#", "@", "!") and unblock.reply_to_msg_id:
        if unblock.reply_to_msg_id:
            reply = await unblock.get_reply_message()
            replied_user = await unblock.client(GetFullUserRequest(reply.from_id))
            name0 = str(replied_user.user.first_name)
            if await approve(reply.from_id) == False:
                return await unblock.edit("`You haven't blocked this user yet!`")
            else:
                return await unblock.edit("`My Master has forgiven you to PM now`")

            await unblock.client(UnblockRequest(replied_user.user.id))

        if BOTLOG:
            await unblock.client.send_message(
                BOTLOG_CHATID,
                f"[{name0}](tg://user?id={replied_user.user.id})"
                " was unblocc'd!.",
            )

CMD_HELP.update({
    "pmpermit": "\
.approve\
\nUsage: Approves the mentioned/replied person to PM.\
\n\n.block\
\nUsage: Blocks the person from PMing you.\
\n\n.unblock\
\nUsage: Unblocks the person so they can PM you.\
\n\n.notifoff\
\nUsage: Clears any notifications of unapproved PMs.\
\n\n.notifon\
\nUsage: Allows notifications for unapproved PMs.\
"
})
