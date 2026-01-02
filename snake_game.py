"""
Проста гра "Змійка" для терміналу.

Запуск: python snake_game.py
Керування: стрілки або WASD, вихід — q.

Як скопіювати та запустити на іншому комп'ютері:
1. Створіть будь-яку теку (наприклад, `snake/`) і збережіть у ній файл `snake_game.py`
   з цим кодом. Можна скопіювати текст вручну або передати файл через `scp`/USB.
2. Переконайтеся, що встановлено Python 3. На Windows додатково виконайте
   `pip install windows-curses`.
3. Відкрийте термінал у цій теці й запустіть `python snake_game.py`.
"""
from __future__ import annotations

import curses
import random
from typing import Deque, Tuple
from collections import deque

# Тип для координат (рядок, стовпець)
Point = Tuple[int, int]


def init_window() -> curses.window:
    """Підготовка екрану та кольорів."""
    window = curses.initscr()
    curses.curs_set(0)  # приховати курсор
    window.nodelay(True)  # не блокувати читання клавіш
    window.keypad(True)
    curses.noecho()
    curses.cbreak()

    if curses.has_colors():
        curses.start_color()
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)  # змійка
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)    # яблуко
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK) # текст

    return window


def draw_border(win: curses.window, height: int, width: int) -> None:
    """Малює рамку навколо поля."""
    for x in range(width + 2):
        win.addch(0, x, "#")
        win.addch(height + 1, x, "#")
    for y in range(1, height + 1):
        win.addch(y, 0, "#")
        win.addch(y, width + 1, "#")


def place_food(snake: Deque[Point], height: int, width: int) -> Point:
    """Розміщує нове яблуко в довільній вільній клітинці."""
    while True:
        food = (random.randint(1, height), random.randint(1, width))
        if food not in snake:
            return food


def move_snake(direction: Point, snake: Deque[Point]) -> Point:
    """Переміщує змійку у вказаному напрямку."""
    head_y, head_x = snake[0]
    dy, dx = direction
    new_head = (head_y + dy, head_x + dx)
    snake.appendleft(new_head)
    return new_head


def game_loop(win: curses.window, height: int = 20, width: int = 40) -> None:
    """Основний ігровий цикл."""
    snake: Deque[Point] = deque([(height // 2, width // 2)])
    direction: Point = (0, 1)  # початковий рух праворуч
    food = place_food(snake, height, width)
    score = 0

    draw_border(win, height, width)

    while True:
        win.timeout(100)
        key = win.getch()

        if key in (ord("q"), ord("Q")):
            break

        # Зміна напряму
        if key in (curses.KEY_UP, ord("w"), ord("W")) and direction != (1, 0):
            direction = (-1, 0)
        elif key in (curses.KEY_DOWN, ord("s"), ord("S")) and direction != (-1, 0):
            direction = (1, 0)
        elif key in (curses.KEY_LEFT, ord("a"), ord("A")) and direction != (0, 1):
            direction = (0, -1)
        elif key in (curses.KEY_RIGHT, ord("d"), ord("D")) and direction != (0, -1):
            direction = (0, 1)

        new_head = move_snake(direction, snake)

        # Перевірка зіткнень
        y, x = new_head
        if y == 0 or y == height + 1 or x == 0 or x == width + 1 or new_head in list(snake)[1:]:
            break

        if new_head == food:
            score += 1
            food = place_food(snake, height, width)
        else:
            snake.pop()

        win.clear()
        draw_border(win, height, width)

        # Рендер змійки
        for segment in snake:
            if curses.has_colors():
                win.addch(segment[0], segment[1], "@", curses.color_pair(1))
            else:
                win.addch(segment[0], segment[1], "@")

        # Рендер їжі
        if curses.has_colors():
            win.addch(food[0], food[1], "*", curses.color_pair(2))
        else:
            win.addch(food[0], food[1], "*")

        if curses.has_colors():
            win.addstr(height + 2, 0, f"Рахунок: {score}", curses.color_pair(3))
        else:
            win.addstr(height + 2, 0, f"Рахунок: {score}")

        win.refresh()

    win.nodelay(False)
    win.addstr(height // 2, (width // 2) - 4, "Гру завершено!")
    win.addstr(height // 2 + 1, (width // 2) - 8, f"Ваш рахунок: {score}")
    win.addstr(height // 2 + 2, (width // 2) - 11, "Натисніть будь-яку клавішу...")
    win.refresh()
    win.getch()


def main() -> None:
    """Точка входу у гру."""
    window = init_window()
    try:
        game_loop(window)
    finally:
        curses.nocbreak()
        window.keypad(False)
        curses.echo()
        curses.endwin()


if __name__ == "__main__":
    main()
