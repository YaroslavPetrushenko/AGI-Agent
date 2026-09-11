"""Окно статистики обучения (tkinter, входит в стандартную библиотеку Python).

Показывает судьям, что агент учится САМ, с нуля, без подсказок человека:
счётчик эпизодов, число шагов на решение (и сколько было в начале),
доля исследования (случайных ходов), сколько состояний агент уже изучил,
и график кривой обучения — он падает по мере того, как агент умнеет.
"""

try:
    import tkinter as tk
    _TK_AVAILABLE = True
except Exception:
    _TK_AVAILABLE = False


class LearningStats:
    """Копит статистику между эпизодами."""

    def __init__(self):
        self.episodes = 0
        self.steps_history = []
        self.reward_history = []
        self.baseline_steps = None      # шагов в самом первом эпизоде
        self.total_solved = 0

    def record_episode(self, steps, avg_reward, solved):
        self.episodes += 1
        self.steps_history.append(steps)
        self.reward_history.append(avg_reward)
        if self.baseline_steps is None:
            self.baseline_steps = steps
        if solved:
            self.total_solved += 1


class StatsWindow:
    """Живое окно tkinter. Если графика недоступна — молча отключается."""

    def __init__(self, stats):
        self.stats = stats
        self.enabled = _TK_AVAILABLE
        if not self.enabled:
            return
        try:
            self._build()
        except Exception:
            # нет дисплея / tkinter не смог открыть окно — работаем без него
            self.enabled = False

    def _build(self):
        self.root = tk.Tk()
        self.root.title("AGI-Agent — агент учится сам")
        self.root.configure(bg="#12141c")
        self.root.geometry("540x600")

        fg = "#e8ecff"
        accent = "#7cc7ff"

        tk.Label(
            self.root, text="AGI-Agent: обучение с нуля, без подсказок человека",
            bg="#12141c", fg=accent, font=("Segoe UI", 13, "bold"), pady=10
        ).pack()

        self.info = tk.Label(
            self.root, text="", bg="#12141c", fg=fg,
            font=("Consolas", 11), justify="left"
        )
        self.info.pack(anchor="w", padx=18)

        tk.Label(
            self.root, text="\nСколько агент ещё исследует наугад:",
            bg="#12141c", fg=accent, font=("Segoe UI", 10, "bold")
        ).pack(anchor="w", padx=18)

        self.explore_canvas = tk.Canvas(
            self.root, width=500, height=40, bg="#1b1e2b", highlightthickness=0
        )
        self.explore_canvas.pack(padx=18, pady=6)

        tk.Label(
            self.root, text="Кривая обучения (шагов на решение по эпизодам):",
            bg="#12141c", fg=accent, font=("Segoe UI", 10, "bold")
        ).pack(anchor="w", padx=18, pady=(8, 0))

        self.curve_canvas = tk.Canvas(
            self.root, width=500, height=190, bg="#1b1e2b", highlightthickness=0
        )
        self.curve_canvas.pack(padx=18, pady=6)

        tk.Label(
            self.root,
            text="Чем ниже линия — тем быстрее агент решает пазл: значит, он научился сам.",
            bg="#12141c", fg="#9aa4c8", font=("Segoe UI", 9), wraplength=500
        ).pack(anchor="w", padx=18)

        self._pump()

    # --- служебное ---
    def _pump(self):
        if self.enabled:
            try:
                self.root.update_idletasks()
                self.root.update()
            except tk.TclError:
                self.enabled = False   # окно закрыли

    def _draw_explore(self, epsilon):
        c = self.explore_canvas
        c.delete("all")
        W = 500
        explore = int(W * epsilon)
        # синяя часть — осознанные ходы, оранжевая — случайные (исследование)
        c.create_rectangle(0, 8, W, 32, fill="#2b6f9e", outline="")
        c.create_rectangle(0, 8, explore, 32, fill="#e0994d", outline="")
        c.create_text(explore + 6 if explore < W - 90 else explore - 6,
                      20, anchor="w" if explore < W - 90 else "e",
                      text=f"наугад {round(epsilon*100)}%",
                      fill="#ffffff", font=("Consolas", 9, "bold"))

    def _draw_curve(self):
        c = self.curve_canvas
        c.delete("all")
        hist = self.stats.steps_history
        if len(hist) < 1:
            return
        W, H, pad = 500, 190, 26
        max_s, min_s = max(hist), min(hist)
        span = max(1, max_s - min_s)
        n = len(hist)

        def px(i):
            return pad if n == 1 else pad + (W - 2 * pad) * i / (n - 1)

        def py(v):
            return pad + (H - 2 * pad) * (v - min_s) / span  # меньше шагов -> выше

        c.create_line(pad, pad, pad, H - pad, fill="#3a3f55")
        c.create_line(pad, H - pad, W - pad, H - pad, fill="#3a3f55")

        pts = [(px(i), py(v)) for i, v in enumerate(hist)]
        if len(pts) >= 2:
            flat = [c2 for xy in pts for c2 in xy]
            c.create_line(*flat, fill="#7cc7ff", width=2, smooth=True)
        for (x, y) in pts[-50:]:
            c.create_oval(x - 2, y - 2, x + 2, y + 2, fill="#7cc7ff", outline="")

        c.create_text(pad + 2, pad - 2, anchor="sw",
                      text=f"макс {max_s}", fill="#9aa4c8", font=("Consolas", 8))
        c.create_text(pad + 2, H - pad + 2, anchor="nw",
                      text=f"мин {min_s}", fill="#9aa4c8", font=("Consolas", 8))

    # --- публичное API ---
    def _info_text(self, episode, state, step, avg_reward, agent):
        base = self.stats.baseline_steps
        base_txt = f"   (в начале решал за {base})" if base is not None else ""
        return (
            f"Эпизод: {episode}\n"
            f"Поле: {state['size']}x{state['size']}    Цель: {' '.join(state['goal'])}\n"
            f"Шаг в эпизоде: {step + 1}\n"
            f"Решено пазлов: {self.stats.total_solved}{base_txt}\n"
            f"Изучено состояний: {agent.states_learned()}\n"
            f"Средняя награда за шаг: {avg_reward:+.2f}"
        )

    def on_step(self, episode, state, step, avg_reward, agent):
        if not self.enabled:
            return
        self.info.config(text=self._info_text(episode, state, step, avg_reward, agent))
        self._draw_explore(agent.epsilon)
        self._pump()

    def on_episode_end(self, agent):
        if not self.enabled:
            return
        self._draw_explore(agent.epsilon)
        self._draw_curve()
        self._pump()

    def close(self):
        if self.enabled:
            try:
                self.root.destroy()
            except Exception:
                pass
