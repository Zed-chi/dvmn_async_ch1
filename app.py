from random import randint, choice
from curses_tools import read_controls, draw_frame, get_frame_size
from itertools import cycle
import time
import asyncio
import curses


def get_rocket_frames_iter():
    with open("animations/rocket_frame_1.txt", "r", encoding="utf-8") as file1:
        frame_1 = file1.read()
    with open("animations/rocket_frame_2.txt", "r", encoding="utf-8") as file2:
        frame_2 = file2.read()

    return cycle([frame_1, frame_2])


async def draw_rocket(canvas, start_row, start_column, border, negative=True):
    row, column = (start_row, start_column)
    frames = get_rocket_frames_iter()

    for frame in frames:
        draw_frame(canvas, row, column, frame)
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, frame, negative=True)

        row_delta, column_delta, _ = read_controls(canvas)
        frame_rows, frame_columns = get_frame_size(frame)
        if row_delta == -1:
            row = max(border["top"], row + row_delta)
        if row_delta == 1:
            row = min(border["bottom"] - frame_rows, row + row_delta)
        if column_delta == 1:
            column = min(
                border["right"] - frame_columns, column + column_delta
            )
        if column_delta == -1:
            column = max(border["left"], column + column_delta)


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


async def fire(
    canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0
):
    """Display animation of gun shot, direction and speed can be specified."""

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), "*")
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), "O")
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), " ")

    row += rows_speed
    column += columns_speed

    symbol = "-" if columns_speed else "|"

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), " ")
        row += rows_speed
        column += columns_speed


def get_stars_coroutines(canvas, width, height):
    coroutines = []
    symbols = "+*.:"
    for _ in range(30):
        timings = {
            "normal": randint(5, 20),
            "dim": randint(1, 10),
            "bold": randint(1, 10),
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
    rocket_coroutine = draw_rocket(canvas, height / 2, width / 2, border)
    coroutines = [*stars_coroutines, rocket_coroutine]
    while True:
        for coroutine in coroutines.copy():
            coroutine.send(None)
        canvas.refresh()
        time.sleep(0.01)


if __name__ == "__main__":
    curses.update_lines_cols()
    curses.initscr()
    curses.curs_set(False)
    curses.wrapper(draw)
