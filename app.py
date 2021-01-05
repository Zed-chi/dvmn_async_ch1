import time
import curses

from utils import sleep
from garbage import fill_orbit_with_garbage
from stars import get_stars_coroutines
from rocket import draw_rocket


async def update_year(state, time_to_sleep=100):
    while True:
        state["year"] += 1
        await sleep(time_to_sleep)


async def update_level(state, time_to_sleep=50):
    while True:
        if state["year"] == 1961:
            state["level"] = 2
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
        elif state["year"] >= 2020:
            state["level"] = 12

        await sleep(time_to_sleep)


async def update_info_line(state, canvas, time_to_sleep=20):
    """ Updating year and level info on the screen """
    phrases = {
        1957: "First Sputnik",
        1961: "Gagarin flew!",
        1969: "Armstrong got on the moon!",
        1971: "First orbital space station Salute-1",
        1981: "Flight of the Shuttle Columbia",
        1998: "ISS start building",
        2011: "Messenger launch to Mercury",
        2020: "Take the plasma gun! Shoot the garbage!",
    }
    while True:
        if state["year"] in phrases:
            canvas.clear()
            info = f"[{phrases[state['year']]} in {state['year']}]"
        else:
            info = ""

        canvas.addstr(
            0,
            0,
            f"year is {state['year']}, level is {state['level']} {info}",
        )

        canvas.refresh()
        await sleep(time_to_sleep)


def draw(window):
    state = {
        "year": 1957,
        "obstacles": [],
        "routines": [],
        "collisions": [],
        "level": 1,
    }

    window_height, window_width = window.getmaxyx()
    info_line = window.subwin(1, window_width, window_height - 1, 0)
    game_window = window.derwin(window_height - 1, window_width, 0, 0)
    game_window.nodelay(True)
    game_height = window_height - 1
    game_width = window_width
    border = {"top": 0, "bottom": game_height, "left": 0, "right": game_width}

    stars_coroutines = get_stars_coroutines(
        game_window,
        game_width,
        game_height,
    )
    rocket_coroutine = draw_rocket(
        state,
        game_window,
        game_height // 2,
        game_width // 2,
        border,
    )
    garbage_creator = fill_orbit_with_garbage(state, game_window, game_width)
    info_coroutine = update_info_line(state, info_line)

    state["routines"].extend(
        [
            garbage_creator,
            rocket_coroutine,
            *stars_coroutines,
            info_coroutine,
            update_year(state),
            update_level(state),
        ],
    )

    while True:
        for coroutine in state["routines"].copy():
            try:
                coroutine.send(None)
            except StopIteration:
                state["routines"].remove(coroutine)
        game_window.refresh()
        time.sleep(0.03)


if __name__ == "__main__":
    curses.update_lines_cols()
    curses.initscr()
    curses.curs_set(False)
    curses.wrapper(draw)
