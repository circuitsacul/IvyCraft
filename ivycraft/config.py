import inspect
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Optional, cast


@dataclass
class Config:
    discord_token: str = "**DISCORD BOT TOKEN**"
    chat_channel: int = -1
    ivycraft_guild: int = -1
    required_role: int = -1

    server_path: str = "~/server"
    server_memory: str = "3G"

    db_name: str = "**DATABASE NAME**"
    db_user: Optional[str] = None
    db_password: Optional[str] = None
    db_host: str = "localhost"

    def save(self) -> None:
        pth = Path("config.json")

        dct = asdict(self)
        tosave: dict[str, Any] = {}
        defaults = self.__class__()
        for k, v in dct.items():
            if getattr(defaults, k) == v:
                continue

            tosave[k] = v

        with pth.open("w+") as f:
            f.write(json.dumps(tosave, indent=4))

    @classmethod
    def load(cls) -> "Config":
        pth = Path("config.json")

        if not pth.exists():
            c = Config()
        else:
            keys = set(inspect.signature(Config).parameters)
            with pth.open("r") as f:
                c = Config(
                    **{
                        k: v
                        for k, v in cast(
                            "dict[Any, Any]", json.loads(f.read())
                        ).items()
                        if k in keys
                    }
                )

        c.save()
        return c


CONFIG = Config.load()
