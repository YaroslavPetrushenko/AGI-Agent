from core.hypotheses import apply_hypothesis


def choose_action(features, hypotheses, available_actions, weights, state):
    # features: [mismatch, dist_center, len(actions), len(objects), empty_cells]
    mismatch = features[0]

    # если mismatch большой — выбираем гипотезу place_object
    place_hypotheses = [h for h in hypotheses if h["type"] == "place_object"]
    explore_hypotheses = [h for h in hypotheses if h["type"] == "explore"]

    if mismatch > 0 and place_hypotheses:
        hypothesis = place_hypotheses[0]
    else:
        hypothesis = explore_hypotheses[0] if explore_hypotheses else hypotheses[0]

    action = apply_hypothesis(hypothesis, state)

    if action["type"] in available_actions:
        return action

    return {"type": "move", "direction": [1, 0]}
