import random

# Поле 3x3: на нём табличное Q-обучение реально сходится (число состояний
# исчислимо). При этом случайная расстановка и случайная цель дают тысячи
# разных задач — агенту приходится ориентироваться в незнакомых ситуациях.
GRID_SIZES = [3]
ALPHABET = ["R", "G", "B", "Y", "P", "O", "C", "M"]


def generate_environment():
    # случайный размер поля
    size = random.choice(GRID_SIZES)

    # случайное число объектов (минимум 3, не больше размера и алфавита)
    max_objects = min(size, len(ALPHABET))
    n_objects = random.randint(3, max_objects)

    objects = ALPHABET[:n_objects]

    # цель всегда фиксированная — собрать объекты по порядку (R G B)
    goal = objects[:]

    # случайно раскидываем объекты по полю
    cells = [[x, y] for x in range(size) for y in range(size)]
    positions = random.sample(cells, n_objects)

    grid = [["." for _ in range(size)] for _ in range(size)]
    for obj, (x, y) in zip(objects, positions):
        grid[x][y] = obj

    state = {
        "grid": grid,
        "goal": goal,
        "size": size,
        "actions": ["move", "swap"],
        "cursor": random.choice(cells)
    }

    return state


def apply_action(state, action):
    size = len(state["grid"])
    grid = [row[:] for row in state["grid"]]
    cursor = state["cursor"][:]

    if action["type"] == "move":
        dx, dy = action["direction"]
        nx = max(0, min(size - 1, cursor[0] + dx))
        ny = max(0, min(size - 1, cursor[1] + dy))
        cursor = [nx, ny]

    elif action["type"] == "swap":
        tx, ty = action["target"]
        cx, cy = cursor
        grid[cx][cy], grid[tx][ty] = grid[tx][ty], grid[cx][cy]

    return {
        "grid": grid,
        "goal": state["goal"],
        "size": size,
        "actions": state["actions"],
        "cursor": cursor
    }


def is_goal(state):
    # цель — первые len(goal) клеток первой строки совпадают с целевым порядком
    goal = state["goal"]
    row0 = state["grid"][0]
    return row0[:len(goal)] == goal
