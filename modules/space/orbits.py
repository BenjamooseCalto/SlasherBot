# this will give you orbital information about planets and moons and stuff, it'll be cool
import requests
import json
import os

URL = "https://api.le-systeme-solaire.net/rest/bodies/"
DIR = os.path.dirname(__file__)
DATA_FILE = os.path.join(DIR, "orbits.json")


class OrbitInformation:
    def __init__(self, req=None):
        if req:
            req = req.lower()
            self.request(req)
        else:
            pass

    def request(self, req):
        self.r = requests.get(f"{URL}{req}")
        self.r = self.r.json()
        with open(DATA_FILE, "w", encoding="utf-8") as file:
            json.dump(self.r, file, indent=4)
        self.__build_index()

    def __build_index(self):
        self.name = self.r["englishName"]
        self.isPlanet = self.r["isPlanet"]
        self.moons = self.r["moons"]
        self.semiMajorAxis = self.r["semimajorAxis"]
        self.perihelion = self.r["perihelion"]
        self.aphelion = self.r["aphelion"]
        self.eccentricity = self.r["eccentricity"]
        self.inclination = self.r["inclination"]
        self.mass = self.r["mass"]
        self.volume = self.r["vol"]
        self.density = self.r["density"]
        self.gravity = self.r["gravity"]
        self.escape = self.r["escape"]
        self.meanRadius = self.r["meanRadius"]
        self.equaRadius = self.r["equaRadius"]
        self.polarRadius = self.r["polarRadius"]
        self.flattening = self.r["flattening"]
        self.dimension = self.r["dimension"]
        self.sideralOrbit = self.r["sideralOrbit"]
        self.sideralRotation = self.r["sideralRotation"]
        self.aroundPlanet = self.r["aroundPlanet"]
        self.discoveredBy = self.r["discoveredBy"]
        self.discoveryDate = self.r["discoveryDate"]
        self.alternativeName = self.r["alternativeName"]
        self.axialTilt = self.r["axialTilt"]
        self.avgTemp = self.r["avgTemp"]
        self.mainAnomaly = self.r["mainAnomaly"]
        self.argPeriapsis = self.r["argPeriapsis"]
        self.longAscNode = self.r["longAscNode"]
        self.__formatting()

    def __formatting(self):
        if self.isPlanet == True:
            moons2 = ""
            self.num_moons = len(self.moons)
            for moon in self.moons:
                moons2 += f"{moon['moon']}, "
            self.moons = moons2
            self.moons = self.moons[:-2]

        self.mass = f"{self.mass['massValue']}e^{self.mass['massExponent']}kg"
        self.volume = f"{self.volume['volValue']}e^{self.volume['volExponent']}km\N{SUPERSCRIPT THREE}"


if __name__ == "__main__":
    data = OrbitInformation("mars")
    print(data.mass)
