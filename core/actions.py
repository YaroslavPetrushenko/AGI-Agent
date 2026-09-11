def move_cursor_towards(state, target):
    cx, cy = state["cursor"]
    tx, ty = target

    dx = 0
    dy = 0

    if tx > cx:
        dx = 1
    elif tx < cx:
        dx = -1

    if ty > cy:
        dy = 1
    elif ty < cy:
        dy = -1

    return {"type": "move", "direction": [dx, dy]}


def execute(action, state):
    from core.environment import apply_action

    return apply_action(state, action)
