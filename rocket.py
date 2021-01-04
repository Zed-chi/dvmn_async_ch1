import curses
from itertools import cycle

from curses_tools import read_controls, draw_frame, get_frame_size
from explosion import explode
from obstacles import Collision, Obstacle
from physics import update_speed
from utils import sleep


def get_end_title_frame():
    with open("end.txt", "r") as file:
        return file.read()


async def end(canvas):
    rows_number, columns_number = canvas.getmaxyx()
    frame = get_end_title_frame()
    while True:
        draw_frame(canvas, rows_number // 2, 10, frame)
        await sleep(100)


def get_rocket_frames_iter():
    with open(
        "./animations/rocket_frame_1.txt", "r", encoding="utf-8",
    ) as file1:
        frame_1 = file1.read()
    with open(
        "./animations/rocket_frame_2.txt", "r", encoding="utf-8",
    ) as file2:
        frame_2 = file2.read()

    return cycle([frame_1, frame_1, frame_2, frame_2])


async def fire(
    state,
    canvas,
    start_row,
    start_column,
    rows_speed=-1,
    columns_speed=0,
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

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        for obstacle in state["obstacles"]:
            if obstacle.has_collision(row, column):
                state["collisions"].append(Collision(int(row), int(column)))
                return

        canvas.addstr(round(row), round(column), symbol)
        await sleep()
        canvas.addstr(round(row), round(column), " ")
        row += rows_speed
        column += columns_speed


async def draw_rocket(
    state,
    canvas,
    start_row,
    start_column,
    border,
    negative=True,
    speed_boost=1,
):
    row, column = (start_row, start_column)
    row_speed = column_speed = 0
    frames = get_rocket_frames_iter()
    rows, columns = get_frame_size(next(frames))
    rocket = Obstacle(row, column, rows, columns)

    for frame in frames:
        rocket.row = row
        rocket.column = column
        for obstacle in state["obstacles"]:
            if rocket.has_collision(
                obstacle.row,
                obstacle.column,
                obstacle.rows_size,
                obstacle.columns_size,
            ):
                state["routines"].append(explode(canvas, row, column))
                state["routines"].append(end(canvas))
                return
        draw_frame(canvas, row, column, frame)
        await sleep()
        draw_frame(canvas, row, column, frame, negative=True)

        row_delta, column_delta, space = read_controls(canvas)
        if space and state["year"] >= 1960:
            state["routines"].append(fire(state, canvas, row, column + 2))

        frame_rows, frame_columns = get_frame_size(frame)

        row_speed, column_speed = update_speed(
            row_speed, column_speed, row_delta, column_delta,
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
