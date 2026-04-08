"""
Scene 2: XOR and Period Finding

Shows how XOR creates paired inputs that map to the same output,
which is the core structure Simon's algorithm exploits.
For a function f with period s: f(x) = f(x XOR s) for all x.
"""

from manim import *


class XORPeriodFinding(Scene):
    def construct(self):
        title = Text("XOR Creates Hidden Pairs", font_size=40)
        title.to_edge(UP, buff=0.4)
        self.play(Write(title))
        self.wait(0.5)

        # ── Step 1: What is XOR? ──
        xor_title = Text("XOR (exclusive or): flip bits where s has a 1",
                         font_size=24, color=BLUE)
        xor_title.next_to(title, DOWN, buff=0.4)
        self.play(FadeIn(xor_title))

        # XOR example
        example = VGroup(
            MathTex(r"x   = 0 1 0", font_size=32),
            MathTex(r"s   = 1 1 0", font_size=32, color=YELLOW),
            Line(LEFT * 1.2, RIGHT * 1.2, color=GRAY),
            MathTex(r"x \oplus s = 1 0 0", font_size=32, color=GREEN),
        ).arrange(DOWN, buff=0.15)
        example.move_to(UP * 0.5)

        self.play(LaggedStart(*[FadeIn(e) for e in example], lag_ratio=0.3))
        self.wait(1)

        # XOR property
        prop = MathTex(
            r"(x \oplus s) \oplus s = x",
            font_size=30, color=ORANGE
        )
        prop_note = Text("XOR is its own inverse!", font_size=20, color=ORANGE)
        prop_group = VGroup(prop, prop_note).arrange(DOWN, buff=0.1)
        prop_group.next_to(example, DOWN, buff=0.5)
        self.play(FadeIn(prop_group))
        self.wait(1)

        # Fade step 1
        self.play(FadeOut(VGroup(xor_title, example, prop_group)))

        # ── Step 2: Simon's period structure ──
        period_title = Text("Period s = 110: every input is paired",
                            font_size=26, color=YELLOW)
        period_title.next_to(title, DOWN, buff=0.4)
        self.play(FadeIn(period_title))

        # Show the pairing table
        # For s = 110 (= 6), the pairs in 3-bit space:
        # 000 <-> 110, 001 <-> 111, 010 <-> 100, 011 <-> 101
        pairs = [
            ("000", "110"),
            ("001", "111"),
            ("010", "100"),
            ("011", "101"),
        ]
        colors = [RED, GREEN, BLUE, PURPLE]

        # Left column: inputs
        left_col_header = Text("x", font_size=26, color=WHITE)
        right_col_header = MathTex(r"x \oplus s", font_size=26, color=YELLOW)
        output_header = Text("f(x)", font_size=26, color=WHITE)

        table_entries = VGroup()
        for i, ((a, b), col) in enumerate(zip(pairs, colors)):
            row = VGroup(
                MathTex(a, font_size=28, color=col),
                MathTex(r"\longleftrightarrow", font_size=24, color=GRAY),
                MathTex(b, font_size=28, color=col),
                MathTex(r"\rightarrow", font_size=24, color=GRAY),
                MathTex(f"y_{i}", font_size=28, color=col),
            ).arrange(RIGHT, buff=0.3)
            table_entries.add(row)

        table_entries.arrange(DOWN, buff=0.25)
        table_entries.move_to(DOWN * 0.3)

        # Headers
        left_col_header.next_to(table_entries[0][0], UP, buff=0.4)
        right_col_header.next_to(table_entries[0][2], UP, buff=0.4)
        output_header.next_to(table_entries[0][4], UP, buff=0.4)

        self.play(
            FadeIn(left_col_header),
            FadeIn(right_col_header),
            FadeIn(output_header),
        )
        for row in table_entries:
            self.play(FadeIn(row), run_time=0.5)
        self.wait(0.5)

        # Highlight: each pair maps to the SAME output
        same_output_note = Text(
            "Each pair maps to the SAME output  -->  f is 2-to-1",
            font_size=22, color=YELLOW
        )
        same_output_note.next_to(table_entries, DOWN, buff=0.5)
        self.play(FadeIn(same_output_note))
        self.wait(1)

        # ── Step 3: This is what Simon's algorithm finds ──
        goal_box = Rectangle(width=8, height=1.2, color=RED, fill_opacity=0.1)
        goal_box.to_edge(DOWN, buff=0.3)
        goal_text = Text(
            "Simon's algorithm recovers s from this 2-to-1 structure\n"
            "using only O(n) quantum queries!",
            font_size=20, color=RED_B,
            line_spacing=1.3,
        )
        goal_text.move_to(goal_box.get_center())
        self.play(Create(goal_box), FadeIn(goal_text))
        self.wait(2)
