import json
import os

WEIGHTS_FILE = "memory/weights.json"
DEFAULT_WEIGHTS = [0.1, 0.1, 0.1, 0.1, 0.1]


def save_weights(weights):
    with open(WEIGHTS_FILE, "w") as f:
        json.dump(weights, f, indent=4)


def load_weights():
    if not os.path.exists(WEIGHTS_FILE):
        save_weights(DEFAULT_WEIGHTS)
        return DEFAULT_WEIGHTS

    try:
        with open(WEIGHTS_FILE, "r") as f:
            data = f.read().strip()
            if data == "":
                raise ValueError("Empty JSON")
            return json.loads(data)
    except:
        save_weights(DEFAULT_WEIGHTS)
        return DEFAULT_WEIGHTS


def update_weights(weights, features, reward):
    # простое обучение: двигаем веса по признакам
    lr = 0.05
    new_weights = []

    for w, f in zip(weights, features):
        new_w = w + lr * reward * f
        new_weights.append(new_w)

    return new_weights
