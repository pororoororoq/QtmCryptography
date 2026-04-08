"""
Scene 3: Simon's Algorithm Step-by-Step

Walks through the full quantum circuit pipeline:
  1. Initialize |0...0>|0...0>
  2. Apply Hadamard to input register -> uniform superposition
  3. Query the oracle -> entangle input/output
  4. Measure the output register -> collapse to a pair {x, x XOR s}
  5. Apply Hadamard to input register -> interference
  6. Measure input register -> get y such that y . s = 0
  7. Repeat O(n) times, solve linear system over GF(2)
"""

from manim import *


class SimonsAlgorithmStepByStep(Scene):
    def construct(self):
        title = Text("Simon's Algorithm: Step by Step", font_size=38)
        title.to_edge(UP, buff=0.3)
        self.play(Write(title))

        # ── Build the circuit diagram ──
        # We'll show a 3-qubit example (n=3)
        n = 3
        wire_y = [1.2 - i * 0.5 for i in range(2 * n)]
        wire_start_x = -5.5
        wire_end_x = 5.5

        wires = VGroup()
        wire_labels = VGroup()
        for i in range(2 * n):
            wire = Line(
                [wire_start_x, wire_y[i], 0],
                [wire_end_x, wire_y[i], 0],
                color=GRAY, stroke_width=1.5
            )
            wires.add(wire)

            if i < n:
                label = MathTex(f"|0\\rangle", font_size=22, color=BLUE)
            else:
                label = MathTex(f"|0\\rangle", font_size=22, color=GREEN)
            label.next_to(wire, LEFT, buff=0.1)
            wire_labels.add(label)

        # Register labels
        input_brace = Brace(
            VGroup(*[wire_labels[i] for i in range(n)]),
            LEFT, buff=0.3, color=BLUE
        )
        input_label = Text("input", font_size=18, color=BLUE)
        input_label.next_to(input_brace, LEFT, buff=0.1)

        output_brace = Brace(
            VGroup(*[wire_labels[i] for i in range(n, 2 * n)]),
            LEFT, buff=0.3, color=GREEN
        )
        output_label = Text("output", font_size=18, color=GREEN)
        output_label.next_to(output_brace, LEFT, buff=0.1)

        self.play(
            *[Create(w) for w in wires],
            *[FadeIn(l) for l in wire_labels],
            GrowFromCenter(input_brace), FadeIn(input_label),
            GrowFromCenter(output_brace), FadeIn(output_label),
            run_time=1.5
        )

        # Gate positions
        h1_x = -3.5
        oracle_x = -0.5
        h2_x = 2.5
        meas_x = 4.5

        # ── Step 1: Hadamard on input register ──
        step1_text = Text("Step 1: Hadamard", font_size=20, color=BLUE)
        step1_text.to_edge(DOWN, buff=0.3)

        h_gates = VGroup()
        for i in range(n):
            h_box = Square(side_length=0.4, color=BLUE, fill_opacity=0.2)
            h_box.move_to([h1_x, wire_y[i], 0])
            h_text = MathTex("H", font_size=20, color=BLUE)
            h_text.move_to(h_box.get_center())
            h_gates.add(VGroup(h_box, h_text))

        self.play(
            *[FadeIn(g) for g in h_gates],
            FadeIn(step1_text),
            run_time=0.8
        )

        state1 = MathTex(
            r"\frac{1}{\sqrt{8}} \sum_{x=0}^{7} |x\rangle|0\rangle",
            font_size=22, color=BLUE_B
        )
        state1.next_to(step1_text, UP, buff=0.15)
        self.play(FadeIn(state1))
        self.wait(1)
        self.play(FadeOut(state1), FadeOut(step1_text))

        # ── Step 2: Oracle query ──
        step2_text = Text("Step 2: Query oracle (all x at once!)",
                          font_size=20, color=YELLOW)
        step2_text.to_edge(DOWN, buff=0.3)

        oracle_box = Rectangle(width=1.2, height=3.2, color=YELLOW,
                               fill_opacity=0.15)
        oracle_box.move_to([oracle_x, np.mean(wire_y), 0])
        oracle_label = MathTex("U_f", font_size=26, color=YELLOW)
        oracle_label.move_to(oracle_box.get_center())

        self.play(
            FadeIn(oracle_box), FadeIn(oracle_label),
            FadeIn(step2_text),
            run_time=0.8
        )

        state2 = MathTex(
            r"\frac{1}{\sqrt{8}} \sum_{x} |x\rangle|f(x)\rangle",
            font_size=22, color=YELLOW_B
        )
        state2.next_to(step2_text, UP, buff=0.15)
        self.play(FadeIn(state2))
        self.wait(1)
        self.play(FadeOut(state2), FadeOut(step2_text))

        # ── Step 3: Measure output register ──
        step3_text = Text("Step 3: Measure output -> collapses to pair",
                          font_size=20, color=GREEN)
        step3_text.to_edge(DOWN, buff=0.3)

        meas_output = VGroup()
        for i in range(n, 2 * n):
            m_box = Square(side_length=0.35, color=GREEN, fill_opacity=0.2)
            m_box.move_to([h2_x - 0.7, wire_y[i], 0])
            m_icon = MathTex(r"\measuredangle", font_size=18, color=GREEN)
            m_icon.move_to(m_box.get_center())
            meas_output.add(VGroup(m_box, m_icon))

        self.play(
            *[FadeIn(m) for m in meas_output],
            FadeIn(step3_text),
            run_time=0.8
        )

        state3 = MathTex(
            r"\frac{1}{\sqrt{2}} \big(|x_0\rangle + |x_0 \oplus s\rangle\big)",
            font_size=22, color=GREEN_B
        )
        state3.next_to(step3_text, UP, buff=0.15)
        self.play(FadeIn(state3))
        self.wait(1)
        self.play(FadeOut(state3), FadeOut(step3_text))

        # ── Step 4: Second Hadamard on input register ──
        step4_text = Text("Step 4: Hadamard again -> interference",
                          font_size=20, color=PURPLE)
        step4_text.to_edge(DOWN, buff=0.3)

        h2_gates = VGroup()
        for i in range(n):
            h_box = Square(side_length=0.4, color=PURPLE, fill_opacity=0.2)
            h_box.move_to([h2_x, wire_y[i], 0])
            h_text = MathTex("H", font_size=20, color=PURPLE)
            h_text.move_to(h_box.get_center())
            h2_gates.add(VGroup(h_box, h_text))

        self.play(
            *[FadeIn(g) for g in h2_gates],
            FadeIn(step4_text),
            run_time=0.8
        )
        self.wait(0.5)

        # ── Step 5: Measure -> get y with y . s = 0 ──
        step5_text = Text("Step 5: Measure -> get y where y . s = 0 (mod 2)",
                          font_size=20, color=RED)
        step5_text.to_edge(DOWN, buff=0.3)
        self.play(FadeOut(step4_text), FadeIn(step5_text))

        meas_input = VGroup()
        for i in range(n):
            m_box = Square(side_length=0.35, color=RED, fill_opacity=0.2)
            m_box.move_to([meas_x, wire_y[i], 0])
            m_icon = MathTex(r"\measuredangle", font_size=18, color=RED)
            m_icon.move_to(m_box.get_center())
            meas_input.add(VGroup(m_box, m_icon))

        self.play(*[FadeIn(m) for m in meas_input], run_time=0.8)

        # Show the constraint
        constraint = MathTex(
            r"y \cdot s = y_1 s_1 \oplus y_2 s_2 \oplus y_3 s_3 = 0",
            font_size=24, color=RED_B
        )
        constraint.next_to(step5_text, UP, buff=0.15)
        self.play(FadeIn(constraint))
        self.wait(1)

        self.play(FadeOut(constraint), FadeOut(step5_text))

        # ── Step 6: Repeat and solve ──
        repeat_text = Text(
            "Repeat O(n) times, collect n-1 independent equations,\n"
            "solve linear system over GF(2) to find s.",
            font_size=20, color=WHITE,
            line_spacing=1.3,
        )
        repeat_text.to_edge(DOWN, buff=0.3)
        self.play(FadeIn(repeat_text))

        # Show sample system
        system = MathTex(
            r"\begin{pmatrix} 1 & 0 & 1 \\ 0 & 1 & 1 \end{pmatrix}"
            r"\begin{pmatrix} s_1 \\ s_2 \\ s_3 \end{pmatrix}"
            r"= \begin{pmatrix} 0 \\ 0 \end{pmatrix}",
            font_size=26, color=ORANGE
        )
        system.move_to(DOWN * 1.5)
        self.play(FadeIn(system))

        solution = MathTex(
            r"\Rightarrow s = 110",
            font_size=30, color=YELLOW
        )
        solution.next_to(system, RIGHT, buff=0.5)
        self.play(FadeIn(solution))
        self.wait(2)
