def find_object(state, obj):
    grid = state["grid"]
    for x in range(3):
        for y in range(3):
            if grid[x][y] == obj:
                return [x, y]
    return None


def find_goal_position(obj, goal):
    # goal = ["R", "G", "B"]
    if obj in goal:
        idx = goal.index(obj)
        # кладём в первую строку: [0, idx]
        return [0, idx]
    return None


def generate_hypotheses(state):
    grid = state["grid"]
    goal = state["goal"]

    hypotheses = []

    # гипотеза: привести R на своё место
    r_pos = find_object(state, "R")
    if r_pos is not None:
        r_goal = find_goal_position("R", goal)
        hypotheses.append({
            "type": "place_object",
            "object": "R",
            "from": r_pos,
            "to": r_goal
        })

    # гипотеза: привести G на своё место
    g_pos = find_object(state, "G")
    if g_pos is not None:
        g_goal = find_goal_position("G", goal)
        hypotheses.append({
            "type": "place_object",
            "object": "G",
            "from": g_pos,
            "to": g_goal
        })

    # гипотеза: привести B на своё место
    b_pos = find_object(state, "B")
    if b_pos is not None:
        b_goal = find_goal_position("B", goal)
        hypotheses.append({
            "type": "place_object",
            "object": "B",
            "from": b_pos,
            "to": b_goal
        })

    # запасная гипотеза — исследование
    hypotheses.append({
        "type": "explore",
        "description": "Random exploration"
    })

    return hypotheses


def apply_hypothesis(hypothesis, state):
    from core.actions import move_cursor_towards

    if hypothesis["type"] == "place_object":
        obj = hypothesis["object"]
        target_pos = hypothesis["to"]

        # если курсор не на объекте — идём к объекту
        obj_pos = hypothesis["from"]
        if state["cursor"] != obj_pos:
            return move_cursor_towards(state, obj_pos)

        # если курсор на объекте — идём к целевой позиции
        if state["cursor"] != target_pos:
            return move_cursor_towards(state, target_pos)

        # если курсор на целевой позиции — свап
        return {"type": "swap", "target": target_pos}

    if hypothesis["type"] == "explore":
        # простое исследование: двигаемся по кругу
        cx, cy = state["cursor"]
        if cx < 2:
            return {"type": "move", "direction": [1, 0]}
        elif cy < 2:
            return {"type": "move", "direction": [0, 1]}
        else:
            return {"type": "move", "direction": [-1, 0]}

    # запасное действие
    return {"type": "move", "direction": [1, 0]}
