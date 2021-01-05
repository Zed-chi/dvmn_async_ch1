import os

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
        garbage_obstacle = Obstacle(0, column, rows, columns)
        state["obstacles"].append(garbage_obstacle)

        if state["level"] == 1:
            garbage_speed = 0.1
            time_to_sleep = 30
        elif state["level"] == 2:
            garbage_speed = 0.2
            time_to_sleep = 25
        elif state["level"] == 3:
            garbage_speed = 0.25
            time_to_sleep = 20
        elif state["level"] == 4:
            garbage_speed = 0.3
            time_to_sleep = 15
        elif state["level"] == 5:
            garbage_speed = 0.35
            time_to_sleep = 13
        elif state["level"] == 6:
            garbage_speed = 0.4
            time_to_sleep = 11
        elif state["level"] == 7:
            garbage_speed = 0.45
            time_to_sleep = 10
        elif state["level"] == 8:
            garbage_speed = 0.5
            time_to_sleep = 9
        elif state["level"] == 9:
            garbage_speed = 0.55
            time_to_sleep = 8
        elif state["level"] >= 10:
            garbage_speed = 0.6
            time_to_sleep = 5
        else:
            garbage_speed = 0.6
            time_to_sleep = 5
        state["routines"].append(
            fly_garbage(
                state,
                garbage_obstacle,
                canvas,
                column,
                frame,
                speed=garbage_speed,
            ),
        )
        await sleep(time_to_sleep)


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
    try:
        while row < rows_number:
            obstacle.row = row
            draw_frame(canvas, row, column, garbage_frame)

            await sleep(1)
            draw_frame(canvas, row, column, garbage_frame, negative=True)
            row += speed

            for collision in state["collisions"]:
                if obstacle.has_collision(
                    collision.row,
                    collision.column,
                ):
                    state["routines"].append(explode(canvas, row, column))
                    state["collisions"].remove(collision)                    
                    return
    finally:
        state["obstacles"].remove(obstacle)
