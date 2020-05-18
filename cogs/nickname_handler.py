import json

import discord
from discord.ext import commands

from cogs import utils


ZALGO_CHARACTERS = [
    '\u030d', '\u030e', '\u0304', '\u0305',
    '\u033f', '\u0311', '\u0306', '\u0310',
    '\u0352', '\u0357', '\u0351', '\u0307',
    '\u0308', '\u030a', '\u0342', '\u0343',
    '\u0344', '\u034a', '\u034b', '\u034c',
    '\u0303', '\u0302', '\u030c', '\u0350',
    '\u0300', '\u0301', '\u030b', '\u030f',
    '\u0312', '\u0313', '\u0314', '\u033d',
    '\u0309', '\u0363', '\u0364', '\u0365',
    '\u0366', '\u0367', '\u0368', '\u0369',
    '\u036a', '\u036b', '\u036c', '\u036d',
    '\u036e', '\u036f', '\u033e', '\u035b',
    '\u0346', '\u031a',
    '\u0316', '\u0317', '\u0318','\u0319',
    '\u031c', '\u031d', '\u031e','\u031f',
    '\u0320', '\u0324', '\u0325','\u0326',
    '\u0329', '\u032a', '\u032b','\u032c',
    '\u032d', '\u032e', '\u032f','\u0330',
    '\u0331', '\u0332', '\u0333','\u0339',
    '\u033a', '\u033b', '\u033c','\u0345',
    '\u0347', '\u0348', '\u0349','\u034d',
    '\u034e', '\u0353', '\u0354','\u0355',
    '\u0356', '\u0359', '\u035a','\u0323',
    '\u0315', '\u031b', '\u0340','\u0341',
    '\u0358', '\u0321', '\u0322','\u0327',
    '\u0328', '\u0334', '\u0335','\u0336',
    '\u034f', '\u035c', '\u035d','\u035e',
    '\u035f', '\u0360', '\u0362','\u0338',
    '\u0337', '\u0361', '\u0489',
    '\u0670',
    '\u25ce', '\u20d2',
    '\u06e3', '\u06dc',
    '\u02de',
]


class NicknameHandler(utils.Cog):

    @utils.Cog.listener()
    async def on_member_join(self, member:discord.Member):
        """Pings a member nickname update on member join"""

        if self.bot.guild_settings[member.guild.id]['automatic_nickname_update']:
            self.logger.info(f"Pinging nickname update for member join (G{member.guild.id}/U{member.id})")
            await self.fix_user_nickname(member)

    @utils.Cog.listener()
    async def on_member_update(self, before:discord.Member, member:discord.Member):
        """Pings a member nickname update on nickname update"""

        if self.bot.guild_settings[member.guild.id]['automatic_nickname_update']:
            if before.display_name != member.display_name:
                if member.guild_permissions.manage_nicknames:
                    self.logger.info(f"Not pinging nickname update for manage_nicknames member (G{member.guild.id}/U{member.id})")
                    return
                try:
                    async for entry in member.guild.audit_logs(limit=1, action=discord.AuditLogAction.member_update):
                        if entry.target.id == member.id:
                            if entry.user.id != member.id:
                                self.logger.info(f"Not pinging nickname update for a name changed by moderator (G{member.guild.id}/U{member.id})")
                                return
                            break
                except discord.Forbidden:
                    pass
                self.logger.info(f"Pinging nickname update for member update (G{member.guild.id}/U{member.id})")
                await self.fix_user_nickname(member)

    async def fix_user_nickname(self, user:discord.Member) -> str:
        """Fix the nickname of a user"""

        with open("config/letter_replacements.json") as a:
            replacements = json.load(a)
        translator = str.maketrans(replacements)
        current_name = user.nick or user.name
        new_name_with_zalgo = current_name.translate(translator)
        new_name = ''.join([i for i in new_name_with_zalgo if i not in ZALGO_CHARACTERS])
        if current_name == new_name:
            self.logger.info(f"Not updating the nickname '{new_name}' (G{user.guild.id}/U{user.id})")
            return new_name
        self.logger.info(f"Updating nickname '{current_name}' to '{new_name}' (G{user.guild.id}/U{user.id})")
        await user.edit(nick=new_name)
        return new_name

    @commands.command(cls=utils.Command, aliases=['fun'])
    @commands.has_permissions(manage_nicknames=True)
    @commands.bot_has_permissions(manage_nicknames=True)
    async def fixunzalgoname(self, ctx:utils.Context, user:discord.Member):
        """Fixes a user's nickname to remove dumbass characters"""

        current_name = user.nick or user.name
        new_name = await self.fix_user_nickname(user)
        return await ctx.send(f"Changed their name from `{current_name}` to `{new_name}`.")

    @commands.command(ignore_extra=False, cls=utils.Command)
    @commands.has_permissions(manage_nicknames=True)
    @commands.is_owner()
    @commands.bot_has_permissions(manage_nicknames=True)
    async def addfixableletters(self, ctx:utils.Context, phrase1:str, phrase2:str):
        """Adds fixable letters to the replacement list"""

        try:
            with open("config/letter_replacements.json") as a:
                replacements = json.load(a)
        except Exception as e:
            return await ctx.send(f"Could not open letter replacement file - `{e}`.")
        for i, o in zip(phrase1, phrase2):
            replacements[i] = o
        try:
            with open("config/letter_replacements.json", "w") as a:
                json.dump(replacements, a)
        except Exception as e:
            return await ctx.send(f"Could not open letter replacement file to write to it - `{e}`.")
        return await ctx.send("Written to file successfully.")

    @commands.command(cls=utils.Command)
    @commands.has_permissions(manage_nicknames=True)
    @commands.bot_has_permissions(manage_nicknames=True)
    async def setpermanentnickname(self, ctx:utils.Context, user:discord.Member, *, name:str=None):
        """Sets the permanent nickname for a user"""

        # Update db
        async with self.bot.database() as db:
            if name:
                await db(
                    """INSERT INTO permanent_nicknames (guild_id, user_id, nickname)
                    VALUES ($1, $2, $3)
                    ON CONFLICT (guild_id, user_id) DO UPDATE SET nickname=$3""",
                    ctx.guild.id, user.id, name
                )
            else:
                await db("DELETE FROM permanent_nicknames WHERE guild_id=$1 AND user_id=$2", ctx.guild.id, user.id)

        # Edit and respond
        await user.edit(nick=name)
        if name:
            await ctx.send(f"The nickname of {user.mention} has been set to `{name}`.")
        else:
            await ctx.send(f"{user.mention} no longer has a permanent nickname.")


def setup(bot:utils.Bot):
    x = NicknameHandler(bot)
    bot.add_cog(x)
