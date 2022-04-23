import crescent

from ivycraft.config import CONFIG


class Bot(crescent.Bot):
    def __init__(self) -> None:
        super().__init__(CONFIG.discord_token)


def run() -> None:
    bot = Bot()
    bot.run()
