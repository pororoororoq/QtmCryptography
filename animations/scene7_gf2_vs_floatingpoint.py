"""
Scene 7: GF(2) Linear Algebra — Why Floating Point Breaks

Demonstrates the subtle bug: vectors that are linearly independent
over the real numbers can be linearly DEPENDENT over GF(2).
numpy.linalg.matrix_rank gives the WRONG answer for Simon's algorithm.
"""

from manim import *


class GF2VsFloatingPoint(Scene):
    def construct(self):
        title = Text("GF(2) Rank vs Floating-Point Rank", font_size=36)
        title.to_edge(UP, buff=0.3)
        self.play(Write(title))
        self.wait(0.3)

        # ── Part 1: The problem ──
        problem = Text(
            "Simon's algorithm solves a linear system modulo 2 (GF(2)).",
            font_size=22, color=BLUE
        )
        problem.next_to(title, DOWN, buff=0.3)
        self.play(FadeIn(problem))
        self.wait(0.5)

        # Show example vectors
        vec_label = Text("Consider these 3 vectors:", font_size=22, color=WHITE)
        vec_label.move_to(UP * 0.8 + LEFT * 3)

        v1 = MathTex(r"v_1 = (1, 0)", font_size=28, color=RED)
        v2 = MathTex(r"v_2 = (0, 1)", font_size=28, color=GREEN)
        v3 = MathTex(r"v_3 = (1, 1)", font_size=28, color=YELLOW)

        vecs = VGroup(v1, v2, v3).arrange(DOWN, buff=0.2, aligned_edge=LEFT)
        vecs.next_to(vec_label, DOWN, buff=0.3, aligned_edge=LEFT)
        self.play(FadeIn(vec_label), FadeIn(vecs))
        self.wait(0.5)

        # ── Side-by-side comparison ──
        # Real numbers side
        real_box = Rectangle(width=5, height=3.5, color=BLUE, fill_opacity=0.05)
        real_box.move_to(LEFT * 3 + DOWN * 1.5)
        real_title = Text("Over Real Numbers", font_size=22, color=BLUE)
        real_title.next_to(real_box, UP, buff=0.1)

        real_content = VGroup(
            MathTex(r"v_1 + v_2 = (1, 1) \neq v_3?", font_size=22),
            MathTex(r"\text{Well, } (1,0) + (0,1) = (1,1) = v_3",
                    font_size=22, color=BLUE_B),
            MathTex(r"\text{So } v_3 = v_1 + v_2", font_size=22),
            MathTex(r"\text{rank} = 2", font_size=26, color=BLUE),
        ).arrange(DOWN, buff=0.15)
        real_content.move_to(real_box.get_center())

        # GF(2) side
        gf2_box = Rectangle(width=5, height=3.5, color=GREEN, fill_opacity=0.05)
        gf2_box.move_to(RIGHT * 3 + DOWN * 1.5)
        gf2_title = Text("Over GF(2) (mod 2)", font_size=22, color=GREEN)
        gf2_title.next_to(gf2_box, UP, buff=0.1)

        gf2_content = VGroup(
            MathTex(r"v_1 \oplus v_2 = (1, 1) = v_3",
                    font_size=22, color=GREEN_B),
            MathTex(r"\text{So } v_3 = v_1 \oplus v_2 \text{ (mod 2)}",
                    font_size=22),
            MathTex(r"\text{rank}_{\text{GF(2)}} = 2", font_size=26,
                    color=GREEN),
            MathTex(r"\text{Same answer here!}", font_size=20, color=GRAY),
        ).arrange(DOWN, buff=0.15)
        gf2_content.move_to(gf2_box.get_center())

        self.play(
            Create(real_box), FadeIn(real_title), FadeIn(real_content),
            Create(gf2_box), FadeIn(gf2_title), FadeIn(gf2_content),
            run_time=1.5
        )
        self.wait(1)

        # Fade and show the tricky case
        self.play(
            *[FadeOut(m) for m in [real_box, real_title, real_content,
                                    gf2_box, gf2_title, gf2_content,
                                    vec_label, vecs, problem]],
        )

        # ── Part 2: Where they DIFFER ──
        tricky_label = Text(
            "Where it goes WRONG:",
            font_size=24, color=RED
        )
        tricky_label.next_to(title, DOWN, buff=0.3)
        self.play(FadeIn(tricky_label))

        mat_label = Text("Matrix of collected y-vectors:", font_size=22)
        mat_label.move_to(UP * 0.8)
        self.play(FadeIn(mat_label))

        matrix = MathTex(
            r"A = \begin{pmatrix} 1 & 1 \\ 1 & 0 \\ 0 & 1 \end{pmatrix}",
            font_size=32
        )
        matrix.move_to(UP * 0.0)
        self.play(FadeIn(matrix))
        self.wait(0.5)

        # Real rank
        real_box2 = Rectangle(width=5, height=2.5, color=BLUE, fill_opacity=0.05)
        real_box2.move_to(LEFT * 3 + DOWN * 2)
        real_title2 = Text("numpy rank (float)", font_size=20, color=BLUE)
        real_title2.next_to(real_box2, UP, buff=0.1)

        real_content2 = VGroup(
            MathTex(r"\text{Row 3} = \text{Row 1} - \text{Row 2}", font_size=22,
                    color=BLUE_B),
            MathTex(r"(0,1) = (1,1) - (1,0)", font_size=22),
            MathTex(r"\text{rank} = 2 \quad \checkmark", font_size=24, color=BLUE),
        ).arrange(DOWN, buff=0.15)
        real_content2.move_to(real_box2.get_center())

        # GF(2) rank
        gf2_box2 = Rectangle(width=5, height=2.5, color=GREEN, fill_opacity=0.05)
        gf2_box2.move_to(RIGHT * 3 + DOWN * 2)
        gf2_title2 = Text("GF(2) rank (mod 2)", font_size=20, color=GREEN)
        gf2_title2.next_to(gf2_box2, UP, buff=0.1)

        gf2_content2 = VGroup(
            MathTex(r"\text{Row 1} \oplus \text{Row 2} \oplus \text{Row 3}",
                    font_size=22, color=GREEN_B),
            MathTex(r"= (1,1) \oplus (1,0) \oplus (0,1) = (0,0)",
                    font_size=22, color=RED),
            MathTex(r"\text{rank}_{\text{GF(2)}} = 2 \quad \text{(same)}", font_size=24,
                    color=GREEN),
        ).arrange(DOWN, buff=0.15)
        gf2_content2.move_to(gf2_box2.get_center())

        self.play(
            Create(real_box2), FadeIn(real_title2), FadeIn(real_content2),
            Create(gf2_box2), FadeIn(gf2_title2), FadeIn(gf2_content2),
            run_time=1.5
        )
        self.wait(1)

        # Punchline: when they differ
        self.play(
            *[FadeOut(m) for m in [real_box2, real_title2, real_content2,
                                    gf2_box2, gf2_title2, gf2_content2,
                                    matrix, mat_label, tricky_label]],
        )

        differ_title = Text("Critical: when ranks DISAGREE", font_size=24, color=RED)
        differ_title.next_to(title, DOWN, buff=0.3)
        self.play(FadeIn(differ_title))

        differ_example = VGroup(
            MathTex(r"v_1 = (1, 1),\quad v_2 = (1, 0),\quad v_3 = (0, 1)",
                    font_size=24),
            MathTex(r"\text{Over } \mathbb{R}: \text{rank} = 2 "
                    r"\text{ (only 2 columns, max rank is 2)}",
                    font_size=22, color=BLUE),
            MathTex(r"\text{Over GF(2): } v_1 = v_2 \oplus v_3, "
                    r"\text{ so rank} = 2",
                    font_size=22, color=GREEN),
            Text("With different vectors, float rank can say 'full rank'",
                 font_size=20, color=ORANGE),
            Text("when GF(2) rank is actually lower — leading to WRONG s!",
                 font_size=20, color=RED),
        ).arrange(DOWN, buff=0.2)
        differ_example.move_to(DOWN * 0.3)
        self.play(FadeIn(differ_example), run_time=1.5)
        self.wait(1)

        # Fix
        fix_box = Rectangle(width=10, height=1.2, color=GREEN, fill_opacity=0.1)
        fix_box.to_edge(DOWN, buff=0.2)
        fix_text = Text(
            "Fix: implement Gaussian elimination mod 2 (our _rank_gf2 function)\n"
            "Never use numpy.linalg.matrix_rank for GF(2) problems!",
            font_size=18, color=GREEN_B,
            line_spacing=1.3,
        )
        fix_text.move_to(fix_box.get_center())
        self.play(Create(fix_box), FadeIn(fix_text))
        self.wait(2)
