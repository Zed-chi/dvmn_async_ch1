from random import randint, choice
from curses_tools import read_controls, draw_frame, get_frame_size
from itertools import cycle
import time
import asyncio
import curses
import os

def get_trash_coroutines(canvas, width, number=5):
    frames = get_trash_frames()
    coroutines = []
    for i in range(number):
        column = randint(1, width)
        frame = choice(frames)
        coroutines.append(fly_garbage(canvas,column, frame))
    return coroutines


def get_trash_frames():
    frames = []
    filesnames = os.listdir("./frames")
    for filename in filesnames:        
        path = os.path.join("./frames", filename)
        with open(path, "r") as file:
            frames.append(file.read())
    return frames


async def fly_garbage(canvas, column, garbage_frame, speed=0.5):
    """Animate garbage, flying from top to bottom. Сolumn position will stay same, as specified on start."""
    rows_number, columns_number = canvas.getmaxyx()

    column = max(column, 0)
    column = min(column, columns_number - 1)

    row = 0

    while row < rows_number:
        draw_frame(canvas, row, column, garbage_frame)
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, garbage_frame, negative=True)
        row += speed


def get_rocket_frames_iter():
    with open("animations/rocket_frame_1.txt", "r", encoding="utf-8") as file1:
        frame_1 = file1.read()
    with open("animations/rocket_frame_2.txt", "r", encoding="utf-8") as file2:
        frame_2 = file2.read()

    return cycle([frame_1, frame_1, frame_2, frame_2])


async def draw_rocket(
    canvas, start_row, start_column, border, negative=True, speed_boost=0
):
    row, column = (start_row, start_column)
    frames = get_rocket_frames_iter()
    for frame in frames:
        draw_frame(canvas, row, column, frame)
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, frame, negative=True)

        row_delta, column_delta, _ = read_controls(canvas)
        frame_rows, frame_columns = get_frame_size(frame)
        if row_delta == -1:
            row = max(border["top"], row + (row_delta * speed_boost))
            
        if row_delta == 1:
            row = min(
                border["bottom"] - frame_rows, row + (row_delta * speed_boost)
            )
        if column_delta == 1:
            column = min(
                border["right"] - frame_columns,
                column + (column_delta * speed_boost),
            )
        if column_delta == -1:
            column = max(border["left"], column + (column_delta * speed_boost))


async def blink(canvas, row, column, timings, symbol="*"):
    while True:
        for _ in range(timings["dim"]):
            canvas.addstr(row, column, symbol, curses.A_DIM)
            await asyncio.sleep(0)

        for _ in range(timings["normal"]):
            canvas.addstr(row, column, symbol)
            await asyncio.sleep(0)

        for _ in range(timings["bold"]):
            canvas.addstr(row, column, symbol, curses.A_BOLD)
            await asyncio.sleep(0)

        for _ in range(timings["normal"]):
            canvas.addstr(row, column, symbol)
            await asyncio.sleep(0)


async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    """Display animation of gun shot, direction and speed can be specified."""

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), 'O')
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


def get_stars_coroutines(canvas, width, height):
    coroutines = []
    symbols = "+*.:"
    for _ in range(30):
        timings = {
            "normal": randint(5, 30),
            "dim": randint(1, 20),
            "bold": randint(1, 20),
        }
        row = randint(1, height - 2)
        column = randint(1, width - 2)
        symbol = choice(symbols)
        coroutines.append(blink(canvas, row, column, timings, symbol))
    return coroutines


def draw(canvas):
    canvas.nodelay(True)
    height, width = canvas.getmaxyx()
    border = {"top": 0, "bottom": height, "left": 0, "right": width}
    stars_coroutines = get_stars_coroutines(canvas, width, height)
    rocket_coroutine = draw_rocket(
        canvas, height / 2, width / 2, border, speed_boost=1
    )
    trash_cors = get_trash_coroutines(canvas, width, 6)
    fire_coroutine = fire(canvas, height-1, width/2)
    coroutines = [*stars_coroutines, rocket_coroutine, fire_coroutine, *trash_cors]
    while True:
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)
        canvas.refresh()
        time.sleep(0.05)


if __name__ == "__main__":
    curses.update_lines_cols()
    curses.initscr()
    curses.curs_set(False)
    curses.wrapper(draw)
