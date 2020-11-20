from random import randint, choice
from curses_tools import read_controls, draw_frame, get_frame_size
from itertools import cycle
import time
import asyncio
import curses


def rocket_frames():
    with open("animations/rocket_frame_1.txt", "r", encoding="utf-8") as file1:
        frame_1 = file1.read()
    with open("animations/rocket_frame_2.txt", "r", encoding="utf-8") as file2:
        frame_2 = file2.read()
    
    return cycle([frame_1, frame_2])


async def draw_rocket(canvas, start_row, start_column, negative=True):
    row, column = (start_row, start_column)
    frames = rocket_frames()

    while True:
        frame = next(frames)
        draw_frame(canvas, row, column, frame)
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, frame, negative=True)

        frame = next(frames)
        draw_frame(canvas, row, column, frame, negative=False)
        await asyncio.sleep(0)        
        draw_frame(canvas, row, column, frame, negative=True)

        row_delta, column_delta, _ = read_controls(canvas)        
        row += row_delta
        column += column_delta
        


async def blink(canvas, row, column, symbol="*"):
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await asyncio.sleep(0)
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await asyncio.sleep(0)
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        await asyncio.sleep(0)
        canvas.addstr(row, column, symbol)
        await asyncio.sleep(0)
        canvas.addstr(row, column, symbol)
        await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        await asyncio.sleep(0)


async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
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


def draw(canvas):
    canvas.nodelay(True)    
    y, x = canvas.getmaxyx()
    symbols = "+*.:"    
    #fire_cor = fire(canvas, y - 2, x / 2)
    rocket_cor = draw_rocket(canvas, y / 2, x / 2)
    coroutines = [
        rocket_cor,
    ]

    for i in range(20):
        row = randint(1, y - 2)
        column = randint(1, x - 2)
        symbol = choice(symbols)
        coroutines.append(blink(canvas, row, column, symbol))
    #canvas.border()

    for i in range(1000):        
        cors = coroutines.copy()
        for cor in cors:
            try:
                cor.send(None)
                canvas.refresh()
                time.sleep(0.01)
            except StopIteration:
                coroutines.remove(cor)
        


if __name__ == "__main__":
    curses.update_lines_cols()
    curses.initscr()
    curses.curs_set(False)
    curses.wrapper(draw)
