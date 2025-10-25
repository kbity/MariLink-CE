# --- imports --- #

import discord, traceback, random, json, re, aiohttp, io, os, sys, asyncio, time
from discord import app_commands, StickerFormatType
from discord.ext import commands
from typing import Literal, Optional
from dotenv import load_dotenv

# --- setup --- #

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='ml!', intents=intents)
tree = bot.tree
usernameCache = {}
mari_linking = {}

mlav = None
with open("res/img.png", "rb") as image:
  f = image.read()
  mlav = bytearray(f)

# --- quick config --- #

evaluser = 798072830595301406 # Bot owner Id.

load_dotenv()
TOKEN = os.getenv("TOKEN") # Load Dotenv

VerString = "1.0.0" # Version String

emojis = {}
emojis["normal"] = "<:normal:1415470137464717373>"
emojis["reply"] = "<:reply:1422725515608854579>"
emojis["command"] = "<:command:1422725512589217883>"
emojis["NeoMari_Melt_Sob"] = "<:NeoMari_Melt_Sob:1422744823768809534>"
emojis["ml_mute"] = "<:ml_mute:1431480922385154179>"
emojis["ml_ban"] = "<:ml_ban:1431480918693908531>"
emojis["ml_check"] = "<:ml_check:1431480916181778452>"
emojis["ml_error"] = "<:ml_error:1431480920400990349>"

# these are random strings used in the bot
errorMsgs = ["500 Internal Server Error", "501 Not Implemented", "502 Bad Gateway", "503 Service Unavailable", "504 Gateway Timeout", "505 HTTP Version Not Supported", "506 Variant Also Negotiates", "507 Insufficient Storage", "508 Loop Detected", "509 Bandwidth Limit Exceeded", "510 Not Extended", "511 Network Authentication Required", "520 Web Server Returned an Unknown Error", "521 Web Server Is Down", "522 Connection Timed Out", "523 Origin Is Unreachable", "524 A Timeout Occurred", "525 SSL Handshake Failed", "526 Invalid SSL Certificate", "527 Railgun Error", "529 Site is overloaded", "530 Origin DNS Error", "540 Temporarily Disabled", "555 User Defined Resource Error", "561 Unauthorized", "598 Network read timeout error", "599 Network Connect Timeout Error", "618 Too Many Cubes\n-# ✨ You got the Rare Error"]

whatce = ["Community Edition", "Crystal Ediquite", "Cpython rEwrite", "Crazy Edition", "Colour Edition", "Cell machinE", "AX Zirconium" "Ceiling Effects", "Chilled Estrogen", "CD Easy", "Citem Easylum is way more interesting", "Cool Explosions", "Countless Errors", "CEASCE", "Creating Elephants", "Cyeah ok libEral", "Ceroba Edition", "Classic Edition", "(fan) Cervice Edition", "99 bottles of iCE cold beer", "Creisi Edition", "Cesium Edition", "Community Edition??", "Cinnamon Edition", "Chocolate and Eggs", "CariEink", "CErium", "ChEchen language", "Common Era", "Customer Edge", "Calculator Edition", "Celery Empire"]

# --- commands --- #

@tree.command(name="createchannel", description="creates marilink channel")
async def createchannel(ctx: commands.Context, name: str, password: str = None, public: bool = False, allow_bots: bool = True, mode: Literal["Normal", "Strange", "TwoPoint", "OneWay"] = "Normal"):
    discordChannelIds = None
    try:
        db = load_db()
        if password is None:
            await ctx.response.defer()
        else:
            await ctx.response.defer(ephemeral=True)
        res = f"{emojis['ml_check']} ok i totally created `{name}` as a `{mode}` channel"
        if public and password is not None:
            await ctx.followup.send(f"{emojis['ml_error']} vro pick one like buddy lmao wtf?? you cant have a password on a public channel what the fuck is wrong with you :rofl::rofl:")
            return
        if public and mode == "TwoPoint":
            await ctx.followup.send(f"{emojis['ml_error']} pretty sure you dont want to do this. either way, its not allowed.")
            return
        if name == "MariLink_Configuration":
            await ctx.followup.send(f"{emojis['ml_error']} this name is ass. session terminated.")
            return
        if len(name) > 26:
            await ctx.followup.send(f"{emojis['ml_error']} channel names can only be as long as 26 characters. just think about it, 26 is plenty, im sure.")
            return
        if password is None:
            res = res + " with no password"
        if public:
            res = res + " that is public"
        if not allow_bots:
            res = res + f" that excludes bots (like me {emojis['NeoMari_Melt_Sob']})"
        if name in db:
            if db[name]["userId"] == str(ctx.user.id):
                if "discordChannelIds" in db[name]:
                    discordChannelIds = db[name]["discordChannelIds"]

                if (not "Type" in db[name]) or (not db[name]["Type"] == "TwoPoint"):
                    if mode == "TwoPoint":
                        await ctx.followup.send(f"{emojis['ml_error']} cannot convert normal channel to TwoPoint channel")
                        return

                res = res + "\n-# (Channel Edited)"
            else:
                await ctx.followup.send(f"{emojis['ml_error']} channel already exists!")
                return
        if password is not None and mode == "TwoPoint":
            res = res + "\n-# btw setting passwords is pointless on TwoPoint channels"
        db[name] = {}
        db[name]["userId"] = str(ctx.user.id)
        if password is not None:
            db[name]["password"] = password
        if public:
            db[name]["isPublic"] = public
        if not allow_bots:
            db[name]["allow_bots"] = False
        if not mode == "Normal":
            db[name]["Type"] = mode
        if discordChannelIds:
            db[name]["discordChannelIds"] = discordChannelIds

        await ctx.followup.send(res)
        save_db(db)
    except Exception as e:
        await ctx.channel.send(f"Error {random.choice(errorMsgs)}\n-# {e}")

