# Copyright (C) 2020 by UsergeTeam@Github, < https://github.com/UsergeTeam >.
#
# This file is part of < https://github.com/UsergeTeam/Userge > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/uaudith/Userge/blob/master/LICENSE >
#
# All rights reserved.


import os
import time
import asyncio

from emoji import get_emoji_regexp
from pyrogram import ChatPermissions
from pyrogram.errors import (FloodWait,
                             UserAdminInvalid,
                             UsernameInvalid,
                             ChatAdminRequired,
                             PeerIdInvalid,
                             UserIdInvalid)

from userge import userge, Message

CHANNEL = userge.getCLogger(__name__)


async def is_admin(message: Message):
    check_user = await userge.get_chat_member(message.chat.id, message.from_user.id)
    user_type = check_user.status
    if user_type == "member":
        return False
    if user_type == "administrator":
        rm_perm = check_user.can_restrict_members
        if rm_perm:
            return True
        return False
    return True


async def is_sudoadmin(message: Message):
    check_user = await userge.get_chat_member(message.chat.id, message.from_user.id)
    user_type = check_user.status
    if user_type == "member":
        return False
    if user_type == "administrator":
        add_adminperm = check_user.can_promote_members
        if add_adminperm:
            return True
        return False
    return True


@userge.on_cmd("promote", about={
    'header': "use this to promote group members",
    'description': "Provides admin rights to the person in the supergroup.\n"
                   "you can also add custom title while promoting new admin.\n"
                   "[NOTE: Requires proper admin rights in the chat!!!]",
    'examples': [
        "{tr}promote [username | userid] or [reply to user] :custom title (optional)",
        "{tr}promote @someusername/userid/replytouser Staff (custom title)"]})
async def promote_usr(message: Message):
    """
    this function can promote members in tg group
    """
    custom_rank = ""
    chat_id = message.chat.id
    get_group = await userge.get_chat(chat_id)
    can_promo = await is_sudoadmin(message)

    if can_promo:

        await message.edit("`Trying to Promote User.. Hang on!! ⏳`")

        if message.reply_to_message:
            user_id = message.reply_to_message.from_user.id
            custom_rank = get_emoji_regexp().sub(u'', message.input_str)

            if len(custom_rank) > 15:
                custom_rank = custom_rank[:15]

        else:
            args = message.input_str.split(maxsplit=1)

            if len(args) == 2:
                user_id, custom_rank = args
                custom_rank = get_emoji_regexp().sub(u'', custom_rank)

                if len(custom_rank) > 15:
                    custom_rank = custom_rank[:15]

            elif len(args) == 1:
                user_id = args[0]

            else:
                await message.edit(
                    text="`no valid user_id or message specified,`"
                    "`do .help promote for more info`", del_in=0)
                return

        if user_id:

            try:
                get_mem = await userge.get_chat_member(chat_id, user_id)
                await userge.promote_chat_member(chat_id, user_id,
                                                 can_change_info=True,
                                                 can_delete_messages=True,
                                                 can_restrict_members=True,
                                                 can_invite_users=True,
                                                 can_pin_messages=True)

                await asyncio.sleep(2)

                await userge.set_administrator_title(chat_id, user_id, custom_rank)

                await message.edit("`👑 Promoted Successfully..`", del_in=0)

                await CHANNEL.log(
                    f"#PROMOTE\n\n"
                    f"USER: [{get_mem.user.first_name}](tg://user?id={get_mem.user.id}) "
                    f"(`{get_mem.user.id}`)\n"
                    f"CUSTOM TITLE: `{custom_rank}`\n"
                    f"CHAT: `{get_group.title}` (`{chat_id}`)")

            except UsernameInvalid:
                await message.edit(
                    text="`invalid username, try again with valid info ⚠`", del_in=0
                    )
                return

            except PeerIdInvalid:
                await message.edit(
                    text="`invalid username or userid, try again with valid info ⚠`", del_in=0
                    )
                return

            except UserIdInvalid:
                await message.edit(
                    text="`invalid userid, try again with valid info ⚠`", del_in=0
                    )
                return

            except ChatAdminRequired:
                await message.edit(
                    text=r"`i don't have permission to do that ＞︿＜`", del_in=0
                    )
                return

            except Exception as e_f:
                await message.edit(
                    text="`something went wrong! 🤔`\n\n"
                    f"**ERROR:** `{e_f}`"
                )
                return

    else:
        await message.edit(
            text=r"`i don't have proper permission to do that! (* ￣︿￣)`", del_in=0)


@userge.on_cmd("demote", about={
    'header': "use this to demote group members",
    'description': "Remove admin rights from admin in the supergroup.\n"
                   "[NOTE: Requires proper admin rights in the chat!!!]",
    'examples': "{tr}demote [username | userid] or [reply to user]"})
