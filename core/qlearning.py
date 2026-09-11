"""Q-обучение с нуля — без зашитых подсказок.

Агент НЕ знает заранее, как решать пазл. Он видит поле, у него есть набор
действий (двигать курсор и менять местами соседние клетки) и награда за
прогресс. Стратегию — «подвести объект к его месту и поставить» — он должен
открыть сам, пробуя действия и запоминая, какие из них ведут к награде.

Метод: табличное Q-обучение.
    Q(s, a) <- Q(s, a) + alpha * (r + gamma * max_a' Q(s', a') - Q(s, a))
Выбор действия — epsilon-жадный: иногда пробуем случайное (исследование),
иначе берём лучшее известное (использование). Epsilon со временем падает —
агент всё меньше тыкается наугад и всё больше действует осознанно.
"""

import json
import os
import random

from core.environment import apply_action, is_goal

QTABLE_FILE = "memory/qtable.json"

# 8 действий: подвинуть курсор в 4 стороны и поменять клетку с соседом в 4 стороны
DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]


def count_correct(state):
    """Сколько клеток первой строки уже стоят на своих целевых местах."""
    goal = state["goal"]
    row0 = state["grid"][0]
    return sum(1 for i in range(len(goal)) if row0[i] == goal[i])


def state_key(state):
    """Компактный строковый ключ состояния (поле + курсор + цель)."""
    grid = "/".join("".join(row) for row in state["grid"])
    cursor = "{},{}".format(*state["cursor"])
    goal = "".join(state["goal"])
    return f"{grid}|{cursor}|{goal}"


def available_actions(state):
    """Легальные действия из текущего состояния (без выхода за границы)."""
    size = state["size"]
    cx, cy = state["cursor"]
    actions = []
    for dx, dy in DIRECTIONS:
        nx, ny = cx + dx, cy + dy
        if 0 <= nx < size and 0 <= ny < size:
            actions.append(f"move:{dx},{dy}")   # подвинуть курсор
            actions.append(f"swap:{dx},{dy}")   # поменять клетку с соседом
    return actions


def action_to_env(action, state):
    """Перевод строкового действия в формат среды."""
    kind, delta = action.split(":")
    dx, dy = (int(v) for v in delta.split(","))
    if kind == "move":
        return {"type": "move", "direction": [dx, dy]}
    cx, cy = state["cursor"]
    return {"type": "swap", "target": [cx + dx, cy + dy]}


class QAgent:
    def __init__(self, alpha=0.2, gamma=0.95,
                 epsilon=1.0, epsilon_min=0.02, epsilon_decay=0.9995):
        self.q = {}                      # ключ состояния -> {действие: ценность}
        self.alpha = alpha               # скорость обучения
        self.gamma = gamma               # насколько ценим будущую награду
        self.epsilon = epsilon           # доля случайных действий (исследование)
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.load()

    # --- доступ к таблице ---
    def _qrow(self, key):
        if key not in self.q:
            self.q[key] = {}
        return self.q[key]

    def _qval(self, key, action):
        return self.q.get(key, {}).get(action, 0.0)

    def states_learned(self):
        return len(self.q)

    # --- выбор действия ---
    def choose(self, state, explore=True):
        actions = available_actions(state)
        key = state_key(state)

        if explore and random.random() < self.epsilon:
            return random.choice(actions)

        # берём действие с максимальной ценностью (случайно среди равных лучших)
        best_val = None
        best = []
        for a in actions:
            v = self._qval(key, a)
            if best_val is None or v > best_val:
                best_val, best = v, [a]
            elif v == best_val:
                best.append(a)
        return random.choice(best)

    def step_env(self, state, action):
        return apply_action(state, action_to_env(action, state))

    # --- обучение ---
    def learn(self, state, action, reward, next_state, done):
        key = state_key(state)
        row = self._qrow(key)
        old = row.get(action, 0.0)

        if done:
            target = reward
        else:
            next_key = state_key(next_state)
            next_actions = available_actions(next_state)
            future = max((self._qval(next_key, a) for a in next_actions),
                         default=0.0)
            target = reward + self.gamma * future

        row[action] = old + self.alpha * (target - old)

    def decay_epsilon(self):
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    # --- сохранение / загрузка ---
    def save(self):
        try:
            with open(QTABLE_FILE, "w") as f:
                json.dump({"epsilon": self.epsilon, "q": self.q}, f)
        except Exception:
            pass

    def load(self):
        if not os.path.exists(QTABLE_FILE):
            return
        try:
            with open(QTABLE_FILE, "r") as f:
                data = json.load(f)
            self.q = data.get("q", {})
            self.epsilon = data.get("epsilon", self.epsilon)
        except Exception:
            self.q = {}
