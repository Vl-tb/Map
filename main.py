"""
This is a module that contains functions to create a html-file
which contains a map around user with some marks of places, in
which were filmed some films.
"""
import blessed
import pandas as pd
def start_program(start: bool) -> str:
    """
    """
    term = blessed.Terminal()
    if start:
        print(term.clear)
    print(term.move_y(term.height // 3))
    year_date = input(f"{term.purple}Please enter a year you w\
ould like to have a map for:{term.normal} ")
    coordinates = input(f"{term.purple}Please enter your locati\
on (format: lat, long):{term.normal} ")
    try:
        year_date = int(year_date)
        coordinates = coordinates.replace(" ", "").split(",")
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
    return year_date

def file_reader() -> str:
    """
    """
    with open("locations.list", "r", encoding="iso-8859-1") as file:
        text = file.read()
        text = text.split("\n")
    # with open("new_locations.txt", "w", encoding="utf-8") as new:
    #     new.write(text)
    # df = pd.read_csv("new_locations.txt", encoding="utf-8", error_bad_lines=False)

    return text[15:20]

if __name__ == "__main__":
    print(start_program(start=True))
    print(file_reader())

