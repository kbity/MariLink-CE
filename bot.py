# --- imports --- #

import discord, traceback, random, json, re, aiohttp, io
from discord import app_commands
from discord.ext import commands
from typing import Literal

# --- setup --- #

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='ml!', intents=intents)
tree = bot.tree
usernameCache = {}
mari_linking = {}

mlav = None
with open("img.png", "rb") as image:
  f = image.read()
  mlav = bytearray(f)

# --- quick config --- #

evaluser = 798072830595301406 # Bot owner Id.

TOEKN = "X" # Phil, replace this with dotenv by Dev Build 17. Thanks.

VerString = "Dev" # Version String

# these are random strings used in the bot
errorMsgs = ["500 Internal Server Error", "501 Not Implemented", "502 Bad Gateway", "503 Service Unavailable", "504 Gateway Timeout", "505 HTTP Version Not Supported", "506 Variant Also Negotiates", "507 Insufficient Storage", "508 Loop Detected", "509 Bandwidth Limit Exceeded", "510 Not Extended", "511 Network Authentication Required", "520 Web Server Returned an Unknown Error", "521 Web Server Is Down", "522 Connection Timed Out", "523 Origin Is Unreachable", "524 A Timeout Occurred", "525 SSL Handshake Failed", "526 Invalid SSL Certificate", "527 Railgun Error", "529 Site is overloaded", "530 Origin DNS Error", "540 Temporarily Disabled", "555 User Defined Resource Error", "561 Unauthorized", "598 Network read timeout error", "599 Network Connect Timeout Error", "618 Too Many Cubes\n-# ✨ You got the Rare Error"]

whatce = ["Community Edition", "Crystal Ediquite", "Cpython rEwrite", "Crazy Edition", "Colour Edition", "Cell machinE", "AX Zirconium" "Ceiling Effects", "Chilled Estrogen", "CD Easy", "Citem Easylum is way more interesting", "Cool Explosions", "Countless Errors", "CEASCE", "Creating Elephants", "Cyeah ok libEral", "Ceroba Edition", "Classic Edition", "(fan) Cervice Edition", "99 bottles of iCE cold beer", "Creisi Edition", "Cesium Edition", "Community edition??", "Cinnamon Edition", "Chocolate and Eggs", "CariEink", "Cerium", "ChEchen language", "Common Era", "Customer Edge", "Calculator Edition"]

# --- commands --- #

