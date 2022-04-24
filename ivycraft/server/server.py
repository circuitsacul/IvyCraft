from __future__ import annotations

import asyncio
import pathlib
import subprocess
import threading
from typing import TYPE_CHECKING, Iterator

import hikari

from ivycraft.config import CONFIG
from ivycraft.database.models.user import User

from .whitelist import Whitelist

if TYPE_CHECKING:
    from ivycraft.bot.bot import Bot


def paginate(text: str) -> Iterator[str]:
    current = 0
    jump = 500
    while True:
        page = text[current : current + jump]
        current += jump
        yield page
        if current >= len(text):
            return


class MCServer:
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self._wh: hikari.ExecutableWebhook | None = None

        self.proc: subprocess.Popen[bytes] | None = None
        self.path = pathlib.Path(CONFIG.server_path)
        self.whitelist = Whitelist(self.path / "whitelist.json", bot)

        self.to_log: list[str] = []

        self.reader = threading.Thread(target=self._reader_thread)
        self.logger: asyncio.Task[None] | None = None

    async def start(self) -> None:
        self.proc = subprocess.Popen(
            f"cd {self.path.resolve()} && java -Xmx{CONFIG.server_memory} "
            f"-Xms{CONFIG.server_memory} -jar server.jar nogui",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
            shell=True,
        )
        self.reader.start()
        await self.update_whitelist()
        self.logger = asyncio.create_task(self.logger_loop())

    async def logger_loop(self) -> None:
        while True:
            await asyncio.sleep(10)
            if not self.to_log:
                continue

            to_send = "\n".join(lin.strip() for lin in self.to_log)
            for page in paginate(to_send):
                await self.bot.rest.create_message(CONFIG.log_channel, page)
            self.to_log.clear()

    def command(self, command: str) -> None:
        assert self.proc is not None
        assert self.proc.stdin is not None
        self.proc.stdin.write((command + "\n").encode("utf8"))
        self.proc.stdin.flush()

    async def update_whitelist(self) -> None:
        await self.whitelist.save()
        self.command("whitelist reload")

    async def whitelist_user(self, user: User, mc_name: str) -> None:
        self.command(f"whitelist add {mc_name}")
        await asyncio.sleep(0.5)
        user.minecraft_uuid = self.whitelist.whitelist_by_name()[mc_name]
        await user.save()
        await self.update_whitelist()

    def _reader_thread(self) -> None:
        assert self.proc is not None
        assert self.proc.stdout is not None
        for _line in iter(self.proc.stdout.readline, b""):
            line: str = _line.decode().strip()
            if "Preparing spawn area" in line:
                continue
            if "User Authenticator" in line:
                continue
            self.to_log.append(line)
            print(line)
