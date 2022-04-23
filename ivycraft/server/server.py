from __future__ import annotations

import asyncio
import pathlib
import subprocess

from ivycraft.config import CONFIG
from ivycraft.database.models.user import User

from .whitelist import Whitelist


class MCServer:
    def __init__(self) -> None:
        self.proc: subprocess.Popen[bytes] | None = None
        self.path = pathlib.Path(CONFIG.server_path)
        self.whitelist = Whitelist(self.path / "whitelist.json")

    async def start(self) -> None:
        self.proc = subprocess.Popen(
            [
                "java",
                f"-Xmx{CONFIG.server_memory}",
                f"-Xms{CONFIG.server_memory}",
                "-jar",
                self.path / "server.jar",
                "nogui",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
        )
        await self.update_whitelist()

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
