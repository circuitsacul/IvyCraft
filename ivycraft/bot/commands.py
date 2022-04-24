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
@crescent.hook(mc_mod)
@crescent.command(name="run", description="Run a Minecraft command.")
class RunCommand:
    command = crescent.option(str, "The command to run.")

    async def callback(self, ctx: crescent.Context) -> None:
        bot = cast("Bot", ctx.app)
        bot.server.command(self.command)
        await ctx.respond("Executed command.")


@plugin.include
@crescent.hook(mc_mod)
@crescent.command(name="whitelist", description="Whitelist a player.")
class WhitelistUser:
    user = crescent.option(hikari.User, "The user to whitelist.")

    async def callback(self, ctx: crescent.Context) -> None:
        bot = cast("Bot", ctx.app)

        user = await User.exists(discord_id=self.user.id)
        if not user:
            user = await User(
                discord_id=self.user.id, whitelisted=True
            ).create()

        else:
            user.whitelisted = True
            await user.save()

        await ctx.respond(f"{self.user} has been whitelisted.")
        await bot.server.update_whitelist()


@plugin.include
@crescent.hook(mc_mod)
@crescent.command(name="unwhitelist", description="Unwhitelist a player.")
class UnwhitelistUser:
    user = crescent.option(hikari.User, "The user to unwhitelist.")

    async def callback(self, ctx: crescent.Context) -> None:
        bot = cast("Bot", ctx.app)

        user = await User.exists(discord_id=self.user.id)
        if (not user) or user.whitelisted is False:
            await ctx.respond(f"{self.user} is not whitelisted.")
            return

        user.whitelisted = False
        await user.save()

        await ctx.respond(f"{self.user} has been unwhitelisted.")
        await bot.server.update_whitelist()


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
        if user is None or not user.whitelisted:
            await ctx.respond("You are not whitelisted.", ephemeral=True)
            return

        if user.minecraft_uuid:
            await ctx.respond(
                "You are already linked to a minecraft account.",
                ephemeral=True,
            )
            return

        await bot.server.whitelist_user(user, self.name)
        await ctx.respond(
            "You've linked your Minecraft account.", ephemeral=True
        )
