from steam.client import SteamClient
from steam.enums import EResult

import json
import logging

from modules import get_timestamp, get_time_delta, Cache


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
            print(dictionary)
            self.data_type = dictionary["data_type"]
            self.name = dictionary["name"]
            self.branch = dictionary["branch"]
            self.path = dictionary["path"]
            # self.path.append(self.branch)

    def get_path(self):
        return self.path

    def navigate_to_path(self, data):
        pass


class Update:
    def __init__(
        self,
        watchlist: Watchlist,
        new_data: dict = None,
        old_data: dict = None,
        discord_role: str = None,
    ):
        self.watchlist = watchlist
        self.new_data = new_data
        self.old_data = old_data
        self.discord_role = discord_role

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
        return added, removed, altered, self.discord_role

    def create_output(self):
        added, removed, altered, discord_role = self.parse_data()
        output = {
            "watchlist": self.watchlist,
            "added": added,
            "removed": removed,
            "altered": altered,
            "role": discord_role,
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

    def add_to_watchlist(self, watchlist: Watchlist):
        if watchlist not in self.watchlist:
            self.watchlist.append(watchlist)

    def remove_from_watchlist(self, watchlist_name: str):
        for item in self.watchlist:
            if item.name == watchlist_name:
                self.watchlist.remove(item)


class SteamUpdates:
    def __init__(self, logger):
        self.logger = logger
        self.client = SteamClient()
        self.apps = []
        self.cache = Cache()
        self.update_freq = 0  # how often to check for updates in minutes

        self.login()
        if self.load_config():
            self.logger.info("Loaded config from cache")
        else:
            self.logger.info("No config found in cache")

    def login(self):
        login = self.client.anonymous_login()
        if login == EResult.OK:
            return True
        else:
            return False

    def add_app(self, *args: SteamApp):
        for app in args:
            if app in self.apps:
                self.logger.info(f"{app.name} is already in the list")
                continue
            self.apps.append(app)
        self.save_config()
        return self.apps

    def remove_app(self, *args: int):
        for app in args:
            for app in self.apps:
                if app.id == app:
                    self.apps.pop(app)

    def get_app(self, app_id: int = None, app_name: str = None):
        for app in self.apps:
            if app.id == app_id or app.name == app_name:
                return app
        return None

    def add_to_watchlist(
        self, watchlist: Watchlist, app_id: int = None, app_name: str = None
    ):
        app = self.get_app(app_id, app_name)
        if app is None:
            self.logger.error("App not found")
            return False
        else:
            app.add_to_watchlist(watchlist)
            self.save_config()
            return True

    def remove_from_watchlist(
        self,
        *args: str,
        app_id: int = None,
        app_name: str = None,
    ):
        app = self.get_app(app_id, app_name)
        if app is None:
            self.logger.error("App not found")
            return False
        else:
            app.remove_from_watchlist(args)
            self.save_config()
            return True

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
        self.logger.info("Updating Steam app info...")

        self.old_data = self.cache.read_from_cache("steam", "app_info.json")
        if (
            get_time_delta(self.old_data["last_updated"], get_timestamp())
            < self.update_freq
        ):
            self.logger.info("App info is up to date")
            self.app_info = self.old_data
        else:
            self.app_info = self.client.get_product_info(
                apps=[int(app.id) for app in self.apps],
            )
            self.cache.write_to_cache(self.app_info, "steam", "app_info.json")
            self.app_info = self.cache.read_from_cache("steam", "app_info.json")

        return self.check_for_updates()

    def check_for_updates(self):
        self.logger.info("Checking for updates...")
        checklist = {str(app.id): app.watchlist for app in self.apps}
        updates = {str(app.id): "" for app in self.apps}
        app_update_found = False
        for app in checklist:  # check updates on every app
            main_app = self.get_app(app_id=int(app))
            app_data = self.app_info["apps"][app]  # get app data for specific app
            old_app_data = self.old_data["apps"][app]  # same here but with the old data
            for watchlist in checklist[app]:  # check data for each watchlist
                for key in watchlist.get_path():  # check each path in the watchlist
                    app_data = app_data[key]
                    old_app_data = old_app_data[key]
                if app_data != old_app_data:
                    update = Update(
                        watchlist, app_data, old_app_data, main_app.discord_role
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
            self.logger.info(update_string)
            self.logger.info(updates)
            return updates
        else:
            self.logger.info("No updates found")
            return False

    def get_updated_ids(self, updates):
        updated_apps = []
        for app in updates:
            app_id = int(app)
            updated_apps.append(app_id)
        return updated_apps

    def get_game_metadata(self, app_id: int):
        icon = self.app_info["apps"][str(app_id)]["common"]["clienticon"]
        icon_url = f"https://cdn.cloudflare.steamstatic.com/steamcommunity/public/images/apps/{app_id}/{icon}.jpg"
        return icon_url


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    base_logger = logging.getLogger(__name__)
    a = SteamUpdates(base_logger)
    print(a.get_app_info())