async def demote_usr(message: Message):
    """
    this function can demote members in tg group
    """
    chat_id = message.chat.id
    get_group = await userge.get_chat(chat_id)
    can_demote = await is_sudoadmin(message)

    if can_demote:

        await message.edit("`Trying to Demote User.. Hang on!! ⏳`")

        user_id = message.input_str

        if user_id:

            try:
                get_mem = await userge.get_chat_member(chat_id, user_id)
                await userge.promote_chat_member(chat_id, user_id,
                                                 can_change_info=False,
                                                 can_delete_messages=False,
                                                 can_restrict_members=False,
                                                 can_invite_users=False,
                                                 can_pin_messages=False)

                await message.edit("`🛡 Demoted Successfully..`", del_in=0)
                await CHANNEL.log(
                    f"#DEMOTE\n\n"
                    f"USER: [{get_mem.user.first_name}](tg://user?id={get_mem.user.id}) "
                    f"(`{get_mem.user.id}`)\n"
                    f"CHAT: `{get_group.title}` (`{chat_id}`)")

            except UsernameInvalid:
                await message.edit(
                    text="`invalid username, try again with valid info ⚠`", del_in=0
                    )
                return

            except PeerIdInvalid:
                await message.edit(
                    text="`invalid username or userid, try again with valid info ⚠`", del_in=0
                    )
                return

            except UserIdInvalid:
                await message.edit(
                    text="`invalid userid, try again with valid info ⚠`", del_in=0
                    )
                return

            except ChatAdminRequired:
                await message.edit(
                    text=r"`i don't have permission to do that ＞︿＜`", del_in=0
                    )
                return

            except Exception as e_f:
                await message.edit(
                    text="`something went wrong! 🤔`\n\n"
                    f"**ERROR:** `{e_f}`", del_in=0
                )
                return

        elif message.reply_to_message:

            try:
                get_mem = await userge.get_chat_member(
                    chat_id,
                    message.reply_to_message.from_user.id
                    )
                await userge.promote_chat_member(chat_id, get_mem.user.id,
                                                 can_change_info=False,
                                                 can_delete_messages=False,
                                                 can_restrict_members=False,
                                                 can_invite_users=False,
                                                 can_pin_messages=False)

                await message.edit("`🛡 Demoted Successfully..`", del_in=0)
                await CHANNEL.log(
                    f"#DEMOTE\n\n"
                    f"USER: [{get_mem.user.first_name}](tg://user?id={get_mem.user.id}) "
                    f"(`{get_mem.user.id}`)\n"
                    f"CHAT: `{get_group.title}` (`{chat_id}`)")

            except ChatAdminRequired:
                await message.edit(
                    text=r"`i don't have permission to do that ＞︿＜`", del_in=0
                    )
                return

            except Exception as e_f:
                await message.edit(
                    text="`something went wrong! 🤔`\n\n"
                    f"**ERROR:** `{e_f}`", del_in=0
                )
                return

        else:
            await message.edit(
                text="`no valid user_id or message specified,`"
                "`do .help demote for more info` ⚠", del_in=0)

            return

    else:
        await message.edit(
            text=r"`i don't have proper permission to do that! (* ￣︿￣)`", del_in=0)


@userge.on_cmd("ban", about={
    'header': "use this to ban group members",
    'description': "Ban member from supergroup.\n"
                   "[NOTE: Requires proper admin rights in the chat!!!]",
    'examples': "{tr}ban [username | userid] or [reply to user] :reason (optional)"})
async def ban_usr(message: Message):
    """
    this function can ban user from tg group
    """
    reason = ""
    chat_id = message.chat.id
    get_group = await userge.get_chat(chat_id)
    can_ban = await is_admin(message)

    if can_ban:

        await message.edit("`Trying to Ban User.. Hang on!! ⏳`")

        if message.reply_to_message:
            user_id = message.reply_to_message.from_user.id
            reason = message.input_str
        else:
            args = message.input_str.split(maxsplit=1)
            if len(args) == 2:
                user_id, reason = args
            elif len(args) == 1:
                user_id = args[0]
            else:
                await message.edit(
                    text="`no valid user_id or message specified,`"
                    "`do .help ban for more info` ⚠", del_in=0)
                return

        if user_id:

            try:
                get_mem = await userge.get_chat_member(chat_id, user_id)
                await userge.kick_chat_member(chat_id, user_id)
                await message.edit(
                    f"#BAN\n\n"
                    f"USER: [{get_mem.user.first_name}](tg://user?id={get_mem.user.id}) "
                    f"(`{get_mem.user.id}`)\n"
                    f"CHAT: `{get_group.title}` (`{chat_id}`)\n"
                    f"REASON: `{reason}`", log=True)

            except UsernameInvalid:
                await message.edit(
                    text="`invalid username, try again with valid info ⚠`", del_in=0
                    )
                return

            except PeerIdInvalid:
                await message.edit(
                    text="`invalid username or userid, try again with valid info ⚠`", del_in=0
                    )
                return

            except UserIdInvalid:
                await message.edit(
                    text="`invalid userid, try again with valid info ⚠`", del_in=0
                    )
                return

            except ChatAdminRequired:
                await message.edit(
                    text=r"`i don't have permission to do that ＞︿＜`", del_in=0
                    )
                return

            except Exception as e_f:
                await message.edit(
                    text="`something went wrong! 🤔`\n\n"
                    f"**ERROR:** `{e_f}`", del_in=0
                )
                return

    else:
        await message.edit(
            text=r"`i don't have proper permission to do that! (* ￣︿￣)`", del_in=0)


