import os
import json
import logging
import modules

from datetime import datetime

logger = logging.getLogger("discord.slasher_utils")


def create_directory(path: str):
    if not os.path.exists(path):
        os.makedirs(path)
    else:
        return False


def get_self_path():
    return os.path.dirname(os.path.realpath(__file__))


def log_start():
    log_separator()
    logger.info(f"{get_date()} - Starting SlasherBot...")
    log_separator()


def log_separator():
    logger.info("-----------------------------------------------------")


def get_timestamp(day_only=False):
    if day_only:
        return datetime.now().strftime("%Y-%m-%d")
    else:
        return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def get_date():
    return datetime.now().strftime("%m-%d-%Y @ %H:%M")


def get_time_delta(start_time: str, end_time: str):
    """Returns the difference between two times in minutes"""
    t1 = datetime.strptime(start_time, "%Y-%m-%d_%H-%M-%S")
    t2 = datetime.strptime(end_time, "%Y-%m-%d_%H-%M-%S")

    delta = t2 - t1

    return int(delta.seconds / 60)


class DictToClass:
    def __init__(self, d, target: object):
        self.d = d
        self.target = target

    def convert(self):
        if isinstance(self.d, dict):
            item = self.target()
            for key in self.d:
                setattr(item, key, self.d[key])
            return item
        elif isinstance(self.d, list):
            objects = []
            for config in self.d:
                item = self.target()
                for key in config:
                    setattr(item, key, config[key])
                objects.append(item)
            return objects


class Cache:
    """Class to easily access the cache directory"""

    CACHE_DIR = os.path.join(os.path.dirname(__file__), "cache")

    def write_to_cache(
        self, data: dict, module: str, file: str, encoder=json.JSONEncoder
    ):
        try:
            self.validate_module(module)
        except ValueError as e:
            logger.error(e)
            return False

        logger.info(f"Writing to cache: {module}/{file}")

        cache_file = os.path.join(self.CACHE_DIR, module, file)
        create_directory(os.path.dirname(cache_file))

        data["last_updated"] = get_timestamp()

        with open(cache_file, "w") as file:
            json.dump(data, file, indent=4, cls=encoder)

    def read_from_cache(self, module: str, file: str):
        logger.debug(f"CURRENT DIR: {os.getcwd()}")
        try:
            self.validate_module(module)
        except ValueError as e:
            logger.error(e)
            return False

        cache_file = os.path.join(self.CACHE_DIR, module, file)
        if os.path.exists(cache_file):
            with open(cache_file, "r") as file:
                data = json.load(file)
                logger.debug(f"CACHE_DATA: {data}")
                return data
        else:
            return None

    def validate_module(self, *args: str):
        invalid_modules = []
        for module in args:
            if module not in modules.all_modules:
                invalid_modules.append(module)
        if len(invalid_modules) > 0:
            raise ValueError(f"Invalid module(s): {invalid_modules}")
        else:
            return True


if __name__ == "__main__":
    time = "2022-02-20_21-19-30"
    print(get_time_delta(time, get_timestamp()))
