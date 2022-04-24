from typing import Any

import crescent
import hikari

from ivycraft.config import CONFIG
from ivycraft.database.database import IvyDB
from ivycraft.server.server import MCServer

from .cache import Cache


class Bot(crescent.Bot):
    def __init__(self) -> None:
        self._real_cache = Cache(self)

        super().__init__(
            CONFIG.discord_token,
            default_guild=CONFIG.ivycraft_guild,
            intents=hikari.Intents.GUILD_MEMBERS,
        )

        self.db = IvyDB()
        self.server = MCServer(self)

        self.plugins.load("ivycraft.bot.commands")

    @property
    def cache(self) -> Cache:
        return self._real_cache

    @property  # type: ignore
    def _cache(self) -> Cache:  # type: ignore
        return self._real_cache

    @_cache.setter
    def _cache(self, ot: Any) -> None:
        pass

    async def start(self, *args: Any, **kwargs: Any) -> None:
        await self.db.connect()
        await super().start(*args, **kwargs)
        await self.server.start()


def run() -> None:
    bot = Bot()
    bot.run()
