import asyncio
import curses
from random import randint, choice

""" stars stuff """


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
