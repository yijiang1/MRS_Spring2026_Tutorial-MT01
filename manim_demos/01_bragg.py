"""Bragg's law animation.

Two parallel atomic planes spaced d apart. Two parallel X-rays incident at
angle theta scatter elastically off the planes. The lower ray travels an
extra path length 2 d sin(theta). When that equals n*lambda, the rays
interfere constructively (Bragg condition) and a diffraction peak appears.

Numerical setup uses d = 2.0 scene units, lambda = 1.5 scene units (Cu Kα
analog), so the n=1 Bragg angle is asin(0.375) = 22.0 degrees.
"""
from manim import *
import numpy as np


D_SPACING = 2.0          # spacing between planes (scene units)
WAVELENGTH = 1.5         # X-ray wavelength (scene units)
N_ATOMS = 7              # atoms per plane


class Bragg(Scene):
    def construct(self):
        # ---------- Title ----------
        title = Text("Bragg's Law of X-ray Diffraction", font_size=32).to_edge(UP)
        self.play(Write(title))

        # ---------- Two atomic planes ----------
        plane_y_top = 0.5
        plane_y_bot = plane_y_top - D_SPACING
        x_positions = np.linspace(-4, 4, N_ATOMS)

        atoms_top = VGroup(*[
            Dot([x, plane_y_top, 0], radius=0.10, color=BLUE)
            for x in x_positions
        ])
        atoms_bot = VGroup(*[
            Dot([x, plane_y_bot, 0], radius=0.10, color=BLUE)
            for x in x_positions
        ])
        line_top = Line([-5, plane_y_top, 0], [5, plane_y_top, 0],
                        color=GREY, stroke_width=1).set_opacity(0.4)
        line_bot = Line([-5, plane_y_bot, 0], [5, plane_y_bot, 0],
                        color=GREY, stroke_width=1).set_opacity(0.4)

        # d-spacing label
        d_brace = BraceBetweenPoints([4.5, plane_y_top, 0],
                                     [4.5, plane_y_bot, 0], direction=RIGHT)
        d_label = MathTex("d", font_size=36).next_to(d_brace, RIGHT, buff=0.1)

        self.play(Create(line_top), Create(line_bot),
                  FadeIn(atoms_top), FadeIn(atoms_bot))
        self.play(GrowFromCenter(d_brace), Write(d_label))

        # ---------- Bragg geometry at the n=1 Bragg angle ----------
        theta = np.arcsin(WAVELENGTH / (2 * D_SPACING))   # n=1 condition
        theta_deg = np.degrees(theta)

        # Reflection points on each plane (chosen so rays are parallel & visible)
        x_top = -1.0
        x_bot = x_top + D_SPACING / np.tan(theta)         # geometry: along beam direction
        ref_top = np.array([x_top, plane_y_top, 0])
        ref_bot = np.array([x_bot, plane_y_bot, 0])

        # Direction vectors
        in_dir  = np.array([np.cos(theta), -np.sin(theta), 0])    # incoming (left-to-right, downward)
        out_dir = np.array([np.cos(theta),  np.sin(theta), 0])    # specular reflection (upward)

        # Far ends of the rays
        ray1_in  = Arrow(ref_top - 4 * in_dir,  ref_top, color=YELLOW, buff=0,
                         stroke_width=4, max_tip_length_to_length_ratio=0.05)
        ray1_out = Arrow(ref_top, ref_top + 4 * out_dir, color=YELLOW, buff=0,
                         stroke_width=4, max_tip_length_to_length_ratio=0.05)
        ray2_in  = Arrow(ref_bot - 4 * in_dir,  ref_bot, color=ORANGE, buff=0,
                         stroke_width=4, max_tip_length_to_length_ratio=0.05)
        ray2_out = Arrow(ref_bot, ref_bot + 4 * out_dir, color=ORANGE, buff=0,
                         stroke_width=4, max_tip_length_to_length_ratio=0.05)

        # Theta angle markers between the planes and the rays
        angle_in  = Angle(line_top, Line(ref_top, ref_top - 2 * in_dir),
                          radius=0.5, other_angle=False, color=WHITE)
        angle_in_label = MathTex(r"\theta", font_size=28).move_to(
            ref_top + 0.7 * (np.array([-np.cos(theta/2), -np.sin(theta/2), 0])))
        # Position the label inside the angle wedge
        angle_in_label.move_to(ref_top + 0.85 * np.array([-np.cos(theta/2),
                                                          np.sin(-theta/2), 0]))

        self.play(GrowArrow(ray1_in), GrowArrow(ray2_in))
        self.play(Create(angle_in), Write(angle_in_label))
        self.wait(0.3)
        self.play(GrowArrow(ray1_out), GrowArrow(ray2_out))

        # ---------- Highlight the path-length difference ----------
        # The extra path = 2 d sin(theta).
        # Geometrically: from ref_top, drop perpendiculars onto ray2_in and ray2_out
        # at the start and end of the lower ray's "extra" portion.
        # Project ref_top onto ray2_in:
        v_in_perp_start = ref_bot + np.dot(ref_top - ref_bot, in_dir) * in_dir
        # Project ref_top onto ray2_out:
        v_out_perp_end  = ref_bot + np.dot(ref_top - ref_bot, out_dir) * out_dir

        # The extra distance is from v_in_perp_start to ref_bot,
        # plus from ref_bot to v_out_perp_end. Each = d sin(theta).
        extra_in  = Line(v_in_perp_start, ref_bot, color=RED, stroke_width=8)
        extra_out = Line(ref_bot, v_out_perp_end, color=RED, stroke_width=8)

        # Faint perpendicular construction lines from ref_top to each foot
        perp_in  = DashedLine(ref_top, v_in_perp_start, color=WHITE,
                              stroke_width=2).set_opacity(0.6)
        perp_out = DashedLine(ref_top, v_out_perp_end, color=WHITE,
                              stroke_width=2).set_opacity(0.6)

        self.play(Create(perp_in), Create(perp_out))
        self.play(Create(extra_in), Create(extra_out))

        path_diff_label = MathTex(r"\text{extra path} = 2 d \sin\theta",
                                  font_size=32, color=RED).to_edge(DOWN, buff=1.0)
        self.play(Write(path_diff_label))
        self.wait(1.0)

        # ---------- Bragg condition ----------
        bragg = MathTex(r"n\,\lambda = 2 d \sin\theta",
                        font_size=44).to_edge(DOWN, buff=0.3)
        self.play(Transform(path_diff_label, bragg))
        self.wait(1.5)

        # ---------- Show the actual angle ----------
        theta_value = MathTex(
            rf"\theta = \arcsin\!\left(\frac{{n\lambda}}{{2d}}\right) = "
            rf"{theta_deg:.1f}^\circ",
            font_size=32).next_to(title, DOWN, buff=0.2)
        self.play(Write(theta_value))
        self.wait(2.0)
