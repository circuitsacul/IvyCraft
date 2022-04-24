from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

from ivycraft.database.models.user import User

if TYPE_CHECKING:
    from ivycraft.bot.bot import Bot


class Whitelist:
    def __init__(self, path: Path, bot: Bot) -> None:
        self.path = path
        self.bot = bot

    def whitelist_by_name(self) -> dict[str, str]:
        with self.path.open("r") as f:
            lines = f.read()

        data = json.loads(lines)
        return {item["name"]: item["uuid"] for item in data if item["name"]}

    async def save(self) -> None:
        members = await self.bot.cache.get_ivycraft_members()
        whitelisted = await User.fetch_query().fetchmany()
        wl_json = json.dumps(
            [
                {"uuid": wl.minecraft_uuid, "name": str(wl.discord_id)}
                for wl in whitelisted
                if wl.minecraft_uuid is not None and wl.discord_id in members
            ]
        )
        with self.path.open("w") as f:
            f.write(wl_json)