@userge.on_cmd("unban", about={
    'header': "use this to unban group members",
    'description': "Unban member from supergroup.\n"
                   "[NOTE: Requires proper admin rights in the chat!!!]",
    'examples': "{tr}unban [username | userid] or [reply to user]"})
async def unban_usr(message: Message):
    """
    this function can unban user from tg group
    """
    chat_id = message.chat.id
    get_group = await userge.get_chat(chat_id)
    can_unban = await is_admin(message)

    if can_unban:

        await message.edit("`Trying to Unban User.. Hang on!! ⏳`")

        user_id = message.input_str

        if user_id:

            try:
                get_mem = await userge.get_chat_member(chat_id, user_id)
                await userge.unban_chat_member(chat_id, user_id)
                await message.edit("`🛡 Successfully Unbanned..`", del_in=0)
                await CHANNEL.log(
                    f"#UNBAN\n\n"
                    f"USER: [{get_mem.user.first_name}](tg://user?id={get_mem.user.id}) "
                    f"(`{get_mem.user.id}`)\n"
                    f"CHAT: `{get_group.title}` (`{chat_id}`)")

            except UsernameInvalid:
                await message.edit(
                    text="`invalid username, try again with valid info ⚠`", del_in=0
                    )
                return

            except PeerIdInvalid:
                await message.edit(
                    text="`invalid username or userid, try again with valid info ⚠`", del_in=0
                    )
                return

            except UserIdInvalid:
                await message.edit(
                    text="`invalid userid, try again with valid info ⚠`", del_in=0
                    )
                return

            except Exception as e_f:
                await message.edit(
                    text="`something went wrong! 🤔`\n\n"
                    f"**ERROR:** `{e_f}`", del_in=0
                )
                return

        elif message.reply_to_message:

            try:
                get_mem = await userge.get_chat_member(
                    chat_id,
                    message.reply_to_message.from_user.id
                    )
                await userge.unban_chat_member(chat_id, get_mem.user.id)
                await message.edit("`🛡 Successfully Unbanned..`", del_in=0)
                await CHANNEL.log(
                    f"#UNBAN\n\n"
                    f"USER: [{get_mem.user.first_name}](tg://user?id={get_mem.user.id}) "
                    f"(`{get_mem.user.id}`)\n"
                    f"CHAT: `{get_group.title}` (`{chat_id}`)")

            except Exception as e_f:
                await message.edit(
                    text="`something went wrong 🤔,`\n\n"
                    f"**ERROR:** `{e_f}`", del_in=0
                    )
                return

        else:
            await message.edit(
                text="`no valid user_id or message specified,`"
                "`do .help unban for more info` ⚠", del_in=0)

            return

    else:
        await message.edit(
            text=r"`i don't have proper permission to do that! (* ￣︿￣)`", del_in=0)


@userge.on_cmd("kick", about={
    'header': "use this to kick group members",
    'description': "Kick member from supergroup. member can rejoin the group again if they want.\n"
                   "[NOTE: Requires proper admin rights in the chat!!!]",
    'examples': "{tr}kick [username | userid] or [reply to user]"})
async def kick_usr(message: Message):
    """
    this function can kick user from tg group
    """
    chat_id = message.chat.id
    get_group = await userge.get_chat(chat_id)
    can_kick = await is_admin(message)

    if can_kick:

        await message.edit("`Trying to Kick User.. Hang on!! ⏳`")

        user_id = message.input_str

        if user_id:

            try:
                get_mem = await userge.get_chat_member(chat_id, user_id)
                await userge.kick_chat_member(chat_id, user_id, int(time.time() + 60))
                await message.edit(
                    f"#KICK\n\n"
                    f"USER: [{get_mem.user.first_name}](tg://user?id={get_mem.user.id}) "
                    f"(`{get_mem.user.id}`)\n"
                    f"CHAT: `{get_group.title}` (`{chat_id}`)", log=True)

            except UsernameInvalid:
                await message.edit(
                    text="`invalid username, try again with valid info ⚠`", del_in=0
                    )
                return

            except PeerIdInvalid:
                await message.edit(
                    text="`invalid username or userid, try again with valid info ⚠`", del_in=0
                    )
                return

            except UserIdInvalid:
                await message.edit(
                    text="`invalid userid, try again with valid info ⚠`", del_in=0
                    )
                return

            except ChatAdminRequired:
                await message.edit(
                    text=r"`i don't have permission to do that ＞︿＜`", del_in=0
                    )
                return

            except Exception as e_f:
                await message.edit(
                    text="`something went wrong! 🤔`\n\n"
                    f"**ERROR:** `{e_f}`", del_in=0
                )
                return

        elif message.reply_to_message:

            try:
                get_mem = await userge.get_chat_member(
                    chat_id,
                    message.reply_to_message.from_user.id
                    )
                await userge.kick_chat_member(chat_id, get_mem.user.id, int(time.time() + 45))
                await message.edit(
                    f"#KICK\n\n"
                    f"USER: [{get_mem.user.first_name}](tg://user?id={get_mem.user.id}) "
                    f"(`{get_mem.user.id}`)\n"
                    f"CHAT: `{get_group.title}` (`{chat_id}`)", log=True)

            except ChatAdminRequired:
                await message.edit(
                    text=r"`i don't have permission to do that ＞︿＜`", del_in=0
                    )
                return

            except Exception as e_f:
                await message.edit(
                    text="`something went wrong! 🤔`\n\n"
                    f"**ERROR:** `{e_f}`", del_in=0
                )
                return

        else:
            await message.edit(
                text="`no valid user_id or message specified,`"
                "`do .help kick for more info` ⚠", del_in=0)

            return

    else:
        await message.edit(
            text=r"`i don't have proper permission to do that! (* ￣︿￣)`", del_in=0)


