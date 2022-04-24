from __future__ import annotations

from typing import TYPE_CHECKING, Any

from hikari.impl.cache import CacheImpl
from hikari.impl.config import CacheSettings

from ivycraft.config import CONFIG

if TYPE_CHECKING:
    from ivycraft.bot.bot import Bot


class Cache(CacheImpl):
    def __init__(self, bot: Bot) -> None:
        super().__init__(bot, CacheSettings())

        self._ivycraft_members: set[int] | None = None

    async def get_ivycraft_members(self) -> set[int]:
        if self._ivycraft_members is not None:
            return self._ivycraft_members

        self._ivycraft_members = set()
        async for member in self._app.rest.fetch_members(
            CONFIG.ivycraft_guild
        ):
            self._ivycraft_members.add(member.id)

        return self._ivycraft_members

    def clear_members(self) -> Any:
        self._ivycraft_members = None
        return super().clear_members()

    def clear_members_for_guild(self, guild: Any) -> Any:
        if int(guild) == CONFIG.ivycraft_guild:
            self._ivycraft_members = None
        return super().clear_members_for_guild(guild)

    def delete_member(self, guild: Any, user: Any) -> Any:
        if int(guild) == CONFIG.ivycraft_guild and self._ivycraft_members:
            self._ivycraft_members.remove(int(user))
        return super().delete_member(guild, user)
