"""
Scene 5: Feistel Network Attack

Visualizes:
  1. The 3-round Feistel network structure
  2. The attack: encrypt (x, 0) and (x, 1) and XOR the left halves
  3. How this creates a Simon period related to the round key
"""

from manim import *


class FeistelNetworkAttack(Scene):
    def construct(self):
        title = Text("Quantum Attack on 3-Round Feistel", font_size=36)
        title.to_edge(UP, buff=0.3)
        self.play(Write(title))
        self.wait(0.3)

        # ── Part 1: Feistel structure ──
        struct_label = Text("3-Round Feistel Network", font_size=24, color=BLUE)
        struct_label.next_to(title, DOWN, buff=0.3)
        self.play(FadeIn(struct_label))

        # Draw a simplified Feistel diagram
        # Two vertical tracks: L (left) and R (right)
        l_x = -1.5
        r_x = 1.5
        y_top = 1.0
        round_height = 1.2

        # Input labels
        l_in = MathTex("L_0", font_size=26, color=BLUE)
        l_in.move_to([l_x, y_top + 0.4, 0])
        r_in = MathTex("R_0", font_size=26, color=GREEN)
        r_in.move_to([r_x, y_top + 0.4, 0])
        self.play(FadeIn(l_in), FadeIn(r_in))

        # Draw 3 rounds
        round_groups = VGroup()
        for rnd in range(3):
            y = y_top - rnd * round_height

            # F box on the right track
            f_box = Rectangle(width=1.0, height=0.5, color=YELLOW,
                              fill_opacity=0.15)
            f_box.move_to([0, y - 0.25, 0])
            f_text = MathTex(f"F_{{k}}", font_size=20, color=YELLOW)
            f_text.move_to(f_box.get_center())

            # Arrow from R into F
            arr_r_to_f = Arrow([r_x, y, 0], [0.5, y - 0.25, 0],
                               buff=0.1, color=GREEN, stroke_width=2,
                               max_tip_length_to_length_ratio=0.15)

            # XOR circle on left track
            xor_circ = Circle(radius=0.15, color=ORANGE, fill_opacity=0.2)
            xor_circ.move_to([l_x, y - 0.25, 0])
            xor_text = MathTex(r"\oplus", font_size=14, color=ORANGE)
            xor_text.move_to(xor_circ.get_center())

            # Arrow from F to XOR
            arr_f_to_xor = Arrow([f_box.get_left()[0], y - 0.25, 0],
                                 [xor_circ.get_right()[0], y - 0.25, 0],
                                 buff=0.05, color=ORANGE, stroke_width=2,
                                 max_tip_length_to_length_ratio=0.15)

            # Crossing lines (swap for next round)
            if rnd < 2:
                y_next = y - round_height
                # L -> R (the XOR result goes to right)
                cross1 = Line([l_x, y - 0.55, 0], [r_x, y_next + 0.1, 0],
                              color=BLUE_B, stroke_width=1.5)
                # R -> L (right passes through to left)
                cross2 = Line([r_x, y - 0.55, 0], [l_x, y_next + 0.1, 0],
                              color=GREEN_B, stroke_width=1.5)
                round_groups.add(cross1, cross2)

            round_groups.add(f_box, f_text, arr_r_to_f,
                             xor_circ, xor_text, arr_f_to_xor)

        # Output labels
        y_out = y_top - 3 * round_height + 0.3
        l_out = MathTex("L_3", font_size=26, color=BLUE)
        l_out.move_to([l_x, y_out, 0])
        r_out = MathTex("R_3", font_size=26, color=GREEN)
        r_out.move_to([r_x, y_out, 0])

        self.play(
            FadeIn(round_groups),
            FadeIn(l_out), FadeIn(r_out),
            run_time=2
        )
        self.wait(1)

        # ── Part 2: The attack function ──
        self.play(
            *[FadeOut(m) for m in [round_groups, l_in, r_in, l_out, r_out,
                                    struct_label]],
        )

        attack_label = Text("The Attack", font_size=24, color=RED)
        attack_label.next_to(title, DOWN, buff=0.3)
        self.play(FadeIn(attack_label))

        # Two side-by-side encryptions
        enc_0 = VGroup(
            MathTex(r"\text{Encrypt } (x, 0)", font_size=24, color=BLUE),
            MathTex(r"\rightarrow (L_0, R_0)", font_size=22, color=BLUE_B),
        ).arrange(DOWN, buff=0.1)
        enc_0.move_to(LEFT * 3 + UP * 0.3)

        enc_1 = VGroup(
            MathTex(r"\text{Encrypt } (x, 1)", font_size=24, color=GREEN),
            MathTex(r"\rightarrow (L_1, R_1)", font_size=22, color=GREEN_B),
        ).arrange(DOWN, buff=0.1)
        enc_1.move_to(RIGHT * 3 + UP * 0.3)

        self.play(FadeIn(enc_0), FadeIn(enc_1))
        self.wait(0.5)

        # XOR the left halves
        xor_formula = MathTex(
            r"f(x) = L_0 \oplus L_1",
            font_size=30, color=YELLOW
        )
        xor_formula.move_to(DOWN * 0.5)
        self.play(Write(xor_formula))
        self.wait(0.5)

        # The result
        period_eq = MathTex(
            r"f(x) = f(x \oplus s) \quad \text{where } s = S[k] \oplus S[1 \oplus k]",
            font_size=26, color=ORANGE
        )
        period_eq.next_to(xor_formula, DOWN, buff=0.4)
        self.play(FadeIn(period_eq))
        self.wait(0.5)

        # Steps
        steps = VGroup(
            MathTex(
                r"\textbf{1.}\ \text{Simon's recovers } s",
                font_size=24, color=WHITE
            ),
            MathTex(
                r"\textbf{2.}\ \text{Brute-force } k \text{ from } "
                r"S[k] \oplus S[1 \oplus k] = s",
                font_size=24, color=WHITE
            ),
            MathTex(
                r"\textbf{3.}\ \text{Only a few candidates to check}",
                font_size=24, color=WHITE
            ),
        ).arrange(DOWN, buff=0.2, aligned_edge=LEFT)
        steps.next_to(period_eq, DOWN, buff=0.5)
        self.play(LaggedStart(*[FadeIn(s) for s in steps], lag_ratio=0.4))

        # Punchline
        punchline = Text(
            "Quantum complexity: O(n) queries + small brute-force",
            font_size=20, color=RED_B
        )
        punchline.to_edge(DOWN, buff=0.3)
        self.play(FadeIn(punchline))
        self.wait(2)
