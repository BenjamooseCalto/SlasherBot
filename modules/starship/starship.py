import requests
import json
import os

URL = "https://starshipstatus.space/api/data"  # api by @NoahPrail on Twitter
DIR = os.path.dirname(__file__)
DATA_FILE = os.path.join(DIR, "starship.json")


class StarshipStatus:
    def __init__(
        self, update=False
    ):  # r = api response, either updated on object creation or taken from the data file
        if update == True:
            self.update()
        else:
            with open(DATA_FILE, "r") as file:
                self.r = json.load(file)
        self.build_index()

    def update(self):
        self.r = requests.get(URL)
        self.r = self.r.json()
        with open(DATA_FILE, "w") as file:
            json.dump(self.r, file, indent=4)
        self.build_index()  # have to call this again (for now) because update() can be called manually, and it wouldn't update the information otherwise

    def build_index(self):
        self.weather = Weather(self.r["weather"])
        self.update_date = self.r["lastUpdatedDate"]
        self.location = Location(self.r["tfrs"][0])
        self.tfrs = []
        self.closures = []
        for tfr in self.r["tfrs"]:
            self.tfrs.append(FlightRestriction(tfr))
        for closure in self.r["closures"]:
            self.closures.append(RoadClosure(closure))
        self.num_tfrs = 0
        self.num_closures = 0
        for tfr in self.tfrs:
            if tfr.status == True:
                self.num_tfrs += 1
        for closure in self.closures:
            if closure.status == True:
                self.num_closures += 1

    def show(self):
        string = f"""\
Number of TFR\'s active: {self.num_tfrs}
Number of Active Road Closures: {self.num_closures}
Current Weather in {self.location}: {self.weather}
Last Updated: {self.update_date}"""
        for closure in self.closures:
            if closure.active:
                string += "\n" + closure
        if __name__ == "__main__":
            print(string)
        else:
            return string


class Location:
    def __init__(self, tfr):
        self.location = tfr["details"]["location"]
        self.state = self.location["state"]
        self.city = self.location["city"]

    def __str__(self):
        return f'{self.location["city"]}, {self.location["state"]}'


class FlightRestriction:
    def __init__(self, tfr):
        self.tfr = tfr
        self.airspace = {
            "upper": self.tfr["details"]["airspace"]["upper"],
            "lower": self.tfr["details"]["airspace"]["lower"],
        }
        self.status = tfr["isActive"]

    def __str__(self):
        return f'TFR upper: {self.airspace["upper"]["value"]}{self.airspace["upper"]["unit"]} TFR lower: {self.airspace["lower"]["value"]}{self.airspace["lower"]["unit"]}\nReason for TFR: Space Operations Area'


class Weather:
    def __init__(self, weather):
        self.main = weather
        self.details = weather["weather"]
        self.description = self.details[0]["description"]
        self.temperature = self.main["main"]
        self.visibility = self.main["visibility"]
        self.wind = self.main["wind"]
        self.degree_sign = "\N{DEGREE SIGN}"

    def __str__(self):
        output = ""
        output += self.format("temp")
        output += " | "
        output += self.format("wind")
        return output

    def format(self, type):
        if type == "wind":
            try:
                if self.wind["speed"] < 3:
                    return f'VRB@{int(self.wind["speed"])}kts'
                if self.wind["gust"] - self.wind["speed"] > 7:
                    return f'{(self.wind["deg"])}@{int(self.wind["speed"])}G{int(self.wind["gust"])}kts'
                else:
                    return f'{int(self.wind["deg"])}@{int(self.wind["speed"])}kts'
            except KeyError:
                return f"Wind Unavailable"
        if type == "temp":
            if abs(self.temperature["feels_like"] - self.temperature["temp"]) > 5:
                return f'{self.temperature["temp"]}{self.degree_sign}c, feels like {self.temperature["feels_like"]}{self.degree_sign}c with {self.temperature["humidity"]}% Humidity'
            else:
                return f'{self.temperature["temp"]}{self.degree_sign}c with {self.temperature["humidity"]}% Humidity'


class RoadClosure:
    def __init__(self, closure):
        self.info = closure
        self.status = "ACTIVE" if self.get_status() == True else "Inactive"
        self.active = self.info["isActive"]

    def __str__(self):
        return f"""\
            Closure Date: {self.info['originalDate']}
            Closure Time: {self.info['originalTime']}
            Closure Status: {self.info['status']}
            """

    def get_status(self):
        if self.info["isActive"] == True:
            return True
        else:
            return False


class StarshipRequest:  # this will handle requests made for specific information, probably will add more info about Starship in general, without using the API from above
    # valid requests will be like weather, then specific weather details like temp, humidity, etc. then similar setup for other types like TFRs, closures, etc.
    def __init__(self, request=False):
        self.request = request


def main():
    data = StarshipStatus(update=False)
    data.show()


if __name__ == "__main__":
    main()