@userge.on_cmd("mute", about={
    'header': "use this to mute group members",
    'description': "Mute member in the supergroup. you can only use one flag for command.\n"
                   "[NOTE: Requires proper admin rights in the chat!!!]",
    'flags': {
        '-m': "minutes",
        '-h': "hours",
        '-d': "days"},
    'examples': [
        "{tr}mute -flag [username | userid] or [reply to user] :reason (optional)",
        "{tr}mute -d1 @someusername/userid/replytouser SPAM (mute for one day:reason SPAM)"]})
async def mute_usr(message: Message):
    """
    this function can mute user from tg group
    """
    reason = ""
    chat_id = message.chat.id
    flags = message.flags
    get_group = await userge.get_chat(chat_id)
    can_mute = await is_admin(message)

    minutes = flags.get('-m', 0)
    hours = flags.get('-h', 0)
    days = flags.get('-d', 0)

    if can_mute:

        await message.edit("`Trying to Mute User.. Hang on!! ⏳`")

        if message.reply_to_message:
            user_id = message.reply_to_message.from_user.id
            reason = message.filtered_input_str
        else:
            args = message.filtered_input_str.split(maxsplit=1)
            if len(args) == 2:
                user_id, reason = args
            elif len(args) == 1:
                user_id = args[0]
            else:
                await message.edit(
                    text="`no valid user_id or message specified,`"
                    "`do .help mute for more info`", del_in=0)
                return

        if minutes:

            try:
                get_mem = await userge.get_chat_member(chat_id, user_id)
                mute_period = int(minutes) * 60
                await userge.restrict_chat_member(chat_id, user_id,
                                                  ChatPermissions(),
                                                  int(time.time() + mute_period))
                await message.edit(
                    f"#MUTE\n\n"
                    f"USER: [{get_mem.user.first_name}](tg://user?id={get_mem.user.id}) "
                    f"(`{get_mem.user.id}`)\n"
                    f"CHAT: `{get_group.title}` (`{chat_id}`)\n"
                    f"MUTE UNTIL: `{minutes} minutes`\n"
                    f"REASON: `{reason}`", log=True)

            except UsernameInvalid:
                await message.edit(
                    text="`invalid username, try again with valid info ⚠`", del_in=0
                    )
                return

            except PeerIdInvalid:
                await message.edit(
                    text="`invalid username or userid, try again with valid info ⚠`", del_in=0
                    )
                return

            except UserIdInvalid:
                await message.edit(
                    text="`invalid userid, try again with valid info ⚠`", del_in=0
                    )
                return

            except ChatAdminRequired:
                await message.edit(
                    text=r"`i don't have permission to do that ＞︿＜`", del_in=0
                    )
                return

            except Exception as e_f:
                await message.edit(
                    text=f"`something went wrong 🤔,`"
                    f"`do .help mute for more info`\n\n"
                    f"**ERROR**: `{e_f}`", del_in=0)
                return

        elif hours:

            try:
                get_mem = await userge.get_chat_member(chat_id, user_id)
                mute_period = int(hours) * 3600
                await userge.restrict_chat_member(chat_id, user_id,
                                                  ChatPermissions(),
                                                  int(time.time() + mute_period))
                await message.edit(
                    f"#MUTE\n\n"
                    f"USER: [{get_mem.user.first_name}](tg://user?id={get_mem.user.id}) "
                    f"(`{get_mem.user.id}`)\n"
                    f"CHAT: `{get_group.title}` (`{chat_id}`)\n"
                    f"MUTE UNTIL: `{hours} hours`\n"
                    f"REASON: `{reason}`", log=True)

            except UsernameInvalid:
                await message.edit(
                    text="`invalid username, try again with valid info ⚠`", del_in=0
                    )
                return

            except PeerIdInvalid:
                await message.edit(
                    text="`invalid username or userid, try again with valid info ⚠`", del_in=0
                    )
                return

            except UserIdInvalid:
                await message.edit(
                    text="`invalid userid, try again with valid info ⚠`", del_in=0
                    )
                return

            except ChatAdminRequired:
                await message.edit(
                    text=r"`i don't have permission to do that ＞︿＜`", del_in=0
                    )
                return

            except Exception as e_f:
                await message.edit(
                    text=f"`something went wrong 🤔,`"
                    f"`do .help mute for more info`\n\n"
                    f"**ERROR**: `{e_f}`", del_in=0)
                return

        elif days:

            try:
                get_mem = await userge.get_chat_member(chat_id, user_id)
                mute_period = int(days) * 86400
                await userge.restrict_chat_member(chat_id, user_id,
                                                  ChatPermissions(),
                                                  int(time.time() + mute_period))
                await message.edit(
                    f"#MUTE\n\n"
                    f"USER: [{get_mem.user.first_name}](tg://user?id={get_mem.user.id}) "
                    f"(`{get_mem.user.id}`)\n"
                    f"CHAT: `{get_group.title}` (`{chat_id}`)\n"
                    f"MUTE UNTIL: `{days} days`\n"
                    f"REASON: `{reason}`", log=True)

            except UsernameInvalid:
                await message.edit(
                    text="`invalid username, try again with valid info ⚠`", del_in=0
                    )
                return

            except PeerIdInvalid:
                await message.edit(
                    text="`invalid username or userid, try again with valid info ⚠`", del_in=0
                    )
                return

            except UserIdInvalid:
                await message.edit(
                    text="`invalid userid, try again with valid info ⚠`", del_in=0
                    )
                return

            except ChatAdminRequired:
                await message.edit(
                    text=r"`i don't have permission to do that ＞︿＜`", del_in=0
                    )
                return

            except Exception as e_f:
                await message.edit(
                    text=f"`something went wrong 🤔,`"
                    f"`do .help mute for more info`\n\n"
                    f"**ERROR**: {e_f}", del_in=0)
                return

        else:

            try:
                get_mem = await userge.get_chat_member(chat_id, user_id)
                await userge.restrict_chat_member(chat_id, user_id, ChatPermissions())
                await message.edit(
                    f"#MUTE\n\n"
                    f"USER: [{get_mem.user.first_name}](tg://user?id={get_mem.user.id}) "
                    f"(`{get_mem.user.id}`)\n"
                    f"CHAT: `{get_group.title}` (`{chat_id}`)\n"
                    f"MUTE UNTIL: `forever`\n"
                    f"REASON: `{reason}`", log=True)

            except UsernameInvalid:
                await message.edit(
                    text="`invalid username, try again with valid info ⚠`", del_in=0
                    )
                return

            except PeerIdInvalid:
                await message.edit(
                    text="`invalid username or userid, try again with valid info ⚠`", del_in=0
                    )
                return

            except UserIdInvalid:
                await message.edit(
                    text="`invalid userid, try again with valid info ⚠`", del_in=0
                    )
                return

            except ChatAdminRequired:
                await message.edit(
                    text=r"`i don't have permission to do that ＞︿＜`", del_in=0
                    )
                return

            except Exception as e_f:
                await message.edit(
                    text=f"`something went wrong 🤔,`"
                    f"`do .help mute for more info`\n\n"
                    f"**ERROR**: {e_f}", del_in=0)

                return

    else:
        await message.edit(
            text=r"`i don't have proper permission to do that! (* ￣︿￣)`", del_in=0)


