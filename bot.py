import modules
import os
import sys
import discord
import openai
import logging
import asyncio

from dotenv import load_dotenv
from discord.ext import tasks
from discord.enums import SlashCommandOptionType

# note on the above imports, they are very finicky. one of the modules uses gevent instead of asyncio and it has strange behavior when loaded later

# grabbing environment variables, setting a lot of global variables, most of which are not needed, but useful for testing.
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

DIR = os.path.dirname(os.path.realpath(__file__))
LOG_FILE = os.path.join(DIR, "slasherBot.log")

bot = discord.Bot(command_prefix="!", intents=discord.Intents.all(), owner_id=OWNERID)

# Logging
logger = logging.getLogger("discord")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename=LOG_FILE, encoding="utf-8", mode="a")
handler.setFormatter(
    logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
)
logger.addHandler(handler)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

# logs when the bot is connected and ready to receive commands
@bot.event
async def on_ready():
    logger.info(f"{bot.user.name} has successfully connected to Discord!")


@tasks.loop(minutes=15)
async def check_for_game_updates():
    await bot.wait_until_ready()
    logger.info("Checking for game updates...")
    role_to_mention = 863662006800089120
    channel = bot.get_channel(857891498124247040)
    steam = modules.SteamUpdates()
    response = steam.get_app_info()
    if response is not False:
        keys = response.keys()
        if len(keys) <= 1:
            for app in response:
                app_id = app

            app = steam.get_app(app_id=int(app_id))

            embed = discord.Embed(
                color=discord.Color.blue(),
                title=f"{app.name} Update Detected",
                description=f"<@&{role_to_mention}>",
                url=f"https://steamdb.info/app/{app_id}",
            )
            embed.set_author(
                name="Steam Update",
                url=f"https://store.steampowered.com/app/{app_id}",
                icon_url="https://upload.wikimedia.org/wikipedia/commons/thumb/8/83/Steam_icon_logo.svg/2048px-Steam_icon_logo.svg.png",
            )
            embed.set_image(url=response[app_id]["icon_url"])
            embed.set_footer(text="Data Provided by Slasher Steam Updates")

            old_data_keys = response[app_id]["old_data"].keys()
            new_data_keys = response[app_id]["new_data"].keys()

            for new_key in new_data_keys:
                if new_key not in old_data_keys:
                    embed.add_field(
                        name="New Data",
                        value=f"`{new_key}`: {response[app_id]['new_data'][new_key]}",
                        inline=False,
                    )
                    continue
                for key in old_data_keys:
                    if key not in new_data_keys:
                        removal = (
                            f"`{key}`:{response[app_id]['old_data'][key]} --> Removed"
                        )
                        embed.add_field(
                            name="Removed Data", value=removal, inline=False
                        )
                        continue
                    else:
                        comparison = f"`{key}`:{response[app_id]['old_data'][key]} --> `{new_key}`:{response[app_id]['new_data'][new_key]}"
                        embed.add_field(
                            name="Updated Data", value=comparison, inline=False
                        )

        else:
            app_ids = []
            for app in response:
                app_ids.append(int(app))
            embed = discord.Embed()
            embed.set_author(name="Steam Updates")
            embed.add_field(name="Multiple Games", value=app_ids)
        await channel.send(embed=embed)
    else:
        logger.info("No game updates found.")


check_for_game_updates.start()


@bot.user_command(name="Summon", guild_ids=[LIVEGUILDID, TESTGUILDID])
async def Summon(ctx: discord.ApplicationContext, target: discord.User):
    chan = await target.create_dm()
    if ctx.author.voice == None:
        msg = f"{ctx.author.name} has summoned you!"
    else:
        msg = f"{ctx.author.name} has summoned you to {ctx.author.voice.channel}!"
    await chan.send(msg)


@bot.user_command(name="GetAvatar", guild_ids=[LIVEGUILDID, TESTGUILDID])
async def GetAvatar(ctx: discord.ApplicationContext, target: discord.User):
    if discord.is_owner(ctx.author):
        chan = await ctx.author.create_dm()
        msg = target.display_avatar
        await chan.send(msg)
    else:
        await print("no.")


# debug command, not really used much
@bot.slash_command(name="test", guild_ids=[TESTGUILDID])
async def test(ctx: discord.ApplicationContext):
    await check_for_game_updates()
    # steam = modules.SteamUpdates()
    # bog = steam.get_app_info()
    # await ctx.send(bog)


