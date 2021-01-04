import time
import curses
from utils import sleep
from obstacles import show_obstacles
from garbage import (
    fill_orbit_with_garbage,
)
from stars import get_stars_coroutines
from rocket import draw_rocket


async def print_years(state, canvas):
    counter = 0
    while True:
        if state["year"] == 1960:
            state["level"] = 2
        elif state["year"] == 1965:
            state["level"] = 3
        elif state["year"] == 1970:
            state["level"] = 3
        elif state["year"] == 1975:
            state["level"] = 4
        elif state["year"] == 1980:
            state["level"] = 5
        elif state["year"] == 1985:
            state["level"] = 6
        elif state["year"] == 1990:
            state["level"] = 7
        elif state["year"] == 1995:
            state["level"] = 8
        elif state["year"] == 2000:
            state["level"] = 9
        elif state["year"] == 2010:
            state["level"] = 10
        elif state["year"] == 2015:
            state["level"] = 11
        elif state["year"] == 2020:
            state["level"] = 12

        canvas.addstr(0, 0, f"year is {state['year']}, level is {state['level']}")
        canvas.refresh()
        counter += 1
        await sleep(1)
        if counter == 100:
            state["year"] += 1
            counter = 0


def draw(wind):
    state = {
        "year": 1957,
        "obstacles": [],
        "routines": [],
        "collisions": [],
        "level": 1,
    }    
    main_height, width = wind.getmaxyx()
    info_line = wind.subwin(1, width,0,0)    
    canvas = wind.derwin(main_height-1,width, 1,0)
    canvas.nodelay(True)
    height = main_height - 1
    border = {"top": 0, "bottom": height, "left": 0, "right": width}

    stars_coroutines = get_stars_coroutines(canvas, width, height)
    rocket_coroutine = draw_rocket(
        state, canvas, height // 2, width // 2, border, speed_boost=1
    )
    filler = fill_orbit_with_garbage(state, canvas, width)
    ob_cors = show_obstacles(canvas, state)

    state["routines"].extend(
        [
            filler,
            rocket_coroutine,
            *stars_coroutines,
            # ob_cors
            print_years(state, info_line),
        ]
    )
    while True:        
        for coroutine in state["routines"].copy():
            try:
                coroutine.send(None)
            except StopIteration:
                state["routines"].remove(coroutine)
        canvas.refresh()
        time.sleep(0.05)


if __name__ == "__main__":
    curses.update_lines_cols()
    curses.initscr()
    curses.curs_set(False)
    curses.wrapper(draw)
