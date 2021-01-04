import time
import curses

from utils import sleep
from garbage import fill_orbit_with_garbage
from stars import get_stars_coroutines
from rocket import draw_rocket


async def update_info_line(state, canvas):
    """ Updating year and level info on the screen """

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

        canvas.addstr(
            0, 0, f"year is {state['year']}, level is {state['level']}",
        )
        canvas.refresh()
        await sleep(100)
        state["year"] += 1


def draw(window):
    state = {
        "year": 1957,
        "obstacles": [],
        "routines": [],
        "collisions": [],
        "level": 1,
    }

    window_height, window_width = window.getmaxyx()
    info_line = window.subwin(1, window_width, 0, 0)
    game_window = window.derwin(window_height - 1, window_width, 1, 0)
    game_window.nodelay(True)
    game_height = window_height - 1
    game_width = window_width
    border = {"top": 0, "bottom": game_height, "left": 0, "right": game_width}

    stars_coroutines = get_stars_coroutines(
        game_window, game_width, game_height,
    )
    rocket_coroutine = draw_rocket(
        state, game_window, game_height // 2, game_width // 2, border,
    )
    garbage_creator = fill_orbit_with_garbage(state, game_window, game_width)
    info_coroutine = update_info_line(state, info_line)

    state["routines"].extend(
        [garbage_creator, rocket_coroutine, *stars_coroutines, info_coroutine],
    )

    while True:
        for coroutine in state["routines"].copy():
            try:
                coroutine.send(None)
            except StopIteration:
                state["routines"].remove(coroutine)
        game_window.refresh()
        time.sleep(0.05)


if __name__ == "__main__":
    curses.update_lines_cols()
    curses.initscr()
    curses.curs_set(False)
    curses.wrapper(draw)
