# This is SlasherBot, my custom Discord Bot made in Python

In here you can find the source code for my Discord bot, I've called it SlasherBot for now, but that will likely change. I don't have any plans to make this public unless for some reason it becomes useful.

bot.py is the base file for running the bot and connecting all of the modules to it. In the future I will make a GUI for the bot containing all kinds of cool information!

Inside the modules folder is slasherUtils.py, this is where I keep all of my custom functions/classes for the bot. ~~It's a little bit barren right now, as I made it when I was still fairly new to Python, so I've figured out better ways to do pretty much everything in there. Figured I'd keep it for historical purposes. :)~~ | Removed the useless functions and instead created more widely useful functions and classes that can be used from every other module. Also added __init__.py to the modules folder, allowing easier integration.

Below I'll explain each module, and if you were sent here via my Resume, I'd love to hear your thoughts on this project!

## New Additions

Just completed a new Steam game update notification system thing.

You can choose the game you want to watch, the specific attributes of the game, specific beta branches, etc.

Can also customize how you're notified. Right now it's limited to just sending a message in a chosen channel, but I'm going to allow the bot to DM specific users. Due to it being a private bot for my personal usage, I'm not planning on adding a system for users to customize their notifications. Maybe though, won't rule anything out.

This module was a bit of a disaster to implement because the Steam API library I'm using uses gevent for asynchronous requests, while the rest of the bot uses asyncio - managed to fix it with some tweaking and a custom library I found called asyncio_gevent.

--
Updated SlasherUtils.py with useful functions/classes.
Removed all the .json files and .bat files as they're mostly useless. If for whatever reason you're interested in the raw API data, please check out the sources listed below.

## Starship API

### _API by [@NoahPrail](https://twitter.com/NoahPrail) on Twitter and [starshipstatus.space](https://starshipstatus.space/)_

In modules > starship you'll find my newest addition, this script grabs (nearly) realtime data from Starbase, TX home to the SpaceX South Texas Launch Site.
The script makes an API call to an API made by @NoahPrail on Twitter, this returns a ton of information including Weather, Temporary Flight Restrictions, and road closures.
There is a huge community of people that cover all the happenings at Starbase. The road closures are a great indication of when things are happening, as they are closed when transporting the booster, ship, or even ground support equipment.

Once launches resume, hopefully in September, there will likely be more information regarding launches and general launch information. This will be awesome info to be able to play with.

Right now it returns the number of active TFRs, number of active road closures, current weather, and the time it was last updated.
I am working on a way to request information via my script to get specific information. For example this could be humidity, air pressure, TFR dates, road closure status, etc.

## Space

This module's name might be a little too vague.

Right now it contains the orbits module, which makes a call to "le-systeme-solaire.net", and it returns tons of cool orbital numbers and other cool bits of information about any body in our Solar System.

Users can freely search for planets and moons, and they will receive a nicely formatted message containing all of the cool info like Apogee/Perigee, eccentricity, escape velocity, gravity, and tons more!

## NASA

The NASA Public APIs have tons of cool data and things for me to play around with, currently it only has "apod" which is NASA's "Astronomy Picture of the Day" API. Basically it just gives you a cool space-related image when you call it in Discord.

## Math

Because everyone loves math!

This module is (for now) here just for fun. There is only one function in it currently, which is a cool little mathematical algorithm that applies a set a rules to some numbers, and no matter what number you enter, and no matter how many times you iterate, it will always converge to 1. Cool stuff!
