from __future__ import annotations

import aiohttp


class MojangClient:
    def __init__(self) -> None:
        self._session: aiohttp.ClientSession | None = None

    async def session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close(self) -> None:
        if self._session is not None and not self._session.closed:
            await self._session.close()
            self._session = None

    async def get_uuid(self, name: str) -> str | None:
        ses = await self.session()
        async with ses.get(
            f"https://api.mojang.com/users/profiles/minecraft/{name}"
        ) as resp:
            if resp.status != 200:
                return None
            data = await resp.json()

        return data["id"]  # type: ignore

    async def get_username(self, uuid: str) -> str | None:
        ses = await self.session()
        async with ses.get(
            "https://sessionserver.mojang.com/session/minecraft/profile/"
            f"{uuid}"
        ) as resp:
            if resp.status != 200:
                return None
            data = await resp.json()

        return data[0]["name"]  # type: ignore
