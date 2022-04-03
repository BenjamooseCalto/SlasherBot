import logging
import asyncio
import discord.ui as ui

from modules import Cache
from discord import ButtonStyle, SelectOption, Interaction

logger = logging.getLogger("discord.slasher_ui")


class GUpdateSubscribe(ui.View):
    """Game Update Subscription UI Class"""

    CONFIG_MODULE = "meta"
    CONFIG_PATH = "gupdate_user_config.json"

    def __init__(self, ctx=None, utility=False):
        super().__init__()
        self.cache = Cache()
        self.supported_games = self.get_supported_games()
        self.ctx = ctx
        self.utility = utility

        if self.utility != True:
            self.build_config()
            self.create_select_menu()
            self.create_unsub_button()

    def get_supported_games(self):
        data = self.cache.read_from_cache("steam", "update_config.json")
        data = data["apps"]

        supported_games = [[game["name"], str(game["id"])] for game in data]

        return supported_games

    def build_config(self):
        logger.debug("Building GUpdateSubscribe config")
        data = self.cache.read_from_cache(self.CONFIG_MODULE, self.CONFIG_PATH)
        for game in self.supported_games:
            if game[1] not in data.keys():
                data[game[1]] = {}
                data[game[1]]["game_name"] = game[0]
                data[game[1]]["subscribers"] = []

        self.cache.write_to_cache(data, self.CONFIG_MODULE, self.CONFIG_PATH)

    def create_select_menu(self):
        placeholder = "Select a game..."
        min_values = 0
        max_values = len(self.supported_games)
        options = []
        disabled = False
        user = str(self.ctx.author.id)

        cache_data = self.cache.read_from_cache(self.CONFIG_MODULE, self.CONFIG_PATH)

        subscribed_games = []
        for game in cache_data:
            if game == "last_updated":
                continue
            if user in cache_data[game]["subscribers"]:
                subscribed_games.append(game)
                print(subscribed_games)

        for game in self.supported_games:
            if game[1] in subscribed_games:
                subscribed = True
            else:
                subscribed = False
            option = SelectOption(label=game[0], value=game[1], default=subscribed)
            options.append(option)

        game_select_menu = ui.Select(
            placeholder=placeholder,
            min_values=min_values,
            max_values=max_values,
            options=options,
            disabled=disabled,
        )
        self.game_menu = game_select_menu

        async def update_user_games(interaction: Interaction):
            selected_games = game_select_menu.values
            user_id = str(interaction.user.id)

            current_cache_data = self.cache.read_from_cache(
                self.CONFIG_MODULE, self.CONFIG_PATH
            )

            for game in self.supported_games:
                if game[1] in selected_games:
                    if user_id not in current_cache_data[game[1]]["subscribers"]:
                        current_cache_data[game[1]]["subscribers"].append(user_id)
                else:
                    if user_id in current_cache_data[game[1]]["subscribers"]:
                        current_cache_data[game[1]]["subscribers"].remove(user_id)

            self.cache.write_to_cache(
                current_cache_data, self.CONFIG_MODULE, self.CONFIG_PATH
            )

            return True

        game_select_menu.callback = update_user_games
        self.add_item(game_select_menu)

    def create_unsub_button(self):
        style = ButtonStyle.primary
        disabled = False
        label = "Unsubscribe from all"

        button = ui.Button(style=style, label=label, disabled=disabled)

        async def unsubscribe_from_all(interaction: Interaction):
            user_id = str(interaction.user.id)
            current_cache_data = self.cache.read_from_cache(
                self.CONFIG_MODULE, self.CONFIG_PATH
            )

            for game in current_cache_data:
                if game == "last_updated":
                    continue
                if user_id in current_cache_data[game]["subscribers"]:
                    current_cache_data[game]["subscribers"].remove(user_id)

            self.cache.write_to_cache(
                current_cache_data, self.CONFIG_MODULE, self.CONFIG_PATH
            )

            return True

        button.callback = unsubscribe_from_all
        self.add_item(button)

    def get_subscribers(self, game_id):
        data = self.cache.read_from_cache(self.CONFIG_MODULE, self.CONFIG_PATH)
        return data[game_id]["subscribers"]


if __name__ == "__main__":
    test_ui = GUpdateSubscribe()
