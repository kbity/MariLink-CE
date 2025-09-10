# --- imports --- #

import discord, traceback, random, json
from discord import app_commands
from discord.ext import commands
from typing import Literal

# --- setup --- #

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='ml!', intents=intents)
tree = bot.tree

# --- quick config --- #

evaluser = 798072830595301406
TOEKN = "n"
errorMsgs = ["500 Internal Server Error", "501 Not Implemented", "502 Bad Gateway", "503 Service Unavailable", "504 Gateway Timeout", "505 HTTP Version Not Supported", "506 Variant Also Negotiates", "507 Insufficient Storage", "508 Loop Detected", "509 Bandwidth Limit Exceeded", "510 Not Extended", "511 Network Authentication Required", "520 Web Server Returned an Unknown Error", "521 Web Server Is Down", "522 Connection Timed Out", "523 Origin Is Unreachable", "524 A Timeout Occurred", "525 SSL Handshake Failed", "526 Invalid SSL Certificate", "527 Railgun Error", "529 Site is overloaded", "530 Origin DNS Error", "540 Temporarily Disabled", "555 User Defined Resource Error", "561 Unauthorized", "598 Network read timeout error", "599 Network Connect Timeout Error", "618 Too Many Cubes\n-# ✨ You got the Rare Error"]

# --- commands --- #

@tree.command(name="createchannel", description="creates marilink channel")
async def ping(ctx: commands.Context, name: str, password: str = None, public: bool = False, mode: Literal["Normal", "Strange", "TwoPoint", "OneWay"] = "Normal"):
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
        if name == "MariLink_Configuration":
            await ctx.followup.send("this name is ass bro")
            return
        if password is None:
            res = res + " with no password"
        if public:
            res = res + " that is public"
        if name in db:
            if db[name]["userId"] == str(ctx.user.id):
                if "discordChannelIds" in db[name]:
                    discordChannelIds = db[name]["discordChannelIds"]
                res = res + "\n-# (Channel Edited)"
            else:
                await ctx.followup.send("channel already exists!")
                return
        db[name] = {}
        db[name]["userId"] = str(ctx.user.id)
        if password is not None:
            db[name]["password"] = password
        if public:
            db[name]["isPublic"] = public
        if discordChannelIds:
            db[name]["discordChannelIds"] = discordChannelIds
        if not mode == "Normal":
            db[name]["Type"] = mode

        await ctx.followup.send(res)
        save_db(db)
    except Exception as e:
        await ctx.channel.send(f"Error {random.choice(errorMsgs)}\n-# {e}")

@tree.command(name="removechannel", description="uncreates marilink channel")
async def ping(ctx: commands.Context, name: str):
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
    print("MariLink logged in!")

# --- login --- #
bot.run(TOEKN)
