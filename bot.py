import os
import discord
import openai
import logging

from modules.math.threex import magicmath
from modules.starship.starship import StarshipStatus
from modules.nasa.nasa import Apod
from modules.space.orbits import OrbitInformation
from discord_slash.model import ContextMenuType, SlashCommandPermissionType
from random import randint
from dotenv import load_dotenv
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
from discord_slash.context import MenuContext
from discord_slash.utils.manage_commands import (
    create_option,
    create_permission,
)

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILDNAME = os.getenv("DISCORD_GUILDNAME")
TESTGUILDID = int(os.getenv("DISCORD_TESTGUILDID"))
TESTADMINROLE = int(os.getenv("DISCORD_TESTADMINROLE"))
LIVEGUILDID = int(os.getenv("DISCORD_LIVEGUILDID"))
LIVEOWNERROLE = int(os.getenv("DISCORD_LIVEOWNERROLE"))
LIVEADMINROLE = int(os.getenv("DISCORD_LIVEADMINROLE"))
LIVEADMINROLE2 = int(os.getenv("DISCORD_LIVEADMINROLE2"))
OWNERID = os.getenv("DISCORD_OWNERID")

APPID = os.getenv("DISCORD_APPID")
OWNER = str(os.getenv("OWNER"))
OPENAI_FINE_TUNE_MODEL = str(os.getenv("FINE_TUNE_MODEL"))
openai.api_key = os.getenv("OPENAI_API_KEY")

DISCORD_API_URL = "https://discord.com/api/v9"
CMDS_URL = (
    f"https://discord.com/api/v9/applications/{APPID}/guilds/{TESTGUILDID}/commands"
)
CMDS_GLOBAL_URL = f"https://discord.com/api/v9/applications/{APPID}/commands"

DIR = os.path.dirname(__file__)
LOG_FILE = os.path.join(DIR, "slasherBot.log")

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all(), owner_id=OWNERID)
slash = SlashCommand(bot, sync_commands=True)


def isOwner(author):
    if str(author) == str(OWNER):
        return True
    else:
        return False


logger = logging.getLogger("discord")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename=LOG_FILE, encoding="utf-8", mode="a")
handler.setFormatter(
    logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
)
logger.addHandler(handler)


@bot.event
async def on_ready():
    print(f"{bot.user.name} has connected to Discord!")


@slash.context_menu(
    target=ContextMenuType.USER, name="Summon", guild_ids=[LIVEGUILDID, TESTGUILDID]
)
async def Summon(ctx: MenuContext):
    chan = await ctx.target_author.create_dm()
    if ctx.author.voice == None:
        msg = f"{ctx.author.name} has summoned you!"
    else:
        msg = f"{ctx.author.name} has summoned you to {ctx.author.voice.channel}!"
    await chan.send(msg)


@slash.slash(  # this command removes the [Original Message Deleted] messages from the free games channel
    name="cleanchat",
    description="Cleans old messages from free games channel",
    guild_ids=[LIVEGUILDID, TESTGUILDID],
    permissions={
        LIVEGUILDID: [
            create_permission(LIVEOWNERROLE, SlashCommandPermissionType.ROLE, True),
            create_permission(LIVEADMINROLE, SlashCommandPermissionType.ROLE, True),
            create_permission(LIVEADMINROLE2, SlashCommandPermissionType.ROLE, True),
        ],
        TESTGUILDID: [
            create_permission(TESTADMINROLE, SlashCommandPermissionType.ROLE, True)
        ],
    },
)
async def cleanchat(ctx: SlashContext):
    channel = discord.utils.get(bot.get_all_channels(), name="the-game-garage")
    i = 0
    async for message in channel.history():
        if message.content == "[Original Message Deleted]":
            i += 1
            await message.delete()
            print("message deleted")


