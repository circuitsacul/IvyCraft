from __future__ import annotations

from typing import TYPE_CHECKING, cast

import crescent
import hikari

from ivycraft.config import CONFIG
from ivycraft.database.models.user import User

if TYPE_CHECKING:
    from .bot import Bot


async def guild_only(ctx: crescent.Context) -> None | crescent.HookResult:
    if ctx.guild_id is None:
        await ctx.respond(
            "This command can only be used in a guild.", ephemeral=True
        )
        return crescent.HookResult(exit=True)

    return None


async def mc_mod(ctx: crescent.Context) -> None | crescent.HookResult:
    ret = await guild_only(ctx)
    if ret is not None:
        return ret
    assert ctx.member
    if CONFIG.required_role not in ctx.member.role_ids:
        await ctx.respond("You cannot run this command.", ephemeral=True)
        return crescent.HookResult(exit=True)

    return None


plugin = crescent.Plugin("commands")


@plugin.include
@crescent.hook(guild_only)
@crescent.command(name="whois", description="Wait who's that")
class Whois:
    discord_user = crescent.option(
        hikari.User, description="The Discord user to lookup.", default=None
    )
    minecraft_user = crescent.option(
        str, description="The Minecraft username to lookup.", default=None
    )

    async def callback(self, ctx: crescent.Context) -> None:
        bot = cast("Bot", ctx.app)

        if self.discord_user is not None:
            user = await User.exists(id=self.discord_user.id)
            if user is None or user.minecraft_uuid is None:
                await ctx.respond(
                    f"{self.discord_user} has not linked their minecraft "
                    "account.",
                    ephemeral=True,
                )
                return
            minecraft_user = await bot.mojang.get_username(user.minecraft_uuid)
            if minecraft_user is None:
                await ctx.respond(
                    f"{self.discord_user} is linked to an invalid account.",
                    ephemeral=True,
                )
                return
            await ctx.respond(
                f"{self.discord_user}'s Minecraft username is "
                f"{minecraft_user}."
            )

        elif self.minecraft_user is not None:
            minecraft_uuid = await bot.mojang.get_uuid(self.minecraft_user)
            if minecraft_uuid is None:
                await ctx.respond(
                    f"{self.minecraft_user} is not a valid Minecraft "
                    "username.",
                    ephemeral=True,
                )
                return
            user = await User.exists(minecraft_uuid=minecraft_uuid)
            if user is None:
                await ctx.respond(
                    f"{self.minecraft_user} is not linked to a Discord "
                    "account.",
                    ephemeral=True,
                )
                return
            discord_user = await bot.rest.fetch_user(user.discord_id)
            if discord_user is None:
                await ctx.respond(
                    f"{self.minecraft_user} is linked to an invalid account.",
                    ephemeral=True,
                )
                return
            await ctx.respond(
                f"{self.minecraft_user}'s Discord account is {discord_user}.",
                ephemeral=True,
            )

        else:
            await ctx.respond(
                "You must provide either a Discord user or a Minecraft "
                "username.",
                ephemeral=True,
            )


@plugin.include
@crescent.hook(mc_mod)
@crescent.command(name="run", description="Run a Minecraft command.")
class RunCommand:
    command = crescent.option(str, "The command to run.")

    async def callback(self, ctx: crescent.Context) -> None:
        bot = cast("Bot", ctx.app)
        bot.server.command(self.command)
        await ctx.respond("Executed command.")


@plugin.include
@crescent.hook(guild_only)
@crescent.command(
    name="connect", description="Link your discord to your minecraft account."
)
class LinkAccounts:
    name = crescent.option(
        str, "Your Minecraft username.", name="minecraft-name"
    )

    async def callback(self, ctx: crescent.Context) -> None:
        bot = cast("Bot", ctx.app)
        assert ctx.member is not None

        user = await User.exists(discord_id=ctx.member.id)
        if user is None:
            user = await User(discord_id=ctx.member.id).create()

        if user.minecraft_uuid:
            await ctx.respond(
                "You are already linked to a minecraft account.",
                ephemeral=True,
            )
            return

        uuid = await bot.mojang.get_uuid(self.name)
        if uuid is None:
            await ctx.respond("Invalid username.", ephemeral=True)

        user.minecraft_uuid = uuid
        await user.save()
        await bot.server.update_whitelist()
        await ctx.respond(
            "You've linked your Minecraft account.", ephemeral=True
        )
