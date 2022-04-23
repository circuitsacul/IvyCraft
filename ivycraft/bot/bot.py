from typing import Any

import crescent

from ivycraft.config import CONFIG
from ivycraft.database.database import IvyDB
from ivycraft.server.server import MCServer


class Bot(crescent.Bot):
    def __init__(self) -> None:
        super().__init__(
            CONFIG.discord_token, default_guild=CONFIG.ivycraft_guild
        )

        self.db = IvyDB()
        self.server = MCServer(self)

        self.plugins.load("ivycraft.bot.commands")

    async def start(self, *args: Any, **kwargs: Any) -> None:
        await self.db.connect()
        await self.server.start()
        await super().start(*args, **kwargs)


def run() -> None:
    bot = Bot()
    bot.run()
