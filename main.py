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
from geopy.exc import GeocoderUnavailable

def start_program(start: bool) -> list:
    """
    This function starts the program. It prints welcome message
    and some other stuff. Returns a list containing the year and
    coordinates of start point.
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
    This function transforms database in txt format to
    pandas DataFrame and then writes it to .csv file. Prints
    final message and returns None.
    """
    with open("new_locations.txt", "r", encoding="utf-8") as file:
        text = file.read()
        text = text.split("\n")[:-1]
    i = 0
    while i < len(text):
        if i > 10000:
            break
        if "{" in text[i]:
            text[i] = text[i].replace('{', "\t")
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
            place = text[i][-2]
        else:
            place = text[i][-1]
        text[i] = (name, year, place)
        i+=1
    text = text[:i-1]
    text = list(set(text))
    for i in range(len(text)):
        text[i] = list(text[i])
        lst = text[i][2].split(",")
        text[i][2] = lst[0]
        try:
            text[i].append(lst[1])
        except IndexError:
            continue
    df = pd.DataFrame(text)
    df = df[df[1].isin([f"({int(year_date)})"])]
    i = 0
    lst = []
    while i < len(df):
        try:
            from geopy.extra.rate_limiter import RateLimiter
            geolocator = Nominatim(user_agent="main.py")
            geocode = RateLimiter(geolocator.geocode, min_delay_seconds=0.5)
            location = geocode(f"{df.iloc[i, 2]}")
            if location == None:
                location = geocode(f"{df.iloc[i, 3]}")
            if location == None:
                lst.append("gg")
            else:
                lst.append((location.latitude, location.longitude))
        except GeocoderUnavailable:
            lst.append("gg")
        i +=1
    df[4] = lst
    df = df[df[4] != "gg"]
    df.to_csv("locations.csv")
    return

def finder(coordinates: tuple, path: str) -> pd.DataFrame:
    """
    This function finds 10 the nearest points, where was filmed
    a film or series. Returns DataFrame.
    >>> finder((34.24323, 53.23444), "locations.csv")
    [((42.6502473, 18.0924947), '"4-Stjerners Reise"'), ((47.4983\
815, 19.0404707), '"A Stáb a Balatonon"'), ((47.4983815, 19.04047\
07), '"2030 - Ki öregszik hamarabb"'), ((46.9071694, 18.0541598\
), '"A Stáb a Balatonon"'), ((46.9567254, 17.888892), '"A Stáb a B\
alatonon"'), ((42.6384261, 12.674297), '"A Traveler\\'s Guide to th\
e Planets"'), ((52.5170365, 13.3888599), '"45 Min"'), ((43.458654\
1, 11.1389204), '"4-Stjerners Reise"'), ((52.0089065, 11.7003344)\
, '"45 Min"'), ((48.332833050000005, 10.039082513905473), '"A Trav\
eler\\'s Guide to the Planets"')]
    """
    df = pd.read_csv(path)
    places = df['0'].tolist()
    all_coord = df['4'].tolist()
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
    This function calculates distance between two
    dots on the sphere. Returns distance in int format.
    >>> distance_calc((12.123544, 43.2134), (23.123554, 32.2354423))
    1686.4305373326386
    """
    haversin = (math.sin((math.pi/180)*(start[0]-obj[0])/2)**2 +
    math.cos((math.pi/180)*obj[0])* math.cos((math.pi/180)*start[0])
    * math.sin((math.pi/180)*(start[1]-obj[1])/2)**2)
    distance = 6371.3 * 2 * math.asin(haversin ** 0.5)
    return distance

def map_builder(output: list, coordinates: tuple) -> None:
    """
    This function creates a map with 10 or less points.
    Returns None.
    """
    term = blessed.Terminal()
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
    print(term.clear)
    print(term.move_y(term.height // 3) + term.center(f"{term.green}Finis\
hed. Please have look at the map world_map.html{term.normal}"))
    return 

if __name__ == "__main__":
    in_d = start_program(start=True)
    file_reader_transform(in_d[0])
    for i in range(len(in_d[1])):
        in_d[1][i] = float(in_d[1][i])
    map_builder(finder(in_d[1], "locations.csv"), in_d[1])
    