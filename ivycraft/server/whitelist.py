from __future__ import annotations

import json
from pathlib import Path

from ivycraft.database.models.user import User


class Whitelist:
    def __init__(self, path: Path) -> None:
        self.path = path

    def whitelist_by_name(self) -> dict[str, str]:
        with self.path.open("r") as f:
            lines = f.read()

        data = json.loads(lines)
        return {item["name"]: item["uuid"] for item in data if item["name"]}

    async def save(self) -> None:
        whitelisted = (
            await User.fetch_query().where(whitelisted=True).fetchmany()
        )
        wl_json = json.dumps(
            [
                {"uuid": wl.minecraft_uuid}
                for wl in whitelisted
                if wl.minecraft_uuid is not None
            ]
        )
        with (self.path).open("w") as f:
            f.write(wl_json)
