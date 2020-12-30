import os
import asyncio
from random import randint, choice
from curses_tools import draw_frame, get_frame_size
from utils import sleep
from obstacles import Obstacle
from explosion import explode


def get_trash_frames():
    frames = []
    filesnames = os.listdir("./frames")
    for filename in filesnames:
        path = os.path.join("./frames", filename)
        with open(path, "r") as file:
            frames.append(file.read())
    return frames


""" Garbage stuff"""


async def fill_orbit_with_garbage(collisions, obstacles, canvas, width, routines):
    frames = get_trash_frames()

    while True:
        column = randint(1, width)
        frame = choice(frames)
        rows, columns = get_frame_size(frame)
        a = Obstacle(0, column, rows, columns)
        obstacles.append(a)
        routines.append(fly_garbage(routines, collisions, obstacles, a, canvas, column, frame))
        await sleep(7)


def get_trash_coroutines(canvas, width, height, number=5):
    frames = get_trash_frames()
    coroutines = []
    for _ in range(number):
        column = randint(1, width)
        row = randint(1, height)
        speed = randint(2, 10) / 10
        frame = choice(frames)
        coroutines.append(fly_garbage(canvas, column, frame, row, speed))
    return coroutines


async def fly_garbage(routines, collisions, obs, 
    obstacle, canvas, column, garbage_frame, row=0, speed=0.3
):
    """Animate garbage, flying from top to bottom. Сolumn position will stay same, as specified on start."""
    rows_number, columns_number = canvas.getmaxyx()

    column = max(column, 0)
    column = min(column, columns_number - 1)

    while row < rows_number:
        obstacle.row = row
        draw_frame(canvas, row, column, garbage_frame)
        
        await sleep(1)
        draw_frame(canvas, row, column, garbage_frame, negative=True)
        row += speed
        
        for i in collisions:            
            if obstacle.has_collision(        
                i.row,
                i.column,                        
            ):
                routines.append(explode(canvas, row, column))
                collisions.remove(i)
                obs.remove(obstacle)
                return                
    obs.remove(obstacle)
