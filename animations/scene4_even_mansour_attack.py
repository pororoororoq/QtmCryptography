"""
Scene 4: Even-Mansour Cipher Attack

Visualizes:
  1. The Even-Mansour cipher structure: E(x) = P(x XOR k1) XOR k2
  2. The attack function f(x) = E(x) XOR P(x)
  3. How keys cancel to create a Simon period: f(x) = f(x XOR k1)
"""

from manim import *


class EvenMansourAttack(Scene):
    def construct(self):
        title = Text("Quantum Attack on Even-Mansour Cipher", font_size=36)
        title.to_edge(UP, buff=0.3)
        self.play(Write(title))
        self.wait(0.5)

        # ── Part 1: Show the cipher structure ──
        subtitle1 = Text("The Cipher", font_size=26, color=BLUE)
        subtitle1.next_to(title, DOWN, buff=0.3)
        self.play(FadeIn(subtitle1))

        # Build cipher pipeline: x -> [XOR k1] -> [P] -> [XOR k2] -> E(x)
        pipe_y = 0.8
        x_label = MathTex("x", font_size=32, color=WHITE)
        x_label.move_to(LEFT * 5.5 + UP * pipe_y)

        xor_k1_box = Rectangle(width=1.4, height=0.8, color=RED,
                                fill_opacity=0.15)
        xor_k1_box.move_to(LEFT * 3.5 + UP * pipe_y)
        xor_k1_text = MathTex(r"\oplus\, k_1", font_size=24, color=RED)
        xor_k1_text.move_to(xor_k1_box.get_center())

        p_box = Rectangle(width=1.4, height=0.8, color=YELLOW,
                          fill_opacity=0.15)
        p_box.move_to(LEFT * 1.2 + UP * pipe_y)
        p_text = MathTex("P", font_size=28, color=YELLOW)
        p_text.move_to(p_box.get_center())

        xor_k2_box = Rectangle(width=1.4, height=0.8, color=RED,
                                fill_opacity=0.15)
        xor_k2_box.move_to(RIGHT * 1.0 + UP * pipe_y)
        xor_k2_text = MathTex(r"\oplus\, k_2", font_size=24, color=RED)
        xor_k2_text.move_to(xor_k2_box.get_center())

        out_label = MathTex("E(x)", font_size=32, color=WHITE)
        out_label.move_to(RIGHT * 3.0 + UP * pipe_y)

        # Arrows
        arrows_cipher = VGroup(
            Arrow(x_label.get_right(), xor_k1_box.get_left(), buff=0.1,
                  color=GRAY, stroke_width=2),
            Arrow(xor_k1_box.get_right(), p_box.get_left(), buff=0.1,
                  color=GRAY, stroke_width=2),
            Arrow(p_box.get_right(), xor_k2_box.get_left(), buff=0.1,
                  color=GRAY, stroke_width=2),
            Arrow(xor_k2_box.get_right(), out_label.get_left(), buff=0.1,
                  color=GRAY, stroke_width=2),
        )

        cipher_group = VGroup(
            x_label, xor_k1_box, xor_k1_text, p_box, p_text,
            xor_k2_box, xor_k2_text, out_label, arrows_cipher
        )
        self.play(FadeIn(cipher_group), run_time=1.5)

        formula_cipher = MathTex(
            r"E(x) = P(x \oplus k_1) \oplus k_2",
            font_size=28, color=BLUE_B
        )
        formula_cipher.next_to(cipher_group, RIGHT, buff=0.5)
        self.play(FadeIn(formula_cipher))
        self.wait(1)

        # ── Part 2: The attack function ──
        self.play(FadeOut(subtitle1))
        subtitle2 = Text("The Attack Function", font_size=26, color=GREEN)
        subtitle2.next_to(title, DOWN, buff=0.3)
        self.play(FadeIn(subtitle2))

        attack_formula = MathTex(
            r"f(x) = E(x) \oplus P(x)",
            font_size=30, color=GREEN
        )
        attack_formula.move_to(DOWN * 0.3)
        self.play(Write(attack_formula))
        self.wait(0.5)

        # Expand
        expand = MathTex(
            r"= P(x \oplus k_1) \oplus k_2 \oplus P(x)",
            font_size=28, color=GREEN_B
        )
        expand.next_to(attack_formula, DOWN, buff=0.3)
        self.play(FadeIn(expand))
        self.wait(0.5)

        # ── Part 3: Why it has period k1 ──
        self.play(FadeOut(subtitle2))
        subtitle3 = Text("Why f has Simon period s = k1", font_size=26,
                         color=YELLOW)
        subtitle3.next_to(title, DOWN, buff=0.3)
        self.play(FadeIn(subtitle3))

        proof_lines = VGroup(
            MathTex(
                r"f(x \oplus k_1)",
                font_size=26, color=WHITE
            ),
            MathTex(
                r"= P((x \oplus k_1) \oplus k_1) \oplus k_2 \oplus P(x \oplus k_1)",
                font_size=24, color=WHITE
            ),
            MathTex(
                r"= P(x) \oplus k_2 \oplus P(x \oplus k_1)",
                font_size=26, color=ORANGE
            ),
            MathTex(
                r"= P(x \oplus k_1) \oplus k_2 \oplus P(x)",
                font_size=26, color=ORANGE
            ),
            MathTex(
                r"= f(x) \quad \checkmark",
                font_size=28, color=YELLOW
            ),
        ).arrange(DOWN, buff=0.2, aligned_edge=LEFT)
        proof_lines.move_to(DOWN * 1.5)

        for line in proof_lines:
            self.play(FadeIn(line), run_time=0.6)
        self.wait(0.5)

        # ── Part 4: The punchline ──
        punchline_box = Rectangle(width=10, height=1, color=RED,
                                  fill_opacity=0.1)
        punchline_box.to_edge(DOWN, buff=0.2)
        punchline = Text(
            "Simon's algorithm recovers k1 in O(n) queries.\n"
            "Then k2 = E(0) XOR P(k1). Both keys recovered!",
            font_size=20, color=RED_B,
            line_spacing=1.3,
        )
        punchline.move_to(punchline_box.get_center())
        self.play(Create(punchline_box), FadeIn(punchline))
        self.wait(2)