@tree.command(name="createchannel", description="creates marilink channel")
async def createchannel(ctx: commands.Context, name: str, password: str = None, public: bool = False, mode: Literal["Normal", "Strange", "TwoPoint", "OneWay"] = "Normal"):
    discordChannelIds = None
    try:
        db = load_db()
        if password is None:
            await ctx.response.defer()
        else:
            await ctx.response.defer(ephemeral=True)
        res = f"ok i totally created `{name}` as a `{mode}` channel"
        if public and password is not None:
            await ctx.followup.send("vro pick one like buddy lmao wtf?? you cant have a password on a public channel what the fuck is wrong with you :rofl::rofl:")
            return
        if public and mode == "TwoPoint":
            await ctx.followup.send("pretty sure you dont want to do this. either way, its not allowed.")
            return
        if name == "MariLink_Configuration":
            await ctx.followup.send("this name is ass bro")
            return
        if len(name) > 26:
            await ctx.followup.send("channel names can only be as long as 26 characters. just think about it, 26 is plenty, im sure.")
            return
        if password is None:
            res = res + " with no password"
        if public:
            res = res + " that is public"
        if name in db:
            if db[name]["userId"] == str(ctx.user.id):
                if "discordChannelIds" in db[name]:
                    discordChannelIds = db[name]["discordChannelIds"]

                if (not "Type" in db[name]) or (not db[name]["Type"] == "TwoPoint"):
                    if mode == "TwoPoint":
                        await ctx.followup.send("cannot convert normal channel to TwoPoint channel")
                        return

                res = res + "\n-# (Channel Edited)"
            else:
                await ctx.followup.send("channel already exists!")
                return
        if password is not None and mode == "TwoPoint":
            res = res + "\n-# btw setting passwords is pointless on TwoPoint channels"
        db[name] = {}
        db[name]["userId"] = str(ctx.user.id)
        if password is not None:
            db[name]["password"] = password
        if public:
            db[name]["isPublic"] = public
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
                await ctx.followup.send("not yours <:normal:1415470137464717373>")
                return
        else:
            await ctx.followup.send("channel does not exists")
            return

        res = f"channel `{name}` no longer exists, assuming it existed in the first place"

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
            await ctx.followup.send("you're not the permission-doer 🥸")
            return

        if not name in db:
            await ctx.followup.send("that channel doesnt exist you absolute buffoon")
            return

        #plaintext-grade security
        if "password" in db[name]:
            if not db[name]["password"] == password and not db[name]["userId"] == str(ctx.user.id):
                await ctx.followup.send("wrong password!")
                return

        if "Type" in db[name] and db[name]["Type"] == "TwoPoint":
            if not db[name]["userId"] == str(ctx.user.id):
                await ctx.followup.send("not your channel")
                return

        res = f"✅ `{name}` linked to <#{ctx.channel.id}>"

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
            await ctx.followup.send("you're not the permission-doer 🥸")
            return

        mlchannel = None

        for entry in db:
            if "discordChannelIds" in db[entry]:
                if str(ctx.channel.id) in db[entry]["discordChannelIds"]:
                    mlchannel = entry
                    break

        if mlchannel is None:
            await ctx.followup.send(f"<#{ctx.channel.id}> didn't seem to link anywhere")
            return

        db[mlchannel]["discordChannelIds"].remove(str(ctx.channel.id))

        res = f"✅ `{mlchannel}` unlinked from <#{ctx.channel.id}>"
        await ctx.followup.send(res)
        save_db(db)

    except Exception as e:
        await ctx.channel.send(f"Error {random.choice(errorMsgs)}\n-# {e}")

@tree.command(name="about", description="what is marilink and why is it ce now")
async def unlink(ctx: commands.Context):
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

# --- debug commads --- #

@bot.command(help="might run code i'm not sure")
async def do(ctx, *, prompt: str):
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

@bot.command(help="runs code i think")
async def run(ctx, *, prompt: str):
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

@bot.event
async def on_message(message):
    if message.author.id == bot.user.id:
        return # dont respond to itself
    if message.webhook_id:
        return # dont respond to webhooks, often sent by the bot itself

    # add username to cache, used for moderation
    global usernameCache
    if not message.author.name in usernameCache and not message.author.bot:
        usernameCache[message.author.name] = message.author.id

    global mari_linking # caches messages and their proxied message IDs and webhooks
    mari_linking[str(message.id)] = {}

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

    db.setdefault("MariLink_Configuration", {})
    db["MariLink_Configuration"].setdefault("webhooks", {})

    message_data = message.content

    for channelid in db[mlchannel]["discordChannelIds"]:
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
                deactiveurl = r"(https?://\S+)"
                elipse = ""
                if len(ogmsg.content) > 128:
                    elipse = "..."
                msgcont = re.sub(deactiveurl, r"<\1>", ogmsg.content).replace('\n', ' ')[:128] + elipse
                aorther = str(ogmsg.author).replace('#0000', '').replace(' [Via MariLink]', '')
                reply_thing = f"-# ┌ <:reply:1274886824652832788> **@{str(re.sub(r'\([^)]*\)', '', aorther).strip())}**: {msgcont}\n"
                message_data = reply_thing + message_data

            if not files:
                message_data = message_data or "-# no message content\n"

            webhook_msg = await webhook.send(
                content=message_data[:2000],
                username=author_name,
                avatar_url=avatar_url,
                files=files,
                wait=True,
                allowed_mentions=discord.AllowedMentions.none()
            )
            mari_linking[str(message.id)][str(webhook_msg.id)] = webhook_id

# --- login --- #
bot.run(TOEKN)
