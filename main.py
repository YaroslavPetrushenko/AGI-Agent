import time
import os
import sys

from core.environment import generate_environment, is_goal
from core.features import extract_features
from core.hypotheses import generate_hypotheses
from core.decision import choose_action
from core.actions import execute
from core.learning import load_weights, update_weights, save_weights
from core.agi_score import calculate_agi_score
from memory.memory import save_state, save_history, save_rule

MAX_STEPS = 50


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def print_menu(step, state, action, reward, accuracy, weights, start_time):
    clear_screen()

    elapsed = round(time.time() - start_time, 2)

    print("============== AGI-Agent ==============")
    print(f"Step: {step} / {MAX_STEPS}")
    print(f"Accuracy: {round(accuracy * 100, 2)}%")
    print(f"Reward: {reward}")
    print(f"Time: {elapsed}s")
    print(f"Action: {action}")
    print("\nGrid:")

    for row in state["grid"]:
        print(" ".join(row))

    print(f"\nCursor: {state['cursor']}")
    print(f"Weights: {weights}")
    print("========================================")


def run_episode():
    weights = load_weights()
    state = generate_environment()
    history = []

    start_time = time.time()
    good_steps = 0

    for step in range(MAX_STEPS):
        features = extract_features(state)
        hypotheses = generate_hypotheses(state)
        action = choose_action(features, hypotheses, state["actions"], weights, state)

        state = execute(action, state)

        reward = 1 if is_goal(state) else -0.1

        if reward > 0:
            good_steps += 1

        accuracy = good_steps / (step + 1)

        weights = update_weights(weights, features, reward)
        save_weights(weights)

        save_history(step, state, action, reward)
        save_state(state)

        history.append((step, action, reward))

        if reward > 0:
            save_rule({"step": step, "hypotheses": hypotheses})

        print_menu(step, state, action, reward, accuracy, weights, start_time)

        time.sleep(0.2)

        if is_goal(state):
            print("\nGoal reached!")
            break

    if len(history) == 0:
        score = 0
    else:
        score = calculate_agi_score(history)

    print("\nFinal AGI Score:", score)


def main():
    run_episode()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "while":
        while True:
            run_episode()
            time.sleep(0.5)
    else:
        main()