@slash.slash(  # this rolls the bones, inputs are size, and count - size is the size of the die, count is how many dice you wish to roll
    name="roll",
    description="Rolls some dice",
    guild_ids=[TESTGUILDID, LIVEGUILDID],
    options=[
        create_option(
            name="size",
            description="Choose the size of the die you wish to roll",
            required=True,
            option_type=4,
        ),
        create_option(
            name="count",
            description="Choose the number of times you wish to roll (max 10)",
            required=False,
            option_type=4,
        ),
    ],
)
async def slashRoll(
    ctx: SlashContext, size: int, count: int = 1
):  # rewrote this function, i think it looks way better now, but its still probably not the best way to do this
    author = ctx.author
    rolls = []
    i = 0
    while True:
        i += 1
        rolls.append(randint(1, size))
        if i >= count:
            break

    embed = discord.Embed(
        title="The Bones",
        description=f"{author.display_name}'s Rolls: ",
        colour=discord.Colour.red(),
    )
    embed.set_footer(text=f"This is not rigged in any way.")
    embed.set_author(name=author.display_name, icon_url=author.avatar_url)
    n = 1
    for roll in rolls:
        embed.add_field(name=f"Roll {n}:", value=roll, inline=False)
        n += 1
        if n >= 10:
            break

    embed.add_field(name="Total: ", value=sum(rolls), inline=False)
    await ctx.send(embed=embed)


@slash.slash(  # this makes an OpenAI API call to finish your sentences, limited to Ada only for now because it's the cheapest model
    name="openai",
    description="Have OpenAI attempt to finish your sentence",
    guild_ids=[TESTGUILDID, LIVEGUILDID],
    options=[
        create_option(
            name="input", description="Enter a sentence", required=True, option_type=3
        )
    ],
)
async def finishSentence(ctx: SlashContext, input):
    print(input)
    response = openai.Completion.create(
        engine="ada",
        prompt=input,
        temperature=0.9,
        max_tokens=50,
        top_p=1,
        frequency_penalty=0.0,
        presence_penalty=0.6,
        stop="\n",
    )
    response = response["choices"][0]["text"]

    await ctx.send("Input: " + input + "\n\n" + input + response)


@slash.slash(  # this is part of the mini-casino, much more to be added, most of this works though
    name="flip",
    description="Flip some coins",
    guild_ids=[TESTGUILDID, LIVEGUILDID],
    options=[
        create_option(
            name="bet",
            description="What side will it land on?",
            required=True,
            option_type=3,
        )
    ],
)
async def slashFlip(bet):
    flip = randint(0, 1)
    side = "heads" if flip == 0 else "tails"
    outcome = "won!" if side == bet else "lost!"
    print(f"The coin lands on {side}. You {outcome}")


@slash.slash(  # this uses my fine-tuned OpenAI model to pick out useful information from messages regarding unit conversions, work-in-progress
    name="converttest",
    description="convert with ai or something",
    guild_ids=[TESTGUILDID, LIVEGUILDID],
    options=[
        create_option(
            name="prompt", description="convert something", required=True, option_type=3
        )
    ],
)
async def convert_test(ctx: SlashContext, prompt):
    response = openai.Completion.create(
        model=OPENAI_FINE_TUNE_MODEL,
        prompt=prompt,
        temperature=0.9,
        max_tokens=50,
        top_p=1,
        frequency_penalty=0.0,
        presence_penalty=0.6,
        stop="\n",
    )
    response = response["choices"][0]["text"]
    final_response = response.replace(" ->", "")
    await ctx.send(f"Prompt: {prompt}\nResult: {final_response}")


@slash.slash(  # this returns data from the starship status API, more details on that in modules/starship
    name="starship",
    description="Check up on Starship",
    guild_ids=[TESTGUILDID, LIVEGUILDID],
)
async def starship(ctx: SlashContext):
    data = StarshipStatus(update=True)
    embed = discord.Embed(
        title="Starship Status",
        description="Weather, TFRs, and Road Closure Information",
        colour=discord.Colour.blue(),
    )
    embed.set_footer(text=f"Last Updated: {data.update_date}")
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
    embed.add_field(
        name=f"Current Weather in {data.location}:", value=data.weather, inline=False
    )
    embed.add_field(name="Active TFR's:", value=data.num_tfrs, inline=False)
    for closure in data.closures:
        embed.add_field(
            name=f"Road Closure [{closure.status}]:", value=closure, inline=False
        )

    await ctx.send(embed=embed)


@slash.slash(  # this uses NASA's astronomy picture of the day API to give you a cool picture
    name="apod",
    description="Astronomy Picture of the Day",
    guild_ids=[TESTGUILDID, LIVEGUILDID],
)
async def slashApod(ctx: SlashContext):
    apod = Apod()
    apod.get_apod()
    img = apod.hdurl if apod.hdurl != None else apod.url
    embed = discord.Embed(
        title="Astronomy Picture of the Day",
        description=f"{apod.title} by {apod.copyright}",
        colour=discord.Colour.purple(),
    )
    embed.set_footer(text=f"Date: {apod.date}")
    embed.set_author(
        name="NASA",
        icon_url="https://api.nasa.gov/assets/img/favicons/favicon-192.png",
    )
    embed.add_field(name="Explanation", value=apod.explanation)
    embed.set_image(url=img)
    await ctx.send(embed=embed)


