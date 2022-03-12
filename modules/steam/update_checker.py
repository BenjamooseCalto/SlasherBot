from steam.client import SteamClient
from steam.enums import EResult
from steam.webapi import WebAPI

import os
import json
import logging

from dotenv import load_dotenv
from modules import get_timestamp, get_time_delta, Cache

logger = logging.getLogger("discord.slasher_updates")

load_dotenv()
STEAM_API_KEY = os.getenv("STEAM_API_KEY")


class AppEncoder(json.JSONEncoder):
    def default(self, o):
        return o.__dict__


class Watchlist:
    def __init__(
        self,
        data_type: str = None,
        name: str = None,
        branch: str = None,
        path: list = None,
        dictionary: dict = None,
    ):
        if not dictionary:
            self.data_type = data_type
            self.name = name
            self.branch = branch
            self.path = path
            self.path = self.path.append(self.branch)
        else:
            self.data_type = dictionary["data_type"]
            self.name = dictionary["name"]
            self.branch = dictionary["branch"]
            self.path = dictionary["path"]

    def get_path(self):
        return self.path


class Update:
    def __init__(
        self,
        watchlist: Watchlist = None,
        new_data: dict = None,
        old_data: dict = None,
        discord_role: str = None,
        app_id: int = None,
        app_icon: str = None,
    ):
        self.watchlist = watchlist
        self.new_data = new_data
        self.old_data = old_data
        self.discord_role = discord_role
        self.app_id = app_id
        self.app_icon = app_icon

    def parse_data(self):
        added = {k: v for k, v in self.new_data.items() if k not in self.old_data}
        removed = {k: v for k, v in self.old_data.items() if k not in self.new_data}
        altered = [
            k
            for k, v in self.new_data.items()
            if k in self.old_data and v != self.old_data[k]
        ]
        altered = {
            "new": {k: v for k, v in self.new_data.items() if k in altered},
            "old": {k: v for k, v in self.old_data.items() if k in altered},
        }
        if "public" in altered["new"].keys() or self.app_id == 108600:
            news = self.get_game_news()
        else:
            news = None
        return added, removed, altered, self.discord_role, news

    def get_game_news(self):
        api = WebAPI(STEAM_API_KEY)
        news = api.ISteamNews.GetNewsForApp_v2(
            appid=self.app_id, count=1, maxlength=300
        )
        logger.debug(f"Game news response: {news}")
        if news["appnews"]["newsitems"][0]["feed_type"] == 0 or 1:
            news = {
                "title": news["appnews"]["newsitems"][0]["title"],
                "url": news["appnews"]["newsitems"][0]["url"],
            }
            return news
        else:
            return None

    def create_output(self):
        added, removed, altered, discord_role, news = self.parse_data()
        output = {
            "watchlist": self.watchlist,
            "added": added,
            "removed": removed,
            "altered": altered,
            "role": discord_role,
            "icon": self.app_icon,
            "news": news,
        }
        return output


class SteamApp:
    def __init__(
        self,
        id: int = None,
        name: str = None,
        dictionary: dict = None,
        discord_role: int = None,
    ):
        if not dictionary:
            logging.info("Creating new SteamApp")
            self.id = id
            self.name = name
            self.watchlist = []
            self.discord_role = discord_role
        else:
            logging.info("Loading SteamApp from dictionary")
            self.id = dictionary["id"]
            self.name = dictionary["name"]
            self.watchlist = self.load_watchlist(dictionary["watchlist"])
            self.discord_role = dictionary["discord_role"]

    def load_watchlist(self, dictionary: dict):
        the_list = []
        for entry in dictionary:
            the_list.append(Watchlist(dictionary=entry))
        return the_list

class SteamUpdates:
    def __init__(
        self,
    ):
        self.client = SteamClient()
        self.apps = []
        self.cache = Cache()
        self.update_freq = 0  # how often to check for updates in minutes

        self.login()
        if self.load_config():
            logger.info("Loaded config from cache")
        else:
            logger.info("No config found in cache")

    def login(self):
        login = self.client.anonymous_login()
        if login == EResult.OK:
            return True
        else:
            return False

    def get_app(self, app_id: int = None, app_name: str = None):
        for app in self.apps:
            if app.id == app_id or app.name == app_name:
                return app
        return None

    def save_config(self):
        config = {"apps": self.apps}
        self.cache.write_to_cache(
            config, "steam", "update_config.json", encoder=AppEncoder
        )

    def load_config(self):
        config = self.cache.read_from_cache("steam", "update_config.json")
        if config is not None:
            for app in config["apps"]:
                item = SteamApp(dictionary=app)
                self.apps.append(item)
            return True
        else:
            return False

    def get_app_info(self):
        logger.info("Updating Steam app info...")

        self.old_data = self.cache.read_from_cache("steam", "app_info.json")
        if (
            get_time_delta(self.old_data["last_updated"], get_timestamp())
            < self.update_freq
        ):
            logger.info("App info is up to date")
            self.app_info = self.old_data
        else:
            self.app_info = self.client.get_product_info(
                apps=[app.id for app in self.apps],
            )
            self.cache.write_to_cache(self.app_info, "steam", "app_info.json")
            self.app_info = self.cache.read_from_cache("steam", "app_info.json")

        return self.check_for_updates()

    def check_for_updates(self):
        logger.info("Checking for updates...")
        checklist = {str(app.id): app.watchlist for app in self.apps} # makes a dict of everything we need to check
        updates = {str(app.id): "" for app in self.apps} # this is where we'll store the updates
        app_update_found = False # just a variable to use if we find an update
        for app in checklist:  # check updates on every app
            main_app = self.get_app(app_id=int(app)) # get the app object
            app_data = self.app_info["apps"][app]  # get app data for specific app
            old_app_data = self.old_data["apps"][app]  # same here but with the old data
            for watchlist in checklist[app]:  # check data for each watchlist
                for key in watchlist.get_path():  # check each path in the watchlist
                    app_data = app_data[key]
                    old_app_data = old_app_data[key]
                if app_data != old_app_data:
                    update = Update(
                        watchlist=watchlist,
                        new_data=app_data,
                        old_data=old_app_data,
                        discord_role=main_app.discord_role,
                        app_id=main_app.id,
                        app_icon=self.get_game_metadata(int(app), "icon"),
                    )
                    updates[app] = update.create_output()

        updates = {k: v for k, v in updates.items() if v}  # remove empty app entries

        for app in updates:
            if app_update_found:
                break
            else:
                app_update_found = True if len(updates[app]) > 0 else False

        if app_update_found:
            update_string = "Update detected for:"
            for app_id in self.get_updated_ids(updates):
                update_string += f" {app_id},"
            update_string = update_string[:-1]
            logger.debug(f"Update String: {update_string}")
            logger.debug(f"Update Package: {updates}")
            return updates
        else:
            logger.info("No updates found")
            return False

    def get_updated_ids(self, updates):
        updated_apps = []
        for app in updates:
            app_id = int(app)
            updated_apps.append(app_id)
        return updated_apps

    def get_game_metadata(self, app_id: int, key: str = "icon"):
        match key:
            case "icon":
                icon = self.app_info["apps"][str(app_id)]["common"]["icon"]
                icon_url = f"https://cdn.cloudflare.steamstatic.com/steamcommunity/public/images/apps/{app_id}/{icon}.jpg"
                return icon_url


if __name__ == "__main__":
    a = Update(app_id=1599340)
    print(a.get_game_news())
