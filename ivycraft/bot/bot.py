from typing import Any

import crescent

from ivycraft.config import CONFIG
from ivycraft.database.database import IvyDB


class Bot(crescent.Bot):
    def __init__(self) -> None:
        super().__init__(CONFIG.discord_token)

        self.db = IvyDB()

    async def start(self, *args: Any, **kwargs: Any) -> None:
        await self.db.connect()
        await super().start(*args, **kwargs)


def run() -> None:
    bot = Bot()
    bot.run()