@tree.command(name="removechannel", description="uncreates marilink channel")
async def removechannel(ctx: commands.Context, name: str):
    try:
        db = load_db()
        await ctx.response.defer()
        if name in db:
            if not db[name]["userId"] == str(ctx.user.id):
                await ctx.followup.send(f"{emojis['ml_error']} not yours {emojis['normal']}")
                return
        else:
            await ctx.followup.send(f"{emojis['ml_error']} channel does not exists")
            return

        res = f"{emojis['ml_check']} channel `{name}` no longer exists, assuming it existed in the first place"

        async def confirm_button_thingy(ctx2: discord.Interaction):
            if not db[name]["userId"] == str(ctx2.user.id):
                await ctx2.response.send_message(content = f"sybau the fuck up your fucking mouth", ephemeral=True)
                return
            await ctx2.response.edit_message(
                        content=res,
                        view=None,
                    )
            db.pop(name, None)
            save_db(db)

        confirm = discord.ui.Button(label=f"confirm", style=discord.ButtonStyle.secondary)
        confirm.callback = confirm_button_thingy
        view = discord.ui.View()
        view.add_item(confirm)

        await ctx.followup.send(content = f"ok buddy please confirm you want to delete `{name}` because you cant undo it", view=view)

    except Exception as e:
        await ctx.channel.send(f"Error {random.choice(errorMsgs)}\n-# {e}")

@tree.command(name="link", description="connect current channel to marilink channel")
async def unlink(ctx: commands.Context, name: str, password: str = None):
    try:
        if password is None:
            await ctx.response.defer()
        else:
            await ctx.response.defer(ephemeral=True)

        db = load_db()
        allowed_to_do = False
        if ctx.user.id == evaluser:
            allowed_to_do = True
        else:
            perms = ctx.channel.permissions_for(ctx.user)
            if perms.manage_channels:
                allowed_to_do = True

        if not allowed_to_do:
            await ctx.followup.send(f"{emojis['ml_error']} you're not the permission-doer")
            return

        if not name in db:
            await ctx.followup.send(f"{emojis['ml_error']} that channel doesnt exist you absolute buffoon")
            return

        #plaintext-grade security
        if "password" in db[name]:
            if not db[name]["password"] == password and not db[name]["userId"] == str(ctx.user.id):
                await ctx.followup.send(f"{emojis['ml_error']} wrong password!")
                return

        if "Type" in db[name] and db[name]["Type"] == "TwoPoint":
            if not db[name]["userId"] == str(ctx.user.id):
                await ctx.followup.send(f"{emojis['ml_error']} not your channel")
                return

        res = f"{emojis['ml_check']} `{name}` linked to <#{ctx.channel.id}>"

        for entry in db:
            if "discordChannelIds" in db[entry]:
                if str(ctx.channel.id) in db[entry]["discordChannelIds"]:
                    await ctx.followup.send(f"<#{ctx.channel.id}> is already linked to `{entry}`!")
                    return

        if not "discordChannelIds" in db[name]:
            db[name]["discordChannelIds"] = [str(ctx.channel.id)]
        else:
            if str(ctx.channel.id) in db[name]["discordChannelIds"]:
                await ctx.followup.send(f"<#{ctx.channel.id}> is already linked to `{name}`")
                return
        db[name]["discordChannelIds"].append(str(ctx.channel.id))

        if "Type" in db[name] and db[name]["Type"] == "TwoPoint":
            if len(db[name]["discordChannelIds"]) > 2:
                await ctx.followup.send(f"your cable isnt a hydra and can only connect to 2 places")
                return

        await ctx.followup.send(res)
        save_db(db)

    except Exception as e:
        await ctx.channel.send(f"Error {random.choice(errorMsgs)}\n-# {e}")

@tree.command(name="unlink", description="disconnect current channel to marilink channel")
async def unlink(ctx: commands.Context):
    try:
        await ctx.response.defer()

        db = load_db()
        allowed_to_do = False

        if ctx.user.id == evaluser:
            allowed_to_do = True
        else:
            perms = ctx.channel.permissions_for(ctx.user)
            if perms.manage_channels:
                allowed_to_do = True

        if not allowed_to_do:
            await ctx.followup.send(f"{emojis['ml_error']} you're not the permission-doer")
            return

        mlchannel = None

        for entry in db:
            if "discordChannelIds" in db[entry]:
                if str(ctx.channel.id) in db[entry]["discordChannelIds"]:
                    mlchannel = entry
                    break

        if mlchannel is None:
            await ctx.followup.send(f"{emojis['ml_error']} <#{ctx.channel.id}> didn't seem to link anywhere")
            return

        db[mlchannel]["discordChannelIds"].remove(str(ctx.channel.id))

        res = f"{emojis['ml_check']} `{mlchannel}` unlinked from <#{ctx.channel.id}>"
        await ctx.followup.send(res)
        save_db(db)

    except Exception as e:
        await ctx.channel.send(f"Error {random.choice(errorMsgs)}\n-# {e}")

