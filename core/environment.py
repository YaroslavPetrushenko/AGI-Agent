import random

def generate_environment():
    # базовый пазл RGB
    grid = [
        ["G", ".", "."],
        [".", "B", "."],
        [".", ".", "R"]
    ]

    state = {
        "grid": grid,
        "goal": ["R", "G", "B"],
        "actions": ["move", "swap"],
        "cursor": [0, 0]
    }

    return state


def apply_action(state, action):
    grid = [row[:] for row in state["grid"]]
    cursor = state["cursor"][:]

    if action["type"] == "move":
        dx, dy = action["direction"]
        nx = max(0, min(2, cursor[0] + dx))
        ny = max(0, min(2, cursor[1] + dy))
        cursor = [nx, ny]

    elif action["type"] == "swap":
        tx, ty = action["target"]
        cx, cy = cursor
        grid[cx][cy], grid[tx][ty] = grid[tx][ty], grid[cx][cy]

    return {
        "grid": grid,
        "goal": state["goal"],
        "actions": state["actions"],
        "cursor": cursor
    }


def is_goal(state):
    # считаем, что цель — первая строка соответствует goal
    row0 = state["grid"][0]
    return row0 == state["goal"]
