from typing import Any

from apgorm import Database

from ivycraft.config import CONFIG

from .models.user import User


class IvyDB(Database):
    users = User

    def __init__(self) -> None:
        super().__init__("ivycraft/database/migrations")

    async def connect(self, **_: Any) -> None:
        if self.must_create_migrations():
            raise RuntimeError("There are uncreated migrations.")

        await super().connect(
            host=CONFIG.db_host,
            database=CONFIG.db_name,
            user=CONFIG.db_user,
            password=CONFIG.db_password,
        )

        if await self.must_apply_migrations():
            print("Applying migrations...")
            await self.apply_migrations()
            print("Migrations applied.")
