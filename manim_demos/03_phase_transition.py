"""Cubic -> tetragonal phase transition in BaTiO3, with the simultaneous
(200) -> (200)/(002) XRD peak splitting shown in a side panel.

Left panel:
  Simplified 2D view of the perovskite unit cell.
  Ba at corners, Ti at center, O atoms omitted for clarity.
  As we cool through the Curie temperature (~120 C), the cubic cell
  (a = b = c) elongates along c (a = b < c).

Right panel:
  Zoomed 2theta axis (44 - 46 deg) showing the (200) and (002) Bragg peaks.
  Cu K-alpha (lambda = 1.5406 A); peak position 2theta = 2 arcsin(lambda / 2d).
  In the cubic phase (a = c = 4.00 A) we see one peak at ~45.1 deg.
  In the room-temperature tetragonal phase (a = 3.99 A, c = 4.036 A) the
  (200) shifts slightly higher in 2theta and the (002) shifts lower.

For visual clarity the unit-cell distortion is shown enlarged
(scale factor 5x). The peak positions on the right are computed at the
*true* lattice parameters at every frame.
"""
from manim import *
import numpy as np


LAMBDA = 1.5406            # Cu K-alpha, angstrom
A_LATTICE = 4.000          # cubic (and tetragonal a-axis), angstrom
C_LATTICE_TET = 4.040      # tetragonal c-axis at room temp, angstrom
DISTORTION_VISUAL_GAIN = 5.0  # exaggerate cell elongation 5x for visibility


def two_theta(d_angstrom: float) -> float:
    """Bragg's law in degrees, n=1, Cu Kalpha."""
    return 2.0 * np.degrees(np.arcsin(LAMBDA / (2.0 * d_angstrom)))


