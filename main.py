"""
This is a module that contains functions to create a html-file
which contains a map around user with some marks of places, in
which were filmed some films.
"""
import blessed
import pandas as pd
import folium
import geopy
import math
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
geolocator = Nominatim(user_agent="main.py")

def start_program(start: bool) -> list:
    """
    """
    term = blessed.Terminal()
    if start:
        print(term.clear)
    print(term.move_y(term.height // 3))
    year_date = input(f"{term.purple}Please enter a 1970 < year < 2022 you w\
ould like to have a map for:{term.normal} ")
    coordinates = input(f"{term.purple}Please enter your locati\
on (format: lat, long):{term.normal} ")
    try:
        year_date = int(year_date)
        coordinates = coordinates.replace(" ", "").split(",")
        if year_date < 1900 or year_date > 2021:
            start = False
            print(term.clear)
            print(term.move_y(term.height // 3) + term.center(f"{term.red}Typ\
    e data in correct format!{term.normal}"))
            print()
            print(start_program(start))
    except:
        start = False
        print(term.clear)
        print(term.move_y(term.height // 3) + term.center(f"{term.red}Typ\
e data in correct format!{term.normal}"))
        print()
        print(start_program(start))
    print(term.clear)
    print(term.move_y(term.height // 3) + term.center(f"{term.yellow}Map i\
s generating..."))
    print(term.center(f"Please wait...{term.normal}"))
    return [year_date, coordinates]

def file_reader_transform(year_date: str) -> None:
    """
    """
    with open("norm_location.txt", "r", encoding="utf-8") as file:
        text = file.read()
        text = text.split("\n")[:-1]
    i = 0
    counter = 0
    while i < len(text):
        text[i] = text[i].split("\t")
        first = text[i][0].split(" ")
        for j in range(len(first)):
            try:
                if first[j][0] == "(":
                    year = first[j]
                    name = " ".join(first[:j])
            except IndexError:
                continue
        if text[i][-1][-1] == ")":
            place = text[i][-2].split(",")[0]
        else:
            place = text[i][-1].split(",")[0]
        geocode = RateLimiter(geolocator.geocode, min_delay_seconds=5)
        location = geocode(f"{place}")
        try:
            text[i] = [name, year, place, (location.latitude, location.longitude)]
        except:
            counter +=1
            print("GG = ", counter)
            print(i)
        i +=1
    df = pd.DataFrame(text)
    df.to_csv("location.csv")
    return



def finder(year_date: str, coordinates: tuple, path: str) -> pd.DataFrame:
    """
    """
    df = pd.read_csv(path)
    df = df[df['1'].isin([f"({year_date})"])]
    places = df['0'].tolist()
    all_coord = df['3'].tolist()
    dist = []
    output = []
    for i in range(len(all_coord)):
        all_coord[i] = list(all_coord[i][1:-1].split(","))
        all_coord[i][0] = float(all_coord[i][0])
        all_coord[i][1] = float(all_coord[i][1])
        all_coord[i] = tuple(all_coord[i])
        dist.append([distance_calc(all_coord[i], coordinates), i])
        dist = sorted(dist)
    for i in range(10):
        try:
            output.append((all_coord[dist[i][1]], places[dist[i][1]]))
        except IndexError:
            break
    return output

def distance_calc(obj: tuple, start: tuple) -> int:
    """
    """
    haversin = (math.sin((start[0]-obj[0])/2)**2 + math.cos(obj[0])*
    math.cos(start[0]) * math.sin((start[1]-obj[1])/2)**2)
    distance = 6371.3 * 2 * math.asin(haversin ** 0.5)
    return distance

def map_builder(output: list, coordinates: tuple) -> str:
    """
    """
    map_0 = folium.Map(location=coordinates)
    map_1 = folium.FeatureGroup(name="Population")
    map_1.add_child((folium.GeoJson(data=open('world.json', 'r',
    encoding='utf-8-sig').read(),
    style_function=lambda x: {'fillColor':'green'
    if x['properties']['POP2005'] < 10000000
    else 'orange' if 10000000 <= x['properties']['POP2005'] < 200000000
    else 'red'})))
    map_2 = folium.FeatureGroup(name="Points")
    for i in range(len(output)):
        map_2.add_child((folium.Marker(location=list(output[i][0]),
 popup=output[i][1],
 icon=folium.Icon())))
    map_0.add_child(map_2)
    map_0.add_child(map_1)
    map_0.add_child(folium.LayerControl())
    map_0.save("world_map.html")
    return output

if __name__ == "__main__":
    input_data = start_program(start=True)
    file_reader_transform(input_data[0])
    for i in range(len(input_data[1])):
        input_data[1][i] = float(input_data[1][i])
    print(map_builder(finder(input_data[0], input_data[1], "location.csv"), input_data[1]))