@userge.on_cmd("unmute", about={
    'header': "use this to unmute group members",
    'description': "Unmute member from supergroup.\n"
                   "[NOTE: Requires proper admin rights in the chat!!!]",
    'examples': "{tr}unmute [username | userid]  or [reply to user]"})
async def unmute_usr(message: Message):
    """
    this function can unmute user from tg group
    """
    chat_id = message.chat.id
    get_group = await userge.get_chat(chat_id)
    can_unmute = await is_admin(message)

    amsg = get_group.permissions.can_send_messages
    amedia = get_group.permissions.can_send_media_messages
    astickers = get_group.permissions.can_send_stickers
    aanimations = get_group.permissions.can_send_animations
    agames = get_group.permissions.can_send_games
    ainlinebots = get_group.permissions.can_use_inline_bots
    awebprev = get_group.permissions.can_add_web_page_previews
    apolls = get_group.permissions.can_send_polls
    ainfo = get_group.permissions.can_change_info
    ainvite = get_group.permissions.can_invite_users
    apin = get_group.permissions.can_pin_messages

    if can_unmute:

        await message.edit("`Trying to Unmute User.. Hang on!! ⏳`")

        user_id = message.input_str

        if user_id:

            try:
                get_mem = await userge.get_chat_member(chat_id, user_id)
                await userge.restrict_chat_member(chat_id, user_id,
                                                  ChatPermissions(
                                                      can_send_messages=amsg,
                                                      can_send_media_messages=amedia,
                                                      can_send_stickers=astickers,
                                                      can_send_animations=aanimations,
                                                      can_send_games=agames,
                                                      can_use_inline_bots=ainlinebots,
                                                      can_add_web_page_previews=awebprev,
                                                      can_send_polls=apolls,
                                                      can_change_info=ainfo,
                                                      can_invite_users=ainvite,
                                                      can_pin_messages=apin))

                await message.edit("`🛡 Successfully Unmuted..`", del_in=0)
                await CHANNEL.log(
                    f"#UNMUTE\n\n"
                    f"USER: [{get_mem.user.first_name}](tg://user?id={get_mem.user.id}) "
                    f"(`{get_mem.user.id}`)\n"
                    f"CHAT: `{get_group.title}` (`{chat_id}`)")

            except UsernameInvalid:
                await message.edit(
                    text="`invalid username, try again with valid info ⚠`", del_in=0
                    )
                return

            except PeerIdInvalid:
                await message.edit(
                    text="`invalid username or userid, try again with valid info ⚠`", del_in=0
                    )
                return

            except UserIdInvalid:
                await message.edit(
                    text="`invalid userid, try again with valid info ⚠`", del_in=0
                    )
                return

            except Exception as e_f:
                await message.edit(
                    text="`something went wrong!` 🤔\n\n"
                    f"**ERROR:** `{e_f}`", del_in=0
                )
                return

        elif message.reply_to_message:

            try:
                get_mem = await userge.get_chat_member(
                    chat_id,
                    message.reply_to_message.from_user.id
                    )
                await userge.restrict_chat_member(chat_id, get_mem.user.id,
                                                  ChatPermissions(
                                                      can_send_messages=amsg,
                                                      can_send_media_messages=amedia,
                                                      can_send_stickers=astickers,
                                                      can_send_animations=aanimations,
                                                      can_send_games=agames,
                                                      can_use_inline_bots=ainlinebots,
                                                      can_add_web_page_previews=awebprev,
                                                      can_send_polls=apolls,
                                                      can_change_info=ainfo,
                                                      can_invite_users=ainvite,
                                                      can_pin_messages=apin))

                await message.edit("`🛡 Successfully Unmuted..`", del_in=0)
                await CHANNEL.log(
                    f"#UNMUTE\n\n"
                    f"USER: [{get_mem.user.first_name}](tg://user?id={get_mem.user.id}) "
                    f"(`{get_mem.user.id}`)\n"
                    f"CHAT: `{get_group.title}` (`{chat_id}`)")

            except Exception as e_f:
                await message.edit(
                    text="`something went wrong! 🤔`\n\n"
                    f"**ERROR:** `{e_f}`", del_in=0
                )
                return

        else:
            await message.edit(
                text="`no valid user_id or message specified,`"
                "`do .help unmute for more info`", del_in=0)

            return

    else:
        await message.edit(
            text=r"`i don't have proper permission to do that! (* ￣︿￣)`", del_in=0)


