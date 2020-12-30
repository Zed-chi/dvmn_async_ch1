from itertools import cycle
import curses
from curses_tools import read_controls, draw_frame, get_frame_size
from utils import sleep
from physics import update_speed

""" rocket stuff """


def get_rocket_frames_iter():
    with open(
        "./animations/rocket_frame_1.txt", "r", encoding="utf-8"
    ) as file1:
        frame_1 = file1.read()
    with open(
        "./animations/rocket_frame_2.txt", "r", encoding="utf-8"
    ) as file2:
        frame_2 = file2.read()

    return cycle([frame_1, frame_1, frame_2, frame_2])


async def run_spaceship(
    routines,
):
    pass


async def fire(
    obstacles, canvas, start_row, 
    start_column, rows_speed=-1, columns_speed=0
):
    """Display animation of gun shot, direction and speed can be specified."""

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), "*")
    await sleep()

    canvas.addstr(round(row), round(column), "O")
    await sleep()
    canvas.addstr(round(row), round(column), " ")

    row += rows_speed
    column += columns_speed

    symbol = "-" if columns_speed else "|"

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    # curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        for i in obstacles: 
            if i.has_collision(row,column):
                return
        
        canvas.addstr(round(row), round(column), symbol)
        await sleep()
        canvas.addstr(round(row), round(column), " ")
        row += rows_speed
        column += columns_speed


async def draw_rocket(
    obstacles,
    routines,
    canvas,
    start_row,
    start_column,
    border,
    negative=True,
    speed_boost=0,
):
    row, column = (start_row, start_column)
    row_speed = column_speed = 0
    frames = get_rocket_frames_iter()
    for frame in frames:
        draw_frame(canvas, row, column, frame)
        await sleep()
        draw_frame(canvas, row, column, frame, negative=True)

        row_delta, column_delta, space = read_controls(canvas)
        frame_rows, frame_columns = get_frame_size(frame)

        row_speed, column_speed = update_speed(
            row_speed, column_speed, row_delta, column_delta
        )

        if row_delta == -1:
            row = max(border["top"], row + row_speed)
        elif row_delta == 1:
            row = min(border["bottom"] - frame_rows, row + row_speed)
        elif row_delta == 0:
            row = min(border["bottom"] - frame_rows, row + row_speed)
            row = max(border["top"], row)

        if column_delta == 1:
            column = min(
                border["right"] - frame_columns,
                column + column_speed,
            )
        elif column_delta == -1:
            column = max(border["left"], column + column_speed)
        elif column_delta == 0:
            column = max(border["left"], column + column_speed)
            column = min(
                border["right"] - frame_columns,
                column,
            )
        if space:
            routines.append(
                fire(obstacles, canvas, row, column)
            )