@tree.command(name="help", description="dear fucking god i dont understand marilink at all")
async def help(ctx: commands.Context):
    try:
        await ctx.response.defer()
        embed = discord.Embed(
            title=f"MariLink CE Command Help",
            color=discord.Color.from_str("0xffb1ff")
        )
        embed.add_field(name="/link", value='The most important MariLink command. "name" is the channel name, either one from the channel browser, "general" (which is probably what you want), or a name of a channel you or someone else made for private use. "channel" is where you put the channel in your discord server to link to. "password" is an optional field used if a channel has a password set up to prevent unauthorized links for private channels. requires manage channel or admin.', inline=False)
        embed.add_field(name="/unlink", value="/link but backwards. put in the name of the MariLink channel, and the channel in your server to remove the link.", inline=False)
        embed.add_field(name="/createchannel", value='creates a channel for MariLink. "name" is the name the channel will use, "password", as mentioned in /link, is for preventing unauthorized links. "publicallylisted", if set to yes, will allow your channel to be seen in the channel browser. not recommended if you set a password.', inline=False)
        embed.add_field(name="/removechannel",
            value='removes a channel from MariLink. "name" is the name the channel will delete. you must be the channel\'s owner to delete a channel. confirmation is required.',
            inline=False)
        embed.add_field(name="/delete", value="used by operators, mods, admins, or owners. attempts to delete a message across all the channels. will fail if marilink was restarted after it was sent.", inline=False)
        embed.add_field(name="/mute", value="used by people with owner, admin, or mod permissions and prevents someone from speaking for a period of time", inline=False)
        embed.add_field(name="/ban", value="used by people with admin or owner permissions to block a person from speaking in a channel or globally ever again.", inline=False)
        embed.add_field(name="/promote", value="gives a user perms in either a channel you own or administrate. also can be used by global admins to give people global perms.", inline=False)
        embed.add_field(name="/browser", value="shows you public marilink channels. also has a search option.", inline=False)
        embed.add_field(name="/about", value="displays info about MariLink CE", inline=False)
        if VerString == "Dev":
            embed.set_footer(text=f"MariLink CE Development Version !!𝘕𝘰𝘵 𝘍𝘰𝘳 𝘗𝘳𝘰𝘥𝘶𝘤𝘵𝘪𝘰𝘯 𝘜𝘴𝘦!!")
        else:
            embed.set_footer(text=f"MariLink CE v{VerString}")

        await ctx.followup.send(embed=embed)
    except Exception as e:
        await ctx.channel.send(f"Error {random.choice(errorMsgs)}\n-# {e}")

@tree.command(name="about", description="what is marilink and why is it ce now")
async def about(ctx: commands.Context):
    try:
        await ctx.response.defer()
        embed = discord.Embed(
            title=f"MariLink: {random.choice(whatce)}",
            description="MariLink is a bot for cross-server communication.\nMariLink CE is a rewrite and upgrade to the original MariLink discord bot.\nMariLink was created mostly out of AI-Generated Vibecode, and it has became impossible to maintain, so I am instead rewriting the bot in Python using Discord.py",
            color=discord.Color.from_str("0xffb1ff")
        )
        if VerString == "Dev":
            embed.set_footer(text=f"MariLink CE Development Version !!𝘕𝘰𝘵 𝘍𝘰𝘳 𝘗𝘳𝘰𝘥𝘶𝘤𝘵𝘪𝘰𝘯 𝘜𝘴𝘦!!")
        else:
            embed.set_footer(text=f"MariLink CE v{VerString}")

        await ctx.followup.send(embed=embed)
    except Exception as e:
        await ctx.channel.send(f"Error {random.choice(errorMsgs)}\n-# {e}")

@tree.command(name="listchannels", description="get a list of all the terrible channels you created")
async def listchannels(ctx: commands.Context):
    try:
        await ctx.response.defer()
        db = load_db()
        count = 0

        embed = discord.Embed(
            title="Your Channels",
            color=discord.Color.from_str("0xffb1ff")
        )

        for channel in db:
            if "userId" in db[channel]:
                if db[channel]["userId"] == str(ctx.user.id):
                    count += 1
                    data = ""
                    if "password" in db[channel]:
                        data += f"Password is set!\n"
                    if "allow_bots" in db[channel]:
                        if db[channel]["allow_bots"]:
                            data += f"Bots allowed?: True\n"
                        else:
                            data += f"Bots allowed?: False\n"
                    else:
                        data += f"Bots allowed?: True\n"
                    if "Type" in db[channel]:
                        data += f"Type: {db[channel]['Type']}\n"
                    else:
                        data += "Type: Normal\n"
                    if "discordChannelIds" in db[channel]:
                        connectionslen = len(db[channel]['discordChannelIds'])
                        if connectionslen == 0:
                            data += "Connections: None\n"
                        else:
                            data += f"Connections: {connectionslen}\n"
                    else:
                        data += "Connections: None\n"
                    if "isPublic" in db[channel]:
                        data += f"-# *Channel is Public in /browser*\n"

                    embed.add_field(name=channel, value=data, inline=False)

        embed.set_footer(text=f"Total Channels: {count}")
        if count > 25:
            await ctx.followup.send(f"{emojis['ml_error']} you have too many channels")
        else:
            await ctx.followup.send(embed=embed)
    except Exception as e:
        await ctx.channel.send(f"Error {random.choice(errorMsgs)}\n-# {e}")