@userge.on_cmd("zombies", about={
    'header': "use this to clean zombie accounts",
    'description': "check & remove zombie (deleted) accounts from supergroup.\n"
                   "[NOTE: Requires proper admin rights in the chat!!!]",
    'flags': {'-c': "clean"},
    'examples': [
        "{tr}zombies [check deleted accounts in group]",
        "{tr}zombies -c [remove deleted accounts from group]"]})
async def zombie_clean(message: Message):
    """
    this function can remove deleted accounts from tg group
    """
    chat_id = message.chat.id
    get_group = await userge.get_chat(chat_id)
    flags = message.flags

    rm_delaccs = '-c' in flags

    can_clean = await is_admin(message)

    if rm_delaccs:

        del_users = 0
        del_admins = 0
        del_total = 0
        del_stats = r"`Zero zombie accounts found in this chat... WOOHOO group is clean.. \^o^/`"

        if can_clean:

            await message.edit("`Hang on!! cleaning zombie accounts from this chat..`")
            async for member in userge.iter_chat_members(chat_id):

                if member.user.is_deleted:

                    try:
                        await userge.kick_chat_member(
                            chat_id,
                            member.user.id, int(time.time() + 45))

                    except UserAdminInvalid:
                        del_users -= 1
                        del_admins += 1

                    except FloodWait as e_f:
                        time.sleep(e_f.x)
                    del_users += 1
                    del_total += 1

            if del_admins > 0:
                del_stats = f"`👻 Found` **{del_total}** `total zombies..`\
                \n`🗑 Cleaned` **{del_users}** `zombie (deleted) accounts from this chat..`\
                \n🛡 **{del_admins}** `deleted admin accounts are skipped!!`"

            else:
                del_stats = f"`👻 Found` **{del_total}** `total zombies..`\
                \n`🗑 Cleaned` **{del_users}** `zombie (deleted) accounts from this chat..`"

            await message.edit(f"{del_stats}", del_in=0)
            await CHANNEL.log(
                f"#ZOMBIE_CLEAN\n\n"
                f"CHAT: `{get_group.title}` (`{chat_id}`)\n"
                f"TOTAL ZOMBIE COUNT: `{del_total}`\n"
                f"CLEANED ZOMBIE COUNT: `{del_users}`\n"
                f"ZOMBIE ADMIN COUNT: `{del_admins}`"
            )

        else:
            await message.edit(r"`i don't have proper permission to do that! (* ￣︿￣)`", del_in=0)

    else:

        del_users = 0
        del_stats = r"`Zero zombie accounts found in this chat... WOOHOO group is clean.. \^o^/`"
        await message.edit("`🔎 Searching for zombie accounts in this chat..`")
        async for member in userge.iter_chat_members(chat_id):

            if member.user.is_deleted:
                del_users += 1

        if del_users > 0:

            del_stats = f"`Found` **{del_users}** `zombie accounts in this chat.`"
            await message.edit(
                f"🕵️‍♂️ {del_stats} "
                "`you can clean them using .zombies -c`", del_in=0)
            await CHANNEL.log(
                f"#ZOMBIE_CHECK\n\n"
                f"CHAT: `{get_group.title}` (`{chat_id}`)\n"
                f"ZOMBIE COUNT: `{del_users}`"
                )

        else:
            await message.edit(f"{del_stats}", del_in=0)
            await CHANNEL.log(
                f"#ZOMBIE_CHECK\n\n"
                f"CHAT: `{get_group.title}` (`{chat_id}`)\n"
                r"ZOMBIE COUNT: `WOOHOO group is clean.. \^o^/`"
                )

