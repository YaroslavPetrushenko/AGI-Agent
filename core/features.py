def extract_features(state):
    grid = state["grid"]
    goal = state["goal"]

    # mismatch: сколько позиций в первой строке не совпадает с goal
    mismatch = 0
    for i in range(3):
        if grid[0][i] != goal[i]:
            mismatch += 1

    # расстояние курсора до центра
    cx, cy = state["cursor"]
    dist_center = abs(cx - 1) + abs(cy - 1)

    # количество доступных действий
    actions_count = len(state["actions"])

    # количество объектов R/G/B
    objects_count = 0
    empty_cells = 0
    for x in range(3):
        for y in range(3):
            if grid[x][y] in ["R", "G", "B"]:
                objects_count += 1
            if grid[x][y] == ".":
                empty_cells += 1

    return [mismatch, dist_center, actions_count, objects_count, empty_cells]
