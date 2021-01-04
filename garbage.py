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


async def fill_orbit_with_garbage(
    state,
    canvas,
    width,
):
    frames = get_trash_frames()

    while True:
        column = randint(1, width)
        frame = choice(frames)
        rows, columns = get_frame_size(frame)
        a = Obstacle(0, column, rows, columns)
        state["obstacles"].append(a)        
        
        if state['level'] == 1:
            state["routines"].append(fly_garbage(state, a, canvas, column, frame, speed=0.1))
            await sleep(30)
        elif state['level'] == 2:
            state["routines"].append(fly_garbage(state, a, canvas, column, frame, speed=0.2))
            await sleep(25)
        elif state['level'] == 3:
            state["routines"].append(fly_garbage(state, a, canvas, column, frame, speed=0.25))
            await sleep(20)
        elif state['level'] == 4:
            state["routines"].append(fly_garbage(state, a, canvas, column, frame, speed=0.3))
            await sleep(15)
        elif state['level'] == 5:
            state["routines"].append(fly_garbage(state, a, canvas, column, frame, speed=0.35))
            await sleep(13)
        elif state['level'] == 6:
            state["routines"].append(fly_garbage(state, a, canvas, column, frame, speed=0.40))
            await sleep(11)
        elif state['level'] == 7:
            state["routines"].append(fly_garbage(state, a, canvas, column, frame, speed=0.45))
            await sleep(10)
        elif state['level'] == 8:
            state["routines"].append(fly_garbage(state, a, canvas, column, frame, speed=0.5))
            await sleep(9)
        elif state['level'] == 9:
            state["routines"].append(fly_garbage(state, a, canvas, column, frame, speed=0.55))
            await sleep(8)
        elif state['level'] >= 10:
            state["routines"].append(fly_garbage(state, a, canvas, column, frame, speed=0.60))
            await sleep(5)
        


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


async def fly_garbage(
    state,
    obstacle,
    canvas,
    column,
    garbage_frame,
    row=0,
    speed=0.3,
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

        for i in state["collisions"]:
            if obstacle.has_collision(
                i.row,
                i.column,
            ):
                state["routines"].append(explode(canvas, row, column))
                state["collisions"].remove(i)
                state["obstacles"].remove(obstacle)
                return
    state["obstacles"].remove(obstacle)
