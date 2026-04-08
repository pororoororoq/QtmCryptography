#!/usr/bin/env python3
"""
Render all Manim animations for the presentation.

Usage:
    # Render all scenes at medium quality:
    python animations/render_all.py

    # Render a single scene:
    manim -qm animations/scene1_classical_vs_quantum.py ClassicalVsQuantumQuery

    # Render at high quality (1080p):
    manim -qh animations/scene1_classical_vs_quantum.py ClassicalVsQuantumQuery

    # Preview (low quality, opens viewer):
    manim -ql -p animations/scene1_classical_vs_quantum.py ClassicalVsQuantumQuery

Quality flags:
    -ql  = 480p (fast preview)
    -qm  = 720p (medium)
    -qh  = 1080p (high)
    -qk  = 4K (production)
"""

import subprocess
import sys

SCENES = [
    ("scene1_classical_vs_quantum.py", "ClassicalVsQuantumQuery"),
    ("scene2_xor_period_finding.py", "XORPeriodFinding"),
    ("scene3_simons_algorithm.py", "SimonsAlgorithmStepByStep"),
    ("scene4_even_mansour_attack.py", "EvenMansourAttack"),
    ("scene5_feistel_attack.py", "FeistelNetworkAttack"),
    ("scene6_slide_attack.py", "SlideAttackRoundIndependence"),
    ("scene7_gf2_vs_floatingpoint.py", "GF2VsFloatingPoint"),
    ("scene8_complexity_comparison.py", "ComplexityComparison"),
]


def main():
    quality = sys.argv[1] if len(sys.argv) > 1 else "-qm"

    for filename, scene_name in SCENES:
        filepath = f"animations/{filename}"
        print(f"\n{'='*60}")
        print(f"Rendering: {scene_name} ({filepath})")
        print(f"{'='*60}")

        cmd = ["manim", quality, filepath, scene_name]
        result = subprocess.run(cmd)

        if result.returncode != 0:
            print(f"FAILED: {scene_name}")
        else:
            print(f"OK: {scene_name}")

    print(f"\n{'='*60}")
    print("All renders complete. Output in media/ directory.")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
