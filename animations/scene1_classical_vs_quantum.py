"""
Scene 1: Classical vs Quantum Query

Visualizes the fundamental difference between classical and quantum
oracle access. A classical query sends ONE input and gets ONE output.
A quantum query sends a SUPERPOSITION of all inputs simultaneously.
"""

from manim import *


class ClassicalVsQuantumQuery(Scene):
    def construct(self):
        title = Text("Classical vs Quantum Oracle Access", font_size=40)
        title.to_edge(UP, buff=0.4)
        self.play(Write(title))
        self.wait(0.5)

        # ── Classical side ──
        classical_label = Text("Classical Query", font_size=28, color=BLUE)
        classical_label.move_to(LEFT * 3.5 + UP * 2)
        self.play(FadeIn(classical_label))

        # Oracle box
        c_oracle = Rectangle(width=2, height=1.2, color=BLUE)
        c_oracle.move_to(LEFT * 3.5)
        c_oracle_text = Text("Oracle", font_size=22, color=BLUE)
        c_oracle_text.move_to(c_oracle.get_center())
        self.play(Create(c_oracle), Write(c_oracle_text))

        # Single input arrow and label
        c_in_arrow = Arrow(LEFT * 5.5 + UP * 0.3, LEFT * 4.5 + UP * 0.3,
                           buff=0, color=BLUE_B)
        c_in_label = MathTex("x = 010", font_size=28, color=BLUE_B)
        c_in_label.next_to(c_in_arrow, UP, buff=0.1)

        # Single output arrow and label
        c_out_arrow = Arrow(LEFT * 2.5 + DOWN * 0.3, LEFT * 1.5 + DOWN * 0.3,
                            buff=0, color=BLUE_D)
        c_out_label = MathTex("f(010)", font_size=28, color=BLUE_D)
        c_out_label.next_to(c_out_arrow, DOWN, buff=0.1)

        self.play(
            GrowArrow(c_in_arrow), FadeIn(c_in_label),
        )
        self.wait(0.3)
        self.play(
            GrowArrow(c_out_arrow), FadeIn(c_out_label),
        )
        self.wait(0.5)

        # Emphasize: one at a time
        c_note = Text("One input at a time", font_size=20, color=BLUE)
        c_note.next_to(c_oracle, DOWN, buff=1.2)
        self.play(FadeIn(c_note))
        self.wait(0.5)

        # ── Quantum side ──
        quantum_label = Text("Quantum Query (Q2 model)", font_size=28, color=YELLOW)
        quantum_label.move_to(RIGHT * 3.5 + UP * 2)
        self.play(FadeIn(quantum_label))

        q_oracle = Rectangle(width=2, height=1.2, color=YELLOW)
        q_oracle.move_to(RIGHT * 3.5)
        q_oracle_text = Text("Oracle", font_size=22, color=YELLOW)
        q_oracle_text.move_to(q_oracle.get_center())
        self.play(Create(q_oracle), Write(q_oracle_text))

        # Superposition input — multiple values stacked
        superposition_inputs = VGroup()
        inputs = ["000", "001", "010", "011", "100", "101", "110", "111"]
        for i, inp in enumerate(inputs):
            t = MathTex(f"|{inp}\\rangle", font_size=18, color=YELLOW_B)
            t.move_to(RIGHT * 1.3 + UP * (0.7 - i * 0.2))
            superposition_inputs.add(t)

        brace_in = Brace(superposition_inputs, LEFT, buff=0.1, color=YELLOW_B)
        sup_label = MathTex(
            r"\sum_{x}|x\rangle",
            font_size=26, color=YELLOW_B
        )
        sup_label.next_to(brace_in, LEFT, buff=0.1)

        q_in_arrow = Arrow(
            RIGHT * 1.8 + ORIGIN, RIGHT * 2.5 + ORIGIN,
            buff=0, color=YELLOW_B
        )

        self.play(
            LaggedStart(*[FadeIn(t, shift=RIGHT * 0.3) for t in superposition_inputs],
                         lag_ratio=0.05),
            GrowFromCenter(brace_in),
            FadeIn(sup_label),
            GrowArrow(q_in_arrow),
        )
        self.wait(0.3)

        # Output superposition
        q_out_arrow = Arrow(RIGHT * 4.5 + ORIGIN, RIGHT * 5.2 + ORIGIN,
                            buff=0, color=YELLOW_D)
        q_out_label = MathTex(
            r"\sum_{x}|x\rangle|f(x)\rangle",
            font_size=24, color=YELLOW_D
        )
        q_out_label.next_to(q_out_arrow, RIGHT, buff=0.1)

        self.play(GrowArrow(q_out_arrow), FadeIn(q_out_label))

        q_note = Text("ALL inputs simultaneously!", font_size=20, color=YELLOW)
        q_note.next_to(q_oracle, DOWN, buff=1.2)
        self.play(FadeIn(q_note))
        self.wait(0.5)

        # ── Comparison callout ──
        divider = DashedLine(UP * 2.5, DOWN * 2.5, color=GRAY)
        self.play(Create(divider))

        box = SurroundingRectangle(
            VGroup(q_note),
            color=RED, buff=0.15
        )
        callout = Text(
            "This is the Q2 threat model:\nthe attacker queries the cipher\nin quantum superposition.",
            font_size=18, color=RED_B,
            line_spacing=1.2,
        )
        callout.to_edge(DOWN, buff=0.3)
        self.play(Create(box), FadeIn(callout))
        self.wait(2)
