from __future__ import annotations

from typing import TYPE_CHECKING, cast

import crescent
import hikari

from ivycraft.config import CONFIG

if TYPE_CHECKING:
    from ivycraft.bot.bot import Bot


plugin = crescent.Plugin("events")


@plugin.include
@crescent.event
async def on_message(event: hikari.GuildMessageCreateEvent) -> None:
    bot = cast("Bot", event.app)

    if event.channel_id != CONFIG.chat_channel:
        return

    if event.author.is_bot:
        return

    bot.server.command(f"say <{event.author} (discord)> {event.content}")