@userge.on_cmd("pin", about={
    'header': "use this to pin & unpin messages",
    'description': "pin & unpin messages in groups with or without notify to members.",
    'flags': {
        '-s': "silent",
        '-u': "unpin"},
    'examples': [
        "{tr}pin [reply to chat message]",
        "{tr}pin -s [reply to chat message]",
        "{tr}pin -u [send to chat]"]})
async def pin_msgs(message: Message):
    """
    this function can pin & unpin message in groups
    """
    chat_id = message.chat.id
    flags = message.flags
    get_group = await userge.get_chat(chat_id)
    check_user = await userge.get_chat_member(message.chat.id, message.from_user.id)
    user_type = check_user.status
    can_pin = None

    silent_pin = '-s' in flags
    unpin_pinned = '-u' in flags

    if user_type == "member":
        can_pin = get_group.permissions.can_pin_messages

    elif user_type == "administrator":
        can_pin = check_user.can_pin_messages

    else:
        can_pin = True

    if can_pin:

        if unpin_pinned:

            try:
                await userge.unpin_chat_message(chat_id)
                await message.delete()
                await CHANNEL.log(
                    f"#UNPIN\n\n"
                    f"CHAT: `{get_group.title}` (`{chat_id}`)"
                    )

            except Exception as e_f:
                await message.edit(
                    r"`something went wrong! (⊙_⊙;)`"
                    f"\n`do .help pin for more info..`\n\n"
                    f"**ERROR:** `{e_f}`"
                    )

        elif silent_pin:

            try:
                message_id = message.reply_to_message.message_id
                await userge.pin_chat_message(chat_id, message_id, disable_notification=True)
                await message.delete()
                await CHANNEL.log(
                    f"#PIN-SILENT\n\n"
                    f"CHAT: `{get_group.title}` (`{chat_id}`)"
                    )

            except Exception as e_f:
                await message.edit(
                    r"`something went wrong! (⊙_⊙;)`"
                    f"\n`do .help pin for more info..`\n\n"
                    f"**ERROR:** `{e_f}`"
                    )

        else:

            try:
                message_id = message.reply_to_message.message_id
                await userge.pin_chat_message(chat_id, message_id)
                await message.delete()
                await CHANNEL.log(
                    f"#PIN\n\n"
                    f"CHAT: `{get_group.title}` (`{chat_id}`)"
                    )

            except Exception as e_f:
                await message.edit(
                    r"`something went wrong! (⊙_⊙;)`"
                    f"\n`do .help pin for more info..`\n\n"
                    f"**ERROR:** `{e_f}`"
                    )

    else:
        await message.edit(r"`i don't have proper permission to do that! (* ￣︿￣)`", del_in=0)

@userge.on_cmd("gpic", about={
    'header': "use this to set or delete chat photo",
    'description': "set new chat photo or delete current chat photo",
    'flags': {
        '-s': "set",
        '-d': "delete"},
    'examples': [
        "{tr}gpic -s [reply to chat image/media file]",
        "{tr}gpic -d [send to chat]"]})
async def chatpic_func(message: Message):
    """
    this function can change chat photo
    """
    chat_id = message.chat.id
    flags = message.flags
    get_group = await userge.get_chat(chat_id)
    check_user = await userge.get_chat_member(message.chat.id, message.from_user.id)
    user_type = check_user.status
    change_chatpic = None

    gpic_set = '-s' in flags
    gpic_del = '-d' in flags

    if user_type == "member":
        change_chatpic = False

    elif user_type == "administrator":
        change_chatpic = check_user.can_change_info

    else:
        change_chatpic = True

    if change_chatpic:

        if gpic_set:

            if message.reply_to_message.photo:

                try:
                    img_id = message.reply_to_message.photo.file_id
                    img_ref = message.reply_to_message.photo.file_ref
                    await userge.set_chat_photo(chat_id, img_id, img_ref)
                    await message.delete()
                    await CHANNEL.log(
                        f"#GPIC-SET\n\n"
                        f"CHAT: `{get_group.title}` (`{chat_id}`)"
                        )

                except Exception as e_f:
                    await message.edit(
                        r"`something went wrong!! (⊙ˍ⊙)`"
                        f"\n\n**ERROR:** `{e_f}`")
                    return

            elif message.reply_to_message.document.mime_type == "image/png":

                try:
                    gpic_path = await userge.download_media(message.reply_to_message)
                    await userge.set_chat_photo(message.chat.id, gpic_path)
                    await message.delete()
                    os.remove(gpic_path)
                    await CHANNEL.log(
                        f"#GPIC-SET\n\n"
                        f"CHAT: `{get_group.title}` (`{chat_id}`)"
                        )

                except Exception as e_f:
                    await message.edit(
                        r"`something went wrong!! (⊙ˍ⊙)`"
                        f"\n\n**ERROR:** `{e_f}`")
                    return

            else:
                await message.edit(
                    text="`no valid message/picture reply specified,`"
                    " `do .help gpic for more info` ⚠", del_in=0)
                return

        elif gpic_del:

            try:
                await userge.delete_chat_photo(chat_id)
                await message.delete()
                await CHANNEL.log(
                    f"#GPIC-DELETE\n\n"
                    f"CHAT: `{get_group.title}` (`{chat_id}`)"
                    )

            except Exception as e_f:
                await message.edit(
                    r"`something went wrong!! (⊙ˍ⊙)`"
                    f"\n\n**ERROR:** `{e_f}`")
                return

        else:
            await message.edit(
                text="`invalid flag type, do .help gpic for more info` ⚠", del_in=0)
            return

    else:
        await message.edit(r"`i don't have proper permission to do that! (* ￣︿￣)`", del_in=0)


