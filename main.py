import time
import os
import sys

from core.environment import generate_environment, is_goal
from core.qlearning import QAgent, count_correct
from memory.memory import save_state, save_history
from stats_window import LearningStats, StatsWindow

MAX_STEPS = 60
STEP_DELAY = 0.12


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def print_menu(episode, step, state, action, reward, agent, start_time):
    clear_screen()
    elapsed = round(time.time() - start_time, 2)

    explore_pct = round(agent.epsilon * 100)

    print("============== AGI-Agent (Q-learning) ==============")
    print(f"Эпизод: {episode}")
    print(f"Поле: {state['size']}x{state['size']}   Цель: {' '.join(state['goal'])}")
    print(f"Шаг: {step + 1} / {MAX_STEPS}")
    print(f"Награда за шаг: {reward:+.2f}")
    print(f"Исследование (случайные ходы): {explore_pct}%")
    print(f"Изучено состояний: {agent.states_learned()}")
    print(f"Время: {elapsed}s")
    print(f"Действие: {action}")
    print("\nПоле:")
    for x, row in enumerate(state["grid"]):
        marks = []
        for y, cell in enumerate(row):
            marks.append(f"[{cell}]" if [x, y] == state["cursor"] else f" {cell} ")
        print("".join(marks))
    print("====================================================")


def run_episode(agent, stats=None, window=None, training=True):
    state = generate_environment()
    start_time = time.time()
    reward_sum = 0.0
    episode_no = (stats.episodes + 1) if stats else 1

    step = 0
    for step in range(MAX_STEPS):
        action = agent.choose(state, explore=training)

        correct_before = count_correct(state)
        next_state = agent.step_env(state, action)
        correct_after = count_correct(next_state)
        done = is_goal(next_state)

        # награда: +1 за каждую вновь верно поставленную клетку, штраф за шаг,
        # бонус за полное решение. Агент сам ищет, какие действия её приносят.
        reward = (correct_after - correct_before) - 0.02
        if done:
            reward += 1.0
        reward = round(reward, 3)
        reward_sum += reward

        if training:
            agent.learn(state, action, reward, next_state, done)

        state = next_state

        save_history(step, state, action, reward)
        save_state(state)

        print_menu(episode_no, step, state, action, reward, agent, start_time)
        if window:
            avg_reward = reward_sum / (step + 1)
            window.on_step(episode_no, state, step, avg_reward, agent)

        time.sleep(STEP_DELAY)

        if done:
            print("\nРешено! Агент собрал цель.")
            break

    steps_used = step + 1
    solved = is_goal(state)
    avg_reward = reward_sum / steps_used if steps_used else 0.0

    if training:
        agent.decay_epsilon()
        agent.save()

    if stats:
        stats.record_episode(steps_used, avg_reward, solved)
    if window:
        window.on_episode_end(agent)


def learn_from_scratch(episodes=4000):
    """Быстрое обучение с НУЛЯ: агент стартует, ничего не зная, и на глазах
    умнеет. Кривая обучения в окне падает по мере роста мастерства."""
    if os.path.exists("memory/qtable.json"):
        os.remove("memory/qtable.json")

    agent = QAgent()  # свежий: epsilon=1.0, пустая таблица
    stats = LearningStats()
    window = StatsWindow(stats)

    print("Обучение с нуля... (Ctrl+C чтобы остановить)")
    try:
        for ep in range(episodes):
            state = generate_environment()
            reward_sum = 0.0
            step = 0
            for step in range(MAX_STEPS):
                action = agent.choose(state, explore=True)
                cb = count_correct(state)
                nxt = agent.step_env(state, action)
                ca = count_correct(nxt)
                done = is_goal(nxt)
                reward = (ca - cb) - 0.02 + (1.0 if done else 0.0)
                reward_sum += reward
                agent.learn(state, action, reward, nxt, done)
                state = nxt
                if done:
                    break
            agent.decay_epsilon()
            solved = is_goal(state)
            stats.record_episode(step + 1, reward_sum / (step + 1), solved)
            window.on_episode_end(agent)  # обновляем кривую каждый эпизод
            if (ep + 1) % 50 == 0:
                clear_screen()
                print(f"Эпизод {ep + 1}/{episodes}")
                print(f"Исследование (наугад): {round(agent.epsilon * 100)}%")
                print(f"Изучено состояний: {agent.states_learned()}")
                last = stats.steps_history[-50:]
                print(f"Шагов на решение (в начале {stats.baseline_steps}, "
                      f"сейчас ~{round(sum(last)/len(last))})")
    except KeyboardInterrupt:
        pass
    finally:
        agent.save()
        print("\nГотово. Мозг агента сохранён в memory/qtable.json")
        window.close()


def demo_loop():
    """Показ выученного: агент решает случайные незнакомые расстановки."""
    agent = QAgent()
    stats = LearningStats()
    window = StatsWindow(stats)
    try:
        while True:
            run_episode(agent, stats, window, training=False)
            time.sleep(0.6)
    except KeyboardInterrupt:
        pass
    finally:
        window.close()


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "demo"

    if mode == "learn":
        learn_from_scratch()
    elif mode == "while":
        # бесконечное обучение с показом каждого шага
        agent = QAgent()
        stats = LearningStats()
        window = StatsWindow(stats)
        try:
            while True:
                run_episode(agent, stats, window, training=True)
                time.sleep(0.4)
        except KeyboardInterrupt:
            pass
        finally:
            window.close()
    else:
        demo_loop()
