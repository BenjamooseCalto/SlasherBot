import requests
import json
import os

from dotenv import load_dotenv
from datetime import date

load_dotenv()
NASA_API_KEY = os.getenv("NASA_API_KEY")
DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(DIR, "data")
TODAY = date.today()

# astronomy picture of the day
class Apod:
    def __init__(self):
        self.url = "https://api.nasa.gov/planetary/apod"
        self.data_file = os.path.join(DATA_DIR, "apod.json")

    def __req(self):
        apod = requests.get(f"{self.url}?api_key={NASA_API_KEY}")
        apod = apod.json()
        with open(self.data_file, "w") as file:
            json.dump(apod, file, indent=4)
        self.__index(apod)

    def __index(self, apod):
        self.copyright = apod["copyright"]
        self.date = apod["date"]
        self.explanation = apod["explanation"]
        self.hdurl = apod["hdurl"]
        self.media_type = apod["media_type"]
        self.service_version = apod["service_version"]
        self.title = apod["title"]
        self.url = apod["url"]

    def get_apod(self):
        with open(self.data_file, "r") as file:
            data = json.load(file)
            if data["date"] != TODAY:
                self.__req()
                return "retrieved new data"
            else:
                self.__index(data)
                return "used existing data"


def main():
    pass


if __name__ == "__main__":
    pass