"""
@bot.slash_command(  # this rolls the bones, inputs are size, and count - size is the size of the die, count is how many dice you wish to roll
    name="roll",
    description="Rolls some dice",
    guild_ids=[TESTGUILDID, LIVEGUILDID],
    options=[
        discord.Option(
            discord.SlashCommandOptionType.INTEGER,
            description="Choose the size of the die you wish to roll",
            required=True,
        ),
        discord.Option(
            discord.SlashCommandOptionType.INTEGER,
            description="Choose the number of times you wish to roll (max 10)",
            required=False,
        ),
    ],
)
async def slashRoll(ctx: discord.ApplicationContext, size: int, count: int = 1):
    author = ctx.interaction.user
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
    embed.set_author(name=author.display_name, icon_url=author.display_avatar)
    n = 1
    for roll in rolls:
        embed.add_field(name=f"Roll {n}:", value=roll, inline=False)
        n += 1
        if n >= 10:
            break

    embed.add_field(name="Total: ", value=sum(rolls), inline=False)
    await ctx.respond(embed=embed)



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
async def finishSentence(ctx: discord.ApplicationContext, input):
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
async def convert_test(ctx: discord.ApplicationContext, prompt):
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
"""


@bot.slash_command(  # this returns data from the starship status API, more details on that in modules/starship
    name="starship",
    description="Check up on Starship",
    guild_ids=[TESTGUILDID, LIVEGUILDID],
)
async def starship(ctx: discord.ApplicationContext):
    data = modules.StarshipStatus(update=True)
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


@bot.slash_command(  # this uses NASA's astronomy picture of the day API to give you a cool picture
    name="apod",
    description="Astronomy Picture of the Day",
    guild_ids=[TESTGUILDID, LIVEGUILDID],
)
async def slashApod(ctx: discord.ApplicationContext):
    apod = modules.Apod()
    apod.get_apod()
    author = apod.copyright if f" by {apod.copyright}" != None else ""
    embed = discord.Embed(
        title="Astronomy Picture of the Day",
        description=f"{apod.title}{author}",
        colour=discord.Colour.purple(),
    )
    embed.set_footer(text=f"Date: {apod.date}")
    embed.set_author(
        name="NASA",
        icon_url="https://api.nasa.gov/assets/img/favicons/favicon-192.png",
    )
    embed.add_field(name="Explanation", value=apod.explanation)
    embed.set_image(url=apod.url)
    await ctx.send(embed=embed)


@bot.slash_command(  # this uses cool math to make any number converge down to 1, and then tells the user the largest number it rose to, and how many steps it took to get to 1
    name="threex", description="Math Magic", guild_ids=[TESTGUILDID, LIVEGUILDID]
)
async def three_x(ctx: discord.ApplicationContext, number):
    await ctx.send(f"> {modules.magicmath(number)}")


@bot.slash_command(  # this makes an API call to "Le-Systeme Solaire" and retrieved orbital information about the requested body
    name="orbit",
    description="Get Orbital information about a given body in our Solar System",
    guild_ids=[TESTGUILDID, LIVEGUILDID],
    options=[
        discord.Option(
            SlashCommandOptionType.string,
            name="body",
            description="body you want information on",
            required=True,
        )
    ],
)
async def orbit(ctx: discord.ApplicationContext, body):
    body = body.lower()
    data = modules.OrbitInformation(body)
    embed = discord.Embed(
        title=f"Orbital Information for {data.name}",
        description="Orbital numbers for a given body",
        colour=discord.Colour.blue(),
    )
    type = "Planet" if data.isPlanet == True else "Moon"
    embed.set_footer(text="Data Provided by Le-Systeme Solaire")
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar)
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


@bot.slash_command(  # returns a random game the gang has in common
    name="randomgame",
    description="Returns a random game the gang owns",
    guild_ids=[TESTGUILDID, LIVEGUILDID],
)
async def randomgame(ctx: discord.ApplicationContext):
    game = modules.goonGames()
    link = f"https://store.steampowered.com/app/{game}"
    await ctx.send(link)


@bot.slash_command(  # returns a quirky message on how to join our game servers
    name="server",
    description="Returns detailed instructions on how to join a Slasher Solutions server.",
    guild_ids=[TESTGUILDID, LIVEGUILDID],
)
async def server_join_msg(ctx: discord.ApplicationContext):
    message = "Join any Slasher Solutions server by using `server.slashersolutions.com` in place of the IP address!"
    embed = discord.Embed(
        title="Slasher Servers", description=message, colour=discord.Colour.blue()
    )
    await ctx.send(embed=embed)


if __name__ == "__main__":
    bot.run(TOKEN)
