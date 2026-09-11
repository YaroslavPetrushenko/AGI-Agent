def calculate_agi_score(history):
    if len(history) == 0:
        return 0.0

    total_reward = sum(h[2] for h in history)
    positive = sum(1 for h in history if h[2] > 0)

    # базовая метрика: комбинация награды и доли положительных шагов
    reward_score = max(total_reward, 0)
    rule_discovery = min(positive / len(history), 1.0)

    return round(reward_score + rule_discovery * 10, 2)
