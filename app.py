from random import randint, choice
import time
import asyncio
import curses

from garbage import get_trash_coroutines, fill_orbit_with_garbage, get_trash_frames, fly_garbage
from stars import get_stars_coroutines
from rocket import draw_rocket, fire





def draw(canvas):
    routines = []
    frames = get_trash_frames()
    canvas.nodelay(True)
    height, width = canvas.getmaxyx()
    border = {"top": 0, "bottom": height, "left": 0, "right": width}
    stars_coroutines = get_stars_coroutines(canvas, width, height)
    rocket_coroutine = draw_rocket(
        canvas, height / 2, width / 2, border, speed_boost=1
    )
    trash_cors = get_trash_coroutines(canvas, width, height, 6)
    fire_coroutine = fire(canvas, height - 1, width / 2)
    #filler = fill_orbit_with_garbage(routines, canvas, width)
    routines = [
        *stars_coroutines,
        rocket_coroutine,
        fire_coroutine,
        *trash_cors,
        
    ]
    while True:
        for coroutine in routines.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                routines.remove(coroutine)
                column = randint(1, width)
                frame = choice(frames)
                routines.append(fly_garbage(canvas, column, frame))
        canvas.refresh()
        time.sleep(0.05)


if __name__ == "__main__":
    curses.update_lines_cols()
    curses.initscr()
    curses.curs_set(False)
    curses.wrapper(draw)
