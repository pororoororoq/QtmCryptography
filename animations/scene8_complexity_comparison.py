"""
Scene 8: Complexity Comparison Table

Animated bar chart / table comparing classical vs quantum attack
complexity for each cipher type we implemented.
"""

from manim import *


class ComplexityComparison(Scene):
    def construct(self):
        title = Text("Classical vs Quantum: Attack Complexity", font_size=36)
        title.to_edge(UP, buff=0.3)
        self.play(Write(title))
        self.wait(0.3)

        # ── Build comparison table ──
        # Headers
        headers = VGroup(
            Text("Attack", font_size=22, color=WHITE, weight=BOLD),
            Text("Classical", font_size=22, color=BLUE, weight=BOLD),
            Text("Quantum", font_size=22, color=RED, weight=BOLD),
            Text("Speedup", font_size=22, color=YELLOW, weight=BOLD),
        )
        col_x = [-3.5, -0.5, 2.0, 4.5]
        for header, x in zip(headers, col_x):
            header.move_to([x, 2.0, 0])

        self.play(*[FadeIn(h) for h in headers])

        header_line = Line(LEFT * 5.5 + UP * 1.7, RIGHT * 5.8 + UP * 1.7,
                           color=GRAY, stroke_width=1)
        self.play(Create(header_line))

        # Data rows
        rows_data = [
            ("Simon's\n(period finding)", r"O(2^{n/2})", r"O(n)",
             "Exponential"),
            ("Even-Mansour\n(key recovery)", r"O(2^{n/2})", r"O(n)",
             "Exponential"),
            ("3-Round Feistel\n(key recovery)", r"O(2^{n/2})", r"O(n) + \text{bf}",
             "Exponential"),
            ("Slide Attack\n(iterated cipher)", r"O(2^{n/2})", r"O(n)",
             "Exponential"),
        ]

        row_groups = VGroup()
        for i, (attack, classical, quantum, speedup) in enumerate(rows_data):
            y = 1.1 - i * 0.9

            attack_text = Text(attack, font_size=17, color=WHITE,
                               line_spacing=1.0)
            attack_text.move_to([col_x[0], y, 0])

            classical_text = MathTex(classical, font_size=24, color=BLUE_B)
            classical_text.move_to([col_x[1], y, 0])

            quantum_text = MathTex(quantum, font_size=24, color=RED_B)
            quantum_text.move_to([col_x[2], y, 0])

            speedup_text = Text(speedup, font_size=18, color=YELLOW)
            speedup_text.move_to([col_x[3], y, 0])

            row = VGroup(attack_text, classical_text, quantum_text, speedup_text)
            row_groups.add(row)

        for row in row_groups:
            self.play(FadeIn(row), run_time=0.7)

        self.wait(1)

        # ── Animated bar chart below ──
        # Show O(2^{n/2}) vs O(n) for n = 8, 16, 32, 64
        self.play(*[FadeOut(m) for m in [*row_groups, headers, header_line]])

        chart_title = Text(
            "Query count: classical vs quantum (log scale)",
            font_size=22, color=WHITE
        )
        chart_title.next_to(title, DOWN, buff=0.3)
        self.play(FadeIn(chart_title))

        # Bar chart data
        n_values = [8, 16, 32, 64]
        classical_costs = [2**4, 2**8, 2**16, 2**32]  # 2^{n/2}
        quantum_costs = [8, 16, 32, 64]  # O(n)

        # Use log scale for display
        import math
        max_log = math.log2(2**32)  # = 32
        bar_max_height = 3.0

        bar_width = 0.5
        gap = 2.0  # gap between groups

        groups = VGroup()
        for i, n in enumerate(n_values):
            center_x = -4.0 + i * gap

            # Classical bar
            c_log = math.log2(classical_costs[i])
            c_height = (c_log / max_log) * bar_max_height
            c_bar = Rectangle(
                width=bar_width, height=max(c_height, 0.1),
                color=BLUE, fill_opacity=0.6,
            )
            c_bar.move_to([center_x - 0.35, -2.0 + c_height / 2, 0])

            c_label = MathTex(f"2^{{{int(c_log)}}}", font_size=16, color=BLUE)
            c_label.next_to(c_bar, UP, buff=0.05)

            # Quantum bar
            q_log = math.log2(quantum_costs[i])
            q_height = (q_log / max_log) * bar_max_height
            q_bar = Rectangle(
                width=bar_width, height=max(q_height, 0.1),
                color=RED, fill_opacity=0.6,
            )
            q_bar.move_to([center_x + 0.35, -2.0 + q_height / 2, 0])

            q_label = MathTex(f"{quantum_costs[i]}", font_size=16, color=RED)
            q_label.next_to(q_bar, UP, buff=0.05)

            # n label
            n_label = MathTex(f"n={n}", font_size=20, color=WHITE)
            n_label.move_to([center_x, -2.3, 0])

            group = VGroup(c_bar, c_label, q_bar, q_label, n_label)
            groups.add(group)

        # Baseline
        baseline = Line(LEFT * 5.5 + DOWN * 2, RIGHT * 5.5 + DOWN * 2,
                        color=GRAY, stroke_width=1)
        self.play(Create(baseline))

        # Animate bars growing
        for group in groups:
            self.play(
                *[GrowFromEdge(group[0], DOWN),  # classical bar
                  GrowFromEdge(group[2], DOWN),  # quantum bar
                  FadeIn(group[1]),   # classical label
                  FadeIn(group[3]),   # quantum label
                  FadeIn(group[4])],  # n label
                run_time=0.8
            )

        # Legend
        legend = VGroup(
            VGroup(
                Rectangle(width=0.3, height=0.2, color=BLUE, fill_opacity=0.6),
                Text("Classical: O(2^{n/2})", font_size=16, color=BLUE),
            ).arrange(RIGHT, buff=0.1),
            VGroup(
                Rectangle(width=0.3, height=0.2, color=RED, fill_opacity=0.6),
                Text("Quantum: O(n)", font_size=16, color=RED),
            ).arrange(RIGHT, buff=0.1),
        ).arrange(RIGHT, buff=0.5)
        legend.to_edge(DOWN, buff=0.15)
        self.play(FadeIn(legend))

        # Final message
        msg = Text(
            "At n=64: classical needs ~4 billion queries, quantum needs 64.",
            font_size=20, color=YELLOW
        )
        msg.next_to(legend, UP, buff=0.2)
        self.play(FadeIn(msg))
        self.wait(2)
