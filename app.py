from random import randint, choice
import time
import asyncio
import curses
from obstacles import show_obstacles

from garbage import (
    get_trash_coroutines,
    fill_orbit_with_garbage,
    get_trash_frames,
    fly_garbage,
)
from stars import get_stars_coroutines
from rocket import draw_rocket, fire


def draw(canvas):
    obstacles = []
    routines = []
    collisions = []

    canvas.nodelay(True)
    height, width = canvas.getmaxyx()
    border = {"top": 0, "bottom": height, "left": 0, "right": width}
    
    stars_coroutines = get_stars_coroutines(canvas, width, height)
    rocket_coroutine = draw_rocket(
        collisions,
        obstacles, routines, canvas, 
        height // 2, width // 2, border, speed_boost=1
    )
    filler = fill_orbit_with_garbage(collisions, obstacles, canvas, width, routines)
    ob_cors = show_obstacles(canvas, obstacles)

    routines.extend(
        [
            filler,
            rocket_coroutine,
            *stars_coroutines,            
            ob_cors
        ]
    )
    while True:
        for coroutine in routines.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                routines.remove(coroutine)                
                #print(len(collisions))
        canvas.refresh()
        time.sleep(0.05)
    


if __name__ == "__main__":
    curses.update_lines_cols()
    curses.initscr()
    curses.curs_set(False)
    curses.wrapper(draw)
