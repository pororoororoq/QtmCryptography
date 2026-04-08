"""
Scene 6: Slide Attack — Round Count Doesn't Matter

The key visual insight: classical security grows with rounds,
but the quantum slide attack bypasses ALL rounds by attacking
the single round function directly. Shows a bar chart where
classical cost grows but quantum cost stays flat.
"""

from manim import *


class SlideAttackRoundIndependence(Scene):
    def construct(self):
        title = Text("Quantum Slide Attack: Rounds Don't Help", font_size=36)
        title.to_edge(UP, buff=0.3)
        self.play(Write(title))
        self.wait(0.3)

        # ── Part 1: Iterated cipher structure ──
        struct_label = Text(
            "Iterated cipher: apply the SAME round r times",
            font_size=22, color=BLUE
        )
        struct_label.next_to(title, DOWN, buff=0.3)
        self.play(FadeIn(struct_label))

        # Show round chain
        rounds_display = VGroup()
        n_display = 6
        for i in range(n_display):
            box = Rectangle(width=0.9, height=0.7, color=YELLOW,
                            fill_opacity=0.15)
            label = MathTex(f"F_k", font_size=20, color=YELLOW)
            label.move_to(box.get_center())
            rounds_display.add(VGroup(box, label))

        dots = MathTex(r"\cdots", font_size=30, color=GRAY)
        rounds_display.add(dots)

        last_box = Rectangle(width=0.9, height=0.7, color=YELLOW,
                             fill_opacity=0.15)
        last_label = MathTex(f"F_k", font_size=20, color=YELLOW)
        last_label.move_to(last_box.get_center())
        rounds_display.add(VGroup(last_box, last_label))

        rounds_display.arrange(RIGHT, buff=0.15)
        rounds_display.move_to(UP * 0.5)

        x_in = MathTex("x", font_size=28, color=WHITE)
        x_in.next_to(rounds_display, LEFT, buff=0.3)
        x_out = MathTex("E_k(x)", font_size=28, color=WHITE)
        x_out.next_to(rounds_display, RIGHT, buff=0.3)

        arr_in = Arrow(x_in.get_right(), rounds_display.get_left(),
                       buff=0.05, color=GRAY, stroke_width=2)
        arr_out = Arrow(rounds_display.get_right(), x_out.get_left(),
                        buff=0.05, color=GRAY, stroke_width=2)

        self.play(
            FadeIn(x_in), GrowArrow(arr_in),
            FadeIn(rounds_display),
            GrowArrow(arr_out), FadeIn(x_out),
            run_time=1.5
        )

        r_label = MathTex(r"r \text{ rounds}", font_size=22, color=GRAY)
        r_brace = Brace(rounds_display, DOWN, buff=0.1, color=GRAY)
        r_label.next_to(r_brace, DOWN, buff=0.1)
        self.play(GrowFromCenter(r_brace), FadeIn(r_label))
        self.wait(1)

        # ── Part 2: The slide insight ──
        self.play(
            *[FadeOut(m) for m in [rounds_display, x_in, x_out, arr_in,
                                    arr_out, r_brace, r_label, struct_label]],
        )

        insight = Text(
            "Attack targets ONE round, not the full cipher!",
            font_size=24, color=RED
        )
        insight.next_to(title, DOWN, buff=0.3)
        self.play(FadeIn(insight))

        attack_eq = MathTex(
            r"f(x) = F_k(x) \oplus P(x) = P(x \oplus k) \oplus P(x)",
            font_size=28, color=GREEN
        )
        attack_eq.move_to(UP * 0.5)
        self.play(Write(attack_eq))

        period_eq = MathTex(
            r"\text{Simon period: } s = k",
            font_size=28, color=YELLOW
        )
        period_eq.next_to(attack_eq, DOWN, buff=0.3)
        self.play(FadeIn(period_eq))
        self.wait(1)

        # ── Part 3: Bar chart comparison ──
        self.play(FadeOut(insight), FadeOut(attack_eq), FadeOut(period_eq))

        chart_label = Text("Cost vs Number of Rounds", font_size=24, color=WHITE)
        chart_label.next_to(title, DOWN, buff=0.3)
        self.play(FadeIn(chart_label))

        # Axes
        ax_origin = LEFT * 4 + DOWN * 2
        ax = Axes(
            x_range=[0, 10, 2],
            y_range=[0, 100, 20],
            x_length=7,
            y_length=3.5,
            axis_config={"color": GRAY, "font_size": 20},
            tips=False,
        )
        ax.move_to(DOWN * 0.3 + LEFT * 0.3)

        x_label = Text("Number of rounds (r)", font_size=18, color=GRAY)
        x_label.next_to(ax, DOWN, buff=0.3)
        y_label = Text("Attack cost", font_size=18, color=GRAY)
        y_label.next_to(ax, LEFT, buff=0.3).rotate(PI / 2)

        self.play(Create(ax), FadeIn(x_label), FadeIn(y_label))

        # Classical cost: grows with r (birthday bound ~ 2^{n/2} per round pair)
        # Simplified: show it growing
        classical_points = [(1, 15), (2, 25), (3, 35), (4, 45),
                            (5, 55), (6, 62), (7, 70), (8, 78), (9, 85)]
        classical_line = ax.plot_line_graph(
            x_values=[p[0] for p in classical_points],
            y_values=[p[1] for p in classical_points],
            line_color=BLUE,
            vertex_dot_style={"fill_color": BLUE, "radius": 0.05},
            stroke_width=3,
        )
        classical_tag = Text("Classical", font_size=18, color=BLUE)
        classical_tag.move_to(ax.c2p(9, 90))

        # Quantum cost: flat! O(n) regardless of r
        quantum_points = [(1, 10), (2, 10), (3, 10), (4, 10),
                          (5, 10), (6, 10), (7, 10), (8, 10), (9, 10)]
        quantum_line = ax.plot_line_graph(
            x_values=[p[0] for p in quantum_points],
            y_values=[p[1] for p in quantum_points],
            line_color=RED,
            vertex_dot_style={"fill_color": RED, "radius": 0.05},
            stroke_width=3,
        )
        quantum_tag = Text("Quantum (Simon)", font_size=18, color=RED)
        quantum_tag.move_to(ax.c2p(9, 15))

        self.play(Create(classical_line), FadeIn(classical_tag), run_time=1.5)
        self.wait(0.5)
        self.play(Create(quantum_line), FadeIn(quantum_tag), run_time=1.5)
        self.wait(0.5)

        # Punchline
        punchline = Text(
            '"Just add more rounds" is NOT a defense\n'
            'against a quantum adversary!',
            font_size=22, color=RED,
            line_spacing=1.3,
        )
        punchline.to_edge(DOWN, buff=0.2)
        box = SurroundingRectangle(punchline, color=RED, buff=0.15)
        self.play(Create(box), FadeIn(punchline))
        self.wait(2)