@slash.slash(  # this uses cool math to make any number converge down to 1, and then tells the user the largest number it rose to, and how many steps it took to get to 1
    name="threex",
    description="Math Magic",
    guild_ids=[TESTGUILDID, LIVEGUILDID],
    options=[
        create_option(
            name="number",
            description="see how many steps it will take to converge to 1",
            required=True,
            option_type=4,
        )
    ],
)
async def three_x(ctx: SlashContext, number):
    await ctx.send(f"> {magicmath(number)}")


@slash.slash(  # this makes an API call to "Le-Systeme Solaire" and retrieved orbital information about the requested body
    name="orbit",
    description="Get Orbital information about a given body in our Solar System",
    guild_ids=[TESTGUILDID, LIVEGUILDID],
    options=[
        create_option(
            name="body",
            description="body you want information on",
            required=True,
            option_type=3,
        )
    ],
)
async def orbit(ctx: SlashContext, body):
    body = body.lower()
    data = OrbitInformation(body)
    embed = discord.Embed(
        title=f"Orbital Information for {data.name}",
        description="Orbital numbers for a given body",
        colour=discord.Colour.blue(),
    )
    type = "Planet" if data.isPlanet == True else "Moon"
    embed.set_footer(text="Data Provided by Le-Systeme Solaire")
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
    embed.add_field(name="Body Name", value=data.name, inline=True)
    embed.add_field(name="Body Type", value=type, inline=True)
    if type == "Planet":
        embed.add_field(
            name=f"Moons ({data.num_moons})", value=data.moons, inline=False
        )
        embed.add_field(name="Perihelion", value=f"{data.perihelion:,}km", inline=False)
        embed.add_field(name="Aphelion", value=f"{data.aphelion:,}km", inline=False)
    else:
        if body == "moon":
            embed.add_field(
                name="Perigee", value=f"{data.perihelion:,}km", inline=False
            )
            embed.add_field(name="Apogee", value=f"{data.aphelion:,}km", inline=False)
            embed.add_field(name="Parent", value="Earth", inline=False)
        else:
            embed.add_field(
                name="Periapsis", value=f"{data.perihelion:,}km", inline=False
            )
            embed.add_field(name="Apoapsis", value=f"{data.aphelion:,}km", inline=False)
            embed.add_field(
                name="Parent", value=data.aroundPlanet["planet"], inline=False
            )

    embed.add_field(
        name="Semi-Major Axis", value=f"{data.semiMajorAxis:,}km", inline=False
    )
    embed.add_field(name="Eccentricity", value=data.eccentricity, inline=False)
    embed.add_field(
        name="Inclination", value=f"{data.inclination}\N{DEGREE SIGN}", inline=False
    )
    embed.add_field(name="Mass", value=data.mass)
    embed.add_field(name="Volume", value=data.volume)
    embed.add_field(name="Density", value=f"{data.density}g/cm\N{SUPERSCRIPT THREE}")
    embed.add_field(
        name="Gravity", value=f"{data.gravity}m/s\N{SUPERSCRIPT TWO}", inline=False
    )
    embed.add_field(name="Escape Velocity", value=f"{data.escape}m/s", inline=False)
    embed.add_field(name="Mean Radius", value=f"{data.meanRadius}km")
    embed.add_field(name="Equatorial Radius", value=f"{data.equaRadius}km")
    embed.add_field(name="Polar Radius", value=f"{data.polarRadius}km")
    embed.add_field(name="Flattening (??)", value=f"{data.flattening}", inline=False)
    if data.discoveredBy != "":
        embed.add_field(name="Discovered By", value=f"{data.discoveredBy}")
        embed.add_field(name="Discovery Date", value=f"{data.discoveryDate}")
    embed.add_field(
        name="Axial Tilt", value=f"{data.axialTilt}\N{DEGREE SIGN}", inline=False
    )
    embed.add_field(name="Average Temperature", value=f"{data.avgTemp}K", inline=False)
    embed.add_field(name="Long Ascending Node", value=data.longAscNode, inline=False)
    await ctx.send(embed=embed)


if __name__ == "__main__":
    bot.run(TOKEN)
