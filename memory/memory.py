import json
import os

STATE_FILE = "memory/state.json"
MEMORY_FILE = "memory/memory.json"
RULES_FILE = "memory/rules.json"
HISTORY_FILE = "memory/history.json"


def _safe_load_list(path):
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r") as f:
            data = f.read().strip()
            if data == "":
                return []
            return json.loads(data)
    except:
        return []


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=4)


def load_state():
    if not os.path.exists(STATE_FILE):
        return None
    with open(STATE_FILE, "r") as f:
        return json.load(f)


def save_memory_state(state):
    memory = _safe_load_list(MEMORY_FILE)
    memory.append(state)
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=4)


def save_rule(rule):
    rules = _safe_load_list(RULES_FILE)
    rules.append(rule)
    with open(RULES_FILE, "w") as f:
        json.dump(rules, f, indent=4)


def load_rules():
    return _safe_load_list(RULES_FILE)


def save_history(step, state, action, reward):
    history = _safe_load_list(HISTORY_FILE)
    history.append({
        "step": step,
        "state": state,
        "action": action,
        "reward": reward
    })
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=4)


def load_history():
    return _safe_load_list(HISTORY_FILE)