@tree.command(name="browser", description="browse MariLink channels")
@discord.app_commands.describe(query="search term")
@discord.app_commands.describe(page="page number")
async def listchannels(ctx: commands.Context, query: str = "None", page: int = 1):
    try:
        await ctx.response.defer()
        db = load_db()

        # Collect all public channels
        data = {}
        for channel, info in db.items():
            if info.get("isPublic"):
                details = []
                details.append(f"Type: {info.get('Type', 'Normal')}")
                connections = info.get("discordChannelIds", [])
                details.append(f"Connections: {len(connections) if connections else 'None'}")
                data[channel] = "\n".join(details)

        # Apply query filter (case-insensitive)
        if query and query.lower() != "none":
            data = {k: v for k, v in data.items() if query.lower() in k.lower()}

        # Pagination setup
        items_per_page = 8
        total_items = len(data)
        total_pages = max(1, (total_items + items_per_page - 1) // items_per_page)

        # Clamp page number
        page = max(1, min(page, total_pages))

        start_index = (page - 1) * items_per_page
        end_index = start_index + items_per_page
        paged_items = list(data.items())[start_index:end_index]

        # Build embed
        embed = discord.Embed(
            title=f"Public {'Search' if query.lower() != 'none' else 'Channels'}",
            color=discord.Color.from_str("0xffb1ff")
        )

        if not paged_items:
            embed.description = f"{emojis['ml_error']} No public channels found."
        else:
            for name, value in paged_items:
                embed.add_field(name=name, value=value, inline=False)

        embed.set_footer(text=f"Page {page} of {total_pages}")
        await ctx.followup.send(embed=embed)

    except Exception as e:
        await ctx.channel.send(f"Error {random.choice(errorMsgs)}\n-# {e}")
    # i asked chatgpt to finish this because this is stupid

@tree.command(name="delete", description="deletes a message from like... everywhere")
@discord.app_commands.describe(message_id="id or link of message to delete")
async def delete(ctx: commands.Context, message_id: str):
    try:
        await ctx.response.defer()

        if "discord.com" in message_id:
            messageId = message_id.rsplit("/", 1)[-1]
        else:
            messageId = message_id

        to_delete = {}
        leadId = None

        global mari_linking

        if str(message_id) in mari_linking:
            leadId = str(message_id)
        else:
            for messagepile in mari_linking:
                if str(message_id) in mari_linking[messagepile]["proxies"]:
                    leadId = messagepile
                    break

        db = load_db()
        channel = mari_linking[leadId]["marichannel"]

        userisadmin = (str(ctx.user.id) in db[channel]["permissions"] and db[channel]["permissions"][str(ctx.user.id)] == "administrator")
        userismod = (str(ctx.user.id) in db[channel]["permissions"] and db[channel]["permissions"][str(ctx.user.id)] == "moderator")
        userisop = (str(ctx.user.id) in db[channel]["permissions"] and db[channel]["permissions"][str(ctx.user.id)] == "operator")

        userisglobaladmin = (str(ctx.user.id) in db["MariLink_Configuration"]["permissions"] and db["MariLink_Configuration"]["permissions"][str(ctx.user.id)] == "administrator")
        userisglobalmod = (str(ctx.user.id) in db["MariLink_Configuration"]["permissions"] and db["MariLink_Configuration"]["permissions"][str(ctx.user.id)] == "moderator")
        userisglobalop = (str(ctx.user.id) in db["MariLink_Configuration"]["permissions"] and db["MariLink_Configuration"]["permissions"][str(ctx.user.id)] == "operator")

        userisowner = ("userId" in db[channel] and db[channel]["userId"] == str(ctx.user.id))
        userisbotowner = (ctx.user.id == evaluser)

        if not (userisadmin or userismod or userisop or userisowner or userisglobaladmin or userisglobalmod or userisglobalop or userisbotowner):
            return await ctx.followup.send(f"{emojis['ml_error']} perms issue")

        if leadId is None:
            await ctx.followup.send(f"{emojis['ml_error']} failed to delete, message not in cache")
            return

        for msgId in mari_linking[leadId]["proxies"]:
            to_delete[msgId] = mari_linking[leadId]["proxies"][msgId][1]

        for messageId in to_delete:
            channel = bot.get_channel(int(to_delete[messageId]))
            msg = await channel.fetch_message(int(messageId))
            await msg.delete()

        channel = bot.get_channel(int(mari_linking[str(leadId)]["channelID"]))
        msg = await channel.fetch_message(leadId)
        await msg.delete()

        mari_linking.pop(leadId, None)

        await ctx.followup.send(f"{emojis['ml_check']} Deleted")
    except Exception as e:
        await ctx.channel.send(f"Error {random.choice(errorMsgs)}\n-# {e}")

# this command is stolen from cat bot but who cares
@bot.tree.command(description="(ADMIN) Change MariLink avatar")
@discord.app_commands.default_permissions(manage_guild=True)
@discord.app_commands.describe(avatar="The avatar to use (leave empty to reset)")
async def changeavatar(message: discord.Interaction, avatar: Optional[discord.Attachment]):
    try:
        await message.response.defer()

        if avatar and avatar.content_type not in ["image/png", "image/jpeg", "image/gif", "image/webp"]:
            await message.followup.send("Invalid file type! Please upload a PNG, JPEG, GIF, or WebP image.", ephemeral=True)
            return

        if avatar:
            avatar_value = discord.utils._bytes_to_base64_data(await avatar.read())
        else:
            avatar_value = None

        try:
            # this isnt supported by discord.py yet
            await bot.http.request(discord.http.Route("PATCH", f"/guilds/{message.guild.id}/members/@me"), json={"avatar": avatar_value})
            await message.followup.send(f"{emojis['ml_check']} Avatar changed successfully!")
        except Exception:
            await message.followup.send(f"{emojis['ml_error']} Failed to change avatar! Your image is too big or you are changing avatars too quickly.", ephemeral=True)
            return
    except Exception as e:
        await ctx.channel.send(f"Error {random.choice(errorMsgs)}\n-# {e}")

@tree.command(name="promote", description="marmite... and now you're fired.")
async def promote(ctx: commands.Context, level: Literal["none", "operator", "moderator", "administrator"], user: str, channel: str = "MariLink_Configuration"):
    try:
        await ctx.response.defer()
        db = load_db()
        if not channel in db:
            return await ctx.followup.send(f"{emojis['ml_error']} not a real channel")
        db[channel].setdefault("permissions", {})
        target = None
        userisadmin = (str(ctx.user.id) in db[channel]["permissions"] and db[channel]["permissions"][str(ctx.user.id)] == "administrator")
        userisglobaladmin = (str(ctx.user.id) in db["MariLink_Configuration"]["permissions"] and db["MariLink_Configuration"]["permissions"][str(ctx.user.id)] == "administrator")
        userisowner = ("userId" in db[channel] and db[channel]["userId"] == str(ctx.user.id))
        userisbotowner = (ctx.user.id == evaluser)
        if not (userisadmin or userisowner or userisglobaladmin or userisbotowner):
            return await ctx.followup.send(f"{emojis['ml_error']} perms issue")
        if user.isdigit():
            target = user
        else:
            if user[0] == '<' and user[1] == '@':
                target = user.replace('<', '').replace('>', '').replace('@', '').replace(' ', '')
            else:
                if user.lower() in usernameCache:
                    target = usernameCache[user.lower()]
                else:
                    return await ctx.followup.send(f"{emojis['ml_error']} Username not known!")
        db[channel]["permissions"][str(target)] = level
        if level == "none":
            res = f"{emojis['ml_check']} user <@{target}> demoted"
        else:
            res = f"{emojis['ml_check']} user <@{target}> set to {level}"
        if channel == "MariLink_Configuration":
            res += " globally!!!"
        else:
            res += f" in channel {channel}!!"
        save_db(db)
        await ctx.followup.send(res, allowed_mentions=discord.AllowedMentions.none())
    except Exception as e:
        await ctx.channel.send(f"Error {random.choice(errorMsgs)}\n-# {e}")

@tree.command(name="ban", description="ban/unban person from marilink channel or globally")
async def ban(ctx: commands.Context, user: str, channel: str = "MariLink_Configuration", remove: bool = False):
    try:
        await ctx.response.defer()
        db = load_db()
        if not channel in db:
            return await ctx.followup.send(f"{emojis['ml_error']} not a real channel")
        db[channel].setdefault("bans", {})
        target = None
        userisadmin = (str(ctx.user.id) in db[channel]["permissions"] and db[channel]["permissions"][str(ctx.user.id)] == "administrator")
        userisglobaladmin = (str(ctx.user.id) in db["MariLink_Configuration"]["permissions"] and db["MariLink_Configuration"]["permissions"][str(ctx.user.id)] == "administrator")
        userisowner = ("userId" in db[channel] and db[channel]["userId"] == str(ctx.user.id))
        userisbotowner = (ctx.user.id == evaluser)
        if not (userisadmin or userisowner or userisglobaladmin or userisbotowner):
            return await ctx.followup.send(f"{emojis['ml_error']} perms issue")
        if user.isdigit():
            target = user
        else:
            if user[0] == '<' and user[1] == '@':
                target = user.replace('<', '').replace('>', '').replace('@', '').replace(' ', '')
            else:
                if user.lower() in usernameCache:
                    target = usernameCache[user.lower()]
                else:
                    return await ctx.followup.send(f"{emojis['ml_error']} Username not known!")
        db[channel]["bans"][str(target)] = not remove
        if remove:
            un = "un"
        else:
            un = ""
        res = f"{emojis['ml_check']} user <@{target}> has been {un}banned"
        if channel == "MariLink_Configuration":
            res += " globally!!!"
        else:
            res += f" in channel {channel}!!"
        save_db(db)
        await ctx.followup.send(res, allowed_mentions=discord.AllowedMentions.none())
    except Exception as e:
        await ctx.channel.send(f"Error {random.choice(errorMsgs)}\n-# {e}")

@tree.command(name="mute", description="mute/unmute person from marilink channel or globally")
async def mute(ctx: commands.Context, user: str, channel: str = "MariLink_Configuration", timeout: int = 15):
    try:
        await ctx.response.defer()
        db = load_db()
        if not channel in db:
            return await ctx.followup.send(f"{emojis['ml_error']} not a real channel")
        db[channel].setdefault("mutes", {})
        target = None

        userisadmin = (str(ctx.user.id) in db[channel]["permissions"] and db[channel]["permissions"][str(ctx.user.id)] == "administrator")
        userisglobaladmin = (str(ctx.user.id) in db["MariLink_Configuration"]["permissions"] and db["MariLink_Configuration"]["permissions"][str(ctx.user.id)] == "administrator")
        userisowner = ("userId" in db[channel] and db[channel]["userId"] == str(ctx.user.id))
        userisbotowner = (ctx.user.id == evaluser)
        userismod = (str(ctx.user.id) in db[channel]["permissions"] and db[channel]["permissions"][str(ctx.user.id)] == "moderator")
        userisglobalmod = (str(ctx.user.id) in db["MariLink_Configuration"]["permissions"] and db["MariLink_Configuration"]["permissions"][str(ctx.user.id)] == "moderator")

        if not (userisadmin or userisowner or userisglobaladmin or userisbotowner or userismod or userisglobalmod):
            return await ctx.followup.send(f"{emojis['ml_error']} perms issue")

        if user.isdigit():
            target = user
        else:
            if user[0] == '<' and user[1] == '@':
                target = user.replace('<', '').replace('>', '').replace('@', '').replace(' ', '')
            else:
                if user.lower() in usernameCache:
                    target = usernameCache[user.lower()]
                else:
                    return await ctx.followup.send(f"{emojis['ml_error']} Username not known!")
        db[channel]["mutes"][str(target)] = int(time.time())+(timeout*60)
        if not timeout:
            un = "un"
        else:
            un = ""
        res = f"{emojis['ml_check']} user <@{target}> has been {un}muted"
        if timeout:
            res += f" {timeout} minutes"
        if channel == "MariLink_Configuration":
            res += " globally!!!"
        else:
            res += f" in channel {channel}!!"
        save_db(db)
        await ctx.followup.send(res, allowed_mentions=discord.AllowedMentions.none())
    except Exception as e:
        await ctx.channel.send(f"Error {random.choice(errorMsgs)}\n-# {e}")

# --- debug commads --- #

@bot.command(help="simple eval command")
async def output(ctx, *, prompt: str):
    if ctx.author.id == evaluser:
        try:
            result = eval(prompt, {"__builtins__": __builtins__}, {})
            if asyncio.iscoroutine(result):
                result = await result
            if result is None:
                await ctx.send("Success!")
            else:
                await ctx.send(str(result))
        except Exception as e:
            await ctx.send(str(e))

@bot.command(help="complex eval command, needs handling")
async def execute(ctx, *, prompt: str):
    if ctx.author.id == evaluser:
        # complex eval, multi-line + async support
        # requires the full `await message.channel.send(2+3)` to get the result
        # thanks mia lilenakos
        spaced = ""
        for i in prompt.split("\n"):
            spaced += "  " + i + "\n"

        intro = (
            "async def go(prompt, bot, ctx):\n"
            " try:\n"
        )
        ending = (
            "\n except Exception:\n"
            "  await ctx.send(traceback.format_exc())"
            "\nbot.loop.create_task(go(prompt, bot, ctx))"
        )

        complete = intro + spaced + ending
        exec(complete)

@bot.command(help="gets a user's id from username")
async def id_lookup(ctx, *, prompt: str):
    if ctx.author.id == evaluser:
        name = prompt.split()[0]
        if name in usernameCache:
            await ctx.send(usernameCache[name])
        else:
            await ctx.send("Username not known!")

@bot.command(help="restarts the bot")
async def restart(ctx):
    if ctx.author.id == evaluser:
        print("restart has been triggered...")
        await ctx.send("restarting bot...")
        os.execv(sys.executable, ['python'] + sys.argv)

@bot.command(help="ok bro")
async def status(ctx, *, prompt: str):
    if ctx.author.id == evaluser:
        try:
            await bot.change_presence(activity=discord.CustomActivity(name=prompt))
            await ctx.send(f"Status updated to: {prompt}")
        except Exception as e:
            await ctx.send(str(e))

# --- misc functions --- #

def load_db():
    try:
        with open('db.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_db(data):
    with open('db.json', 'w') as f:
        json.dump(data, f, indent=4)

# --- events --- #

@bot.event
async def on_ready():
    await bot.tree.sync()
    bot.session = aiohttp.ClientSession()
    print("MariLink logged in!")
    if VerString == "Dev":
        Status = f"MariLink CE Development Version"
    else:
        Status = f"MariLink CE v{VerString}"
    await bot.change_presence(activity=discord.CustomActivity(name=Status))

@bot.event
async def on_message_delete(message: discord.Message):
    await asyncio.sleep(5) # prevents race conditions

    if message.author.id == bot.user.id:
        return # dont respond to itself

    if message.webhook_id and not message.interaction_metadata: # allow application commands
        return # dont respond to webhooks, often sent by the bot itself

    messageId = message.id

    to_delete = {}
    leadId = None

    global mari_linking

    if str(messageId) in mari_linking:
        leadId = str(messageId)

    if leadId is None:
        return

    if not leadId in mari_linking:
        return

    if not "proxies" in mari_linking[leadId]:
        return

    for msgId in mari_linking[leadId]["proxies"]:
        to_delete[msgId] = mari_linking[leadId]["proxies"][msgId][1]

    for messageId in to_delete:
        try:
            channel = bot.get_channel(int(to_delete[messageId]))
            msg = await channel.fetch_message(int(messageId))
            await msg.delete()
        except Exception as e:
            print(f"deleting error, likely perms issue\n{e}")
            await channel.send("deleting error, likely perms issue (MariLink CE needs manage messages)")

    mari_linking.pop(leadId, None)

@bot.event
async def on_message_edit(before: discord.Message, message: discord.Message):
    await asyncio.sleep(5) # prevents race conditions

    if message.author.id == bot.user.id:
        return # dont respond to itself

    if message.webhook_id and not message.interaction_metadata: # allow application commands
        return # dont respond to webhooks, often sent by the bot itself

    messageId = message.id

    to_edit = {}
    leadId = None

    db = load_db()

    global mari_linking

    if str(messageId) in mari_linking:
        leadId = str(messageId)

    if leadId is None:
        return

    if not leadId in mari_linking:
        return

    if not "proxies" in mari_linking[leadId]:
        return

    for msgId in mari_linking[leadId]["proxies"]:
        to_edit[msgId] = mari_linking[leadId]["proxies"][msgId][1]

    mlchannel = mari_linking[leadId]["marichannel"]

    db[mlchannel].setdefault("mutes", {})
    db[mlchannel].setdefault("bans", {})
    db["MariLink_Configuration"].setdefault("mutes", {})
    db["MariLink_Configuration"].setdefault("bans", {})

    userismuted = (str(message.author.id) in db[mlchannel]["mutes"] and db[mlchannel]["mutes"][str(message.author.id)] > int(time.time()))
    userisbanned = (str(message.author.id) in db[mlchannel]["bans"] and db[mlchannel]["bans"][str(message.author.id)])
    userisglobalmuted = (str(message.author.id) in db["MariLink_Configuration"]["mutes"] and db["MariLink_Configuration"]["mutes"][str(message.author.id)] > int(time.time()))
    userisglobalbanned = (str(message.author.id) in db["MariLink_Configuration"]["bans"] and db["MariLink_Configuration"]["bans"][str(message.author.id)])

    usermoderated = (userismuted or userisbanned or userisglobalmuted or userisglobalbanned)

    if usermoderated:
        return

    for messageId in to_edit:
        try:
            channel = bot.get_channel(int(to_edit[messageId]))
            msg = await channel.fetch_message(int(messageId))

            # get webhooke
            webhook = None

            webhook_id = msg.author.id

            try:
                webhooks = await channel.webhooks()
                webhook = discord.utils.get(webhooks, id=webhook_id)
            except (discord.NotFound, discord.Forbidden):
                webhook = None

            if webhook is None:
                return

            # regenerate the message content

            if True: # cant be bothered to unindent all this
                sticker_data = ""
                if message.stickers:
                    sticker = message.stickers[0]
                    if sticker.format == StickerFormatType.gif:
                        suffix = ".gif"
                    else:
                        suffix = ".png"
                    sticker_data = f"[{sticker.name}](https://media.discordapp.net/stickers/{sticker.id}{suffix})"

                message_data = message.content + sticker_data

                if message.reference:
                    try:
                        ogmsg = await message.channel.fetch_message(message.reference.message_id)
                    except Exception:
                        ogmsg = None
                    deactiveurl = r"(https?://\S+)"
                    if ogmsg is not None:
                        omlmsg = ogmsg.content
                        if ogmsg.content.startswith(f"-# ┌ <:reply:") or ogmsg.content.startswith(f"-# ┌ <:command:"):
                            omlmsg = " ".join(ogmsg.content.splitlines()[1:])
    
                        elipse = ""
                        if len(omlmsg) > 128:
                            elipse = "..."
    
                        msgcont = re.sub(deactiveurl, r"<\1>", omlmsg).replace('\n', ' ')[:128] + elipse

                        quserisbanned = (str(ogmsg.author.id) in db[mlchannel]["bans"] and db[mlchannel]["bans"][str(ogmsg.author.id)])
                        quserisglobalbanned = (str(ogmsg.author.id) in db["MariLink_Configuration"]["bans"] and db["MariLink_Configuration"]["bans"][str(ogmsg.author.id)])
                        qusermoderated = (quserisbanned or quserisglobalbanned)

                        if qusermoderated:
                            msgcont = "[Blocked Message]"

                        aorther = str(ogmsg.author).replace('#0000', '').replace(' [Via MariLink]', '')
                        reply_thing = f"-# ┌ {emojis['reply']} **@{str(re.sub(r'\([^)]*\)', '', aorther).strip())}**: {msgcont}\n"
                    else:
                        reply_thing = f"-# ┌ {emojis['reply']} *Original message was deleted*\n"
                    message_data = reply_thing + message_data

                # bot stuff
                if not message.author.bot and not message.webhook_id:
                    embeds = []
                else:
                    embeds = message.embeds

                if message.interaction_metadata:
                    commandname = "unknown-name"
                    cmd_msg = await bot.http.request(discord.http.Route("GET", f"/channels/{message.channel.id}/messages/{message.id}")) # interaction_metadata lacks command name parameter because fuck me ig
                    if "interaction" in cmd_msg:
                        if "name" in cmd_msg["interaction"]:
                            commandname = cmd_msg["interaction"]["name"]

                    command_thing = f"-# ┌ {emojis['command']} **@{message.interaction_metadata.user.name}** used `/{commandname}`\n"
                    message_data = command_thing + message_data
    
                await webhook.edit_message(messageId, content=(message_data or "-# no message content\n"), embeds=embeds)
        except Exception as e:
            print(f"ERROR!\n{e}")

@bot.event
async def on_message(message: discord.Message):
    if message.author.id == bot.user.id:
        return # dont respond to itself
    if message.webhook_id and not message.interaction_metadata: # allow application commands
        return # dont respond to webhooks, often sent by the bot itself

    # add username to cache, used for moderation
    global usernameCache
    if not message.author.name in usernameCache and not message.author.bot:
        usernameCache[message.author.name] = message.author.id

    await bot.process_commands(message) # processes text commands
    db = load_db()
    mlchannel = None

    for entry in db:
        if "discordChannelIds" in db[entry]:
            if str(message.channel.id) in db[entry]["discordChannelIds"]:
                mlchannel = entry
                break

    if mlchannel is None:
        return

    if "allow_bots" in db[mlchannel]:
        if db[mlchannel]["allow_bots"] == False:
            if message.author.bot:
                return

    db[mlchannel].setdefault("mutes", {})
    db[mlchannel].setdefault("bans", {})
    db["MariLink_Configuration"].setdefault("mutes", {})
    db["MariLink_Configuration"].setdefault("bans", {})

    userismuted = (str(message.author.id) in db[mlchannel]["mutes"] and db[mlchannel]["mutes"][str(message.author.id)] > int(time.time()))
    userisbanned = (str(message.author.id) in db[mlchannel]["bans"] and db[mlchannel]["bans"][str(message.author.id)])
    userisglobalmuted = (str(message.author.id) in db["MariLink_Configuration"]["mutes"] and db["MariLink_Configuration"]["mutes"][str(message.author.id)] > int(time.time()))
    userisglobalbanned = (str(message.author.id) in db["MariLink_Configuration"]["bans"] and db["MariLink_Configuration"]["bans"][str(message.author.id)])

    usermoderated = (userismuted or userisbanned or userisglobalmuted or userisglobalbanned)

    if usermoderated:
        icon = emojis['ml_mute']
        if userisbanned or userisglobalbanned:
            icon = emojis['ml_ban']
        msg = f"{icon} you are "
        if userisglobalbanned:
            msg += "globally banned from marilink"
        elif userisbanned:
            msg += f"banned in {mlchannel}"
        elif userisglobalmuted:
            msg += f"globally muted in marilink and can talk again <t:{db['MariLink_Configuration']['mutes'][str(message.author.id)]}:R>"
        elif userismuted:
            msg += f"muted in {mlchannel} and can talk again <t:{db[mlchannel]['mutes'][str(message.author.id)]}:R>"
        return await message.reply(msg)

    global mari_linking # caches messages and their proxied message IDs and webhooks
    mari_linking[str(message.id)] = {"channelID": str(message.channel.id), "marichannel": mlchannel}

    db.setdefault("MariLink_Configuration", {})
    db["MariLink_Configuration"].setdefault("webhooks", {})

    message_data = message.content

    for channelid in db[mlchannel]["discordChannelIds"]:
        try:
            if not message.channel.id == int(channelid):
                webhook = None
                webhook_id = False
                channel = bot.get_channel(int(channelid))

                if str(channelid) in db["MariLink_Configuration"]["webhooks"]:
                    webhook_id = db["MariLink_Configuration"]["webhooks"][str(channelid)]

                if webhook_id:
                    try:
                        webhooks = await channel.webhooks()
                        webhook = discord.utils.get(webhooks, id=webhook_id)
                    except (discord.NotFound, discord.Forbidden):
                        webhook = None

                if webhook is None:
                    webhook_obj = await channel.create_webhook(
                        name="MariLink Webhook",
                        avatar=mlav
                    )
                    webhook_id = webhook_obj.id
                    db["MariLink_Configuration"]["webhooks"][str(channelid)] = webhook_id
                    save_db(db)
                    webhook = webhook_obj
    
                inch = f" (in #{mlchannel}) "
                blacklisted_words = ["discord", "nitro", "clyde"]
                for word in blacklisted_words:
                    if word in inch:
                        inch = ""
                        break

                author_name = f"{message.author}{inch}[Via MariLink]"
                avatar_url = message.author.display_avatar.url if message.author.display_avatar else None

                sticker_data = ""
                if message.stickers:
                    sticker = message.stickers[0]
                    if sticker.format == StickerFormatType.gif:
                        suffix = ".gif"
                    else:
                        suffix = ".png"
                    sticker_data = f"[{sticker.name}](https://media.discordapp.net/stickers/{sticker.id}{suffix})"

                message_data = message_data + sticker_data
                files = []
                if message.attachments:
                    async with aiohttp.ClientSession() as session:
                        for attachment in message.attachments:
                            async with session.get(attachment.url) as resp:
                                if resp.status == 200:
                                    data = await resp.read()
                                    fp = io.BytesIO(data)
                                    fp.seek(0)
                                    files.append(discord.File(fp, filename=attachment.filename))
    
                if message.reference:
                    ogmsg = await message.channel.fetch_message(message.reference.message_id)

                    quserisbanned = (str(ogmsg.author.id) in db[mlchannel]["bans"] and db[mlchannel]["bans"][str(ogmsg.author.id)])
                    quserisglobalbanned = (str(ogmsg.author.id) in db["MariLink_Configuration"]["bans"] and db["MariLink_Configuration"]["bans"][str(ogmsg.author.id)])
                    qusermoderated = (quserisbanned or quserisglobalbanned)

                    deactiveurl = r"(https?://\S+)"
    
                    omlmsg = ogmsg.content
                    if ogmsg.content.startswith(f"-# ┌ {emojis['reply']}"):
                        omlmsg = " ".join(ogmsg.content.splitlines()[1:])
    
                    elipse = ""
                    if len(omlmsg) > 128:
                        elipse = "..."
    
                    msgcont = re.sub(deactiveurl, r"<\1>", omlmsg).replace('\n', ' ')[:128] + elipse

                    if qusermoderated:
                        msgcont = "[Blocked Message]"

                    aorther = str(ogmsg.author).replace('#0000', '').replace(' [Via MariLink]', '')
                    reply_thing = f"-# ┌ {emojis['reply']} **@{str(re.sub(r'\([^)]*\)', '', aorther).strip())}**: {msgcont}\n"
                    message_data = reply_thing + message_data

                # bot stuff
                if not message.author.bot and not message.webhook_id:
                    embeds = []
                else:
                    embeds = message.embeds

                if message.interaction_metadata:
                    commandname = "unknown-name"
                    cmd_msg = await bot.http.request(discord.http.Route("GET", f"/channels/{message.channel.id}/messages/{message.id}")) # interaction_metadata lacks command name parameter because fuck me ig
                    if "interaction" in cmd_msg:
                        if "name" in cmd_msg["interaction"]:
                            commandname = cmd_msg["interaction"]["name"]

                    command_thing = f"-# ┌ {emojis['command']} **@{message.interaction_metadata.user.name}** used `/{commandname}`\n"
                    message_data = command_thing + message_data
    
                if not files:
                    message_data = message_data or "-# no message content\n"
    
                webhook_msg = await webhook.send(
                    content=message_data[:2000],
                    username=author_name[:80],
                    avatar_url=avatar_url,
                    files=files,
                    wait=True,
                    allowed_mentions=discord.AllowedMentions.none(),
                    embeds=embeds
                )
                mari_linking[str(message.id)].setdefault("proxies", {})
                mari_linking[str(message.id)]["proxies"][str(webhook_msg.id)] = [webhook_id, webhook_msg.channel.id]
        except Exception as e:
            print(f"ERROR!\n{e}")
# --- login --- #
bot.run(TOKEN)