class PhaseTransition(Scene):
    def construct(self):
        # ---------- Title ----------
        title = Text(
            "BaTiO3: cubic -> tetragonal phase transition",
            font_size=28,
        ).to_edge(UP, buff=0.3)
        subtitle = Text(
            "Cell distortion (left) shifts the (200) Bragg peak (right)",
            font_size=18, color=GREY,
        ).next_to(title, DOWN, buff=0.1)
        self.play(Write(title), Write(subtitle))

        # ---------- Left panel: unit cell ----------
        # ValueTracker: t in [0, 1]; t=0 cubic, t=1 fully tetragonal.
        t = ValueTracker(0.0)

        cell_center = LEFT * 3.5
        a_visual = 1.5      # base side length in scene units

        def cell_size():
            tt = t.get_value()
            c_over_a = 1.0 + tt * (C_LATTICE_TET / A_LATTICE - 1.0) * DISTORTION_VISUAL_GAIN
            return a_visual, a_visual * c_over_a

        def cell_corners():
            w, h = cell_size()
            return [
                cell_center + np.array([-w / 2, -h / 2, 0]),
                cell_center + np.array([+w / 2, -h / 2, 0]),
                cell_center + np.array([+w / 2, +h / 2, 0]),
                cell_center + np.array([-w / 2, +h / 2, 0]),
            ]

        # Cell outline
        cell_box = always_redraw(
            lambda: Polygon(*cell_corners(), color=WHITE, stroke_width=2)
        )

        # Ba at corners (large, blue), Ti at center (smaller, yellow)
        ba_atoms = always_redraw(lambda: VGroup(*[
            Dot(pt, radius=0.16, color=BLUE) for pt in cell_corners()
        ]))
        ti_atom = always_redraw(lambda: Dot(cell_center, radius=0.10, color=YELLOW))

        # Atom legend
        ba_legend = VGroup(
            Dot(radius=0.10, color=BLUE),
            Text("Ba", font_size=18),
        ).arrange(RIGHT, buff=0.15).next_to(cell_center, DOWN * 3 + LEFT * 0.7)
        ti_legend = VGroup(
            Dot(radius=0.07, color=YELLOW),
            Text("Ti", font_size=18),
        ).arrange(RIGHT, buff=0.15).next_to(ba_legend, RIGHT, buff=0.5)
        legend_note = Text("(O atoms omitted for clarity)",
                           font_size=14, color=GREY).next_to(ba_legend, DOWN, buff=0.1)

        # Live readout of c/a
        ratio_label = always_redraw(lambda: MathTex(
            rf"c/a = {1.0 + t.get_value() * (C_LATTICE_TET / A_LATTICE - 1.0):.4f}",
            font_size=24,
        ).next_to(cell_center, UP * 2.3))

        # Live a, c values (real, not visual)
        ac_label = always_redraw(lambda: MathTex(
            rf"a = {A_LATTICE:.3f}\,\text{{\AA}},"
            rf"\quad c = {A_LATTICE + t.get_value() * (C_LATTICE_TET - A_LATTICE):.3f}\,\text{{\AA}}",
            font_size=20, color=GREY,
        ).next_to(ratio_label, UP, buff=0.2))

        self.play(Create(cell_box), FadeIn(ba_atoms), FadeIn(ti_atom),
                  FadeIn(ba_legend), FadeIn(ti_legend), FadeIn(legend_note),
                  Write(ratio_label), Write(ac_label))

        # ---------- Right panel: Bragg peaks ----------
        axes_origin = RIGHT * 2.5 + DOWN * 0.5
        axes = Axes(
            x_range=[44, 46, 0.5],
            y_range=[0, 1.2, 0.5],
            x_length=4.5,
            y_length=3.5,
            tips=False,
            axis_config={"color": GREY, "stroke_width": 2,
                         "include_numbers": False},
        ).move_to(axes_origin)
        x_label = MathTex(r"2\theta\,(\text{deg})", font_size=22).next_to(
            axes.x_axis, DOWN, buff=0.2)
        y_label = MathTex(r"I", font_size=22).next_to(axes.y_axis, LEFT, buff=0.2)

        # x-axis tick labels
        x_ticks = VGroup(*[
            MathTex(f"{x:.0f}", font_size=18).next_to(axes.c2p(x, 0), DOWN, buff=0.1)
            for x in [44, 45, 46]
        ])

        self.play(Create(axes), Write(x_label), Write(y_label), Write(x_ticks))

        # Live diffraction pattern: sum of two Lorentzians at (200) and (002) positions
        FWHM = 0.06   # peak width in 2theta degrees

        def pattern_curve():
            tt = t.get_value()
            a = A_LATTICE
            c = a + tt * (C_LATTICE_TET - a)
            two_theta_200 = two_theta(a / 2.0)   # d_(200) = a/2
            two_theta_002 = two_theta(c / 2.0)   # d_(002) = c/2

            def lorentz(x, x0, w):
                return (w / 2)**2 / ((x - x0)**2 + (w / 2)**2)

            def y(x):
                return min(1.0, lorentz(x, two_theta_200, FWHM) +
                                lorentz(x, two_theta_002, FWHM))

            return axes.plot(y, x_range=[44, 46, 0.005], color=ORANGE,
                             stroke_width=3)

        pattern = always_redraw(pattern_curve)

        # Peak labels (also live)
        def peak_labels():
            tt = t.get_value()
            a = A_LATTICE
            c = a + tt * (C_LATTICE_TET - a)
            tt200 = two_theta(a / 2.0)
            tt002 = two_theta(c / 2.0)
            split = abs(tt200 - tt002)
            if split < 0.05:
                return VGroup(
                    MathTex(r"(200)", font_size=20, color=ORANGE).next_to(
                        axes.c2p(tt200, 1.05), UP, buff=0.05)
                )
            return VGroup(
                MathTex(r"(200)", font_size=20, color=ORANGE).next_to(
                    axes.c2p(tt200, 1.05), UR, buff=0.05),
                MathTex(r"(002)", font_size=20, color=ORANGE).next_to(
                    axes.c2p(tt002, 1.05), UL, buff=0.05),
            )
        labels_live = always_redraw(peak_labels)

        self.play(Create(pattern), FadeIn(labels_live))
        self.wait(0.6)

        cubic_caption = Text("Cubic phase (T > 120 C):  one peak",
                             font_size=22, color=BLUE).to_edge(DOWN, buff=0.6)
        self.play(Write(cubic_caption))
        self.wait(1.0)

        # ---------- The transition itself ----------
        new_caption = Text("Cooling through Tc:  cell elongates, peak splits",
                           font_size=22, color=YELLOW).to_edge(DOWN, buff=0.6)
        self.play(Transform(cubic_caption, new_caption))
        self.play(t.animate.set_value(1.0), run_time=4.5, rate_func=smooth)
        self.wait(0.5)

        final_caption = Text("Tetragonal phase (T < 120 C):  (200) and (002) split",
                             font_size=22, color=ORANGE).to_edge(DOWN, buff=0.6)
        self.play(Transform(cubic_caption, final_caption))
        self.wait(2.0)