@userge.on_cmd("smode", about={
    'header': "turn on/off chat slow mode",
    'description': "use this to turn off or switch between chat slow mode \n"
                   "available 6 modes, s10/s30/m1/m5/m15/h1",
    'flags': {
        '-s': "seconds",
        '-m': "minutes",
        '-h': "hour",
        '-o': "off"},
    'types': [
        '-s10 = 10 seconds', '-s30 = 30 seconds', '-m1 = 1 minutes',
        '-m5 = 5 minutes','-m15 = 15 minutes', '-h1 = 1 hour'],
    'examples': [
        "{tr}smode -s30 [send to chat] (turn on 30s slow mode) ",
        "{tr}smode -o [send to chat] (turn off slow mode)"]})
async def smode_switch(message: Message):
    """
    turn on/off chat slow mode
    """
    chat_id = message.chat.id
    can_do_smode = await is_sudoadmin(message)
    get_group = await userge.get_chat(chat_id)
    flags = message.flags

    seconds = flags.get('-s', 0)
    minutes = flags.get('-m', 0)
    hours = flags.get('-h', 0)
    smode_off = '-o' in flags

    if can_do_smode:

        if seconds:
            try:
                seconds = int(seconds)
                await userge.set_slow_mode(chat_id, seconds)
                await message.edit(
                    f"`⏳ turned on {seconds} seconds slow mode for chat!`", del_in=0)
                await CHANNEL.log(
                    f"#SLOW_MODE\n\n"
                    f"CHAT: `{get_group.title}` (`{chat_id}`)\n"
                    f"SLOW MODE TIME: `{seconds} seconds`")
            except Exception as e_f:
                await message.edit(
                    "`something went wrong!!, do .help smode for more info..` \n\n"
                    f"**ERROR:** `{e_f}`")
                return

        elif minutes:
            try:
                smode_time = int(minutes) * 60
                await userge.set_slow_mode(chat_id, smode_time)
                await message.edit(
                    f"`⏳ turned on {minutes} minutes slow mode for chat!`", del_in=0)
                await CHANNEL.log(
                    f"#SLOW_MODE\n\n"
                    f"CHAT: `{get_group.title}` (`{chat_id}`)\n"
                    f"SLOW MODE TIME: `{minutes} minutes`")
            except Exception as e_f:
                await message.edit(
                    "`something went wrong!!, do .help smode for more info..` \n\n"
                    f"**ERROR:** `{e_f}`")
                return

        elif hours:
            try:
                smode_time = int(hours) * 3600
                await userge.set_slow_mode(chat_id, smode_time)
                await message.edit("`⏳ turned on 1 hour slow mode for chat!`", del_in=0)
                await CHANNEL.log(
                    f"#SLOW_MODE\n\n"
                    f"CHAT: `{get_group.title}` (`{chat_id}`)\n"
                    f"SLOW MODE TIME: `{hours} hours`")
            except Exception as e_f:
                await message.edit(
                    "`something went wrong!!, do .help smode for more info..` \n\n"
                    f"**ERROR:** `{e_f}`")
                return

        elif smode_off:
            try:
                await userge.set_slow_mode(chat_id, 0)
                await message.edit("`⏳ turned off slow mode for chat!`", del_in=0)
                await CHANNEL.log(
                    f"#SLOW_MODE\n\n"
                    f"CHAT: `{get_group.title}` (`{chat_id}`)\n"
                    f"SLOW MODE: `Off`")
            except Exception as e_f:
                await message.edit(
                    "`something went wrong!!, do .help smode for more info..` \n\n"
                    f"**ERROR:** `{e_f}`")
            return

        else:
            await message.edit(
                "`inavlid flag type/mode.. do .help smode for more info!!`", del_in=0)

    else:
        await message.edit(r"`i don't have proper permission to do that! (* ￣︿￣)`", del_in=0)
