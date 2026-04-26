"""Ewald sphere construction (in 2D — the Ewald CIRCLE for clarity).

Setup:
  - Reciprocal lattice: integer-spaced grid of points centered on origin O.
  - Ewald circle: radius R = 1/lambda, centered at C = -R*x_hat (so the
    direct beam exits the sphere at the origin O = (0,0)).
  - The diffraction condition is that a reciprocal-lattice point lies
    exactly on the circle. As the crystal rotates, lattice points sweep
    across the circle, and at the instant a point touches the circle,
    that reflection diffracts.

We use lambda such that R = 2.0 in scene units, so the sphere encloses
several lattice points and the geometry is clearly visible.
"""
from manim import *
import numpy as np


R = 2.0                    # Ewald circle radius (= 1/lambda in scene units)
LATTICE_RANGE = 3          # reciprocal-lattice points in each direction
DOT_RADIUS = 0.07
ROTATIONS = 2 * PI         # how far to rotate the crystal
RUN_TIME = 8.0


class Ewald(Scene):
    def construct(self):
        # ---------- Title ----------
        title = Text("Ewald Sphere Construction (2D view)",
                     font_size=30).to_edge(UP)
        self.play(Write(title))

        # ---------- Reciprocal lattice ----------
        lattice_points = VGroup(*[
            Dot([h, k, 0], radius=DOT_RADIUS, color=BLUE)
            for h in range(-LATTICE_RANGE, LATTICE_RANGE + 1)
            for k in range(-LATTICE_RANGE, LATTICE_RANGE + 1)
        ])
        # The (0,0) point — direct beam — gets a special color
        for d in lattice_points:
            if np.allclose(d.get_center()[:2], [0, 0]):
                d.set_color(WHITE)
                d.scale(1.3)

        lattice_label = Text("Reciprocal lattice", font_size=20,
                             color=BLUE).to_corner(UR).shift(0.3 * DOWN)

        # ---------- Ewald circle ----------
        center_C = np.array([-R, 0, 0])
        ewald = Circle(radius=R, color=YELLOW).move_to(center_C)
        center_dot = Dot(center_C, radius=0.06, color=YELLOW)
        center_label = MathTex("C", font_size=24,
                               color=YELLOW).next_to(center_dot, LEFT, buff=0.1)

        # ---------- Incoming wavevector k_in: from C to origin O ----------
        k_in = Arrow(center_C, ORIGIN, color=GREEN, buff=0,
                     stroke_width=4, max_tip_length_to_length_ratio=0.08)
        k_in_label = MathTex(r"\vec{k}_{\rm in}", font_size=28,
                             color=GREEN).next_to(k_in.get_center(), DOWN, buff=0.15)

        origin_label = MathTex("O", font_size=24, color=WHITE).next_to(
            [0, 0, 0], DR, buff=0.1)

        # ---------- Build the static scene ----------
        self.play(FadeIn(lattice_points), Write(lattice_label))
        self.play(Create(ewald), FadeIn(center_dot), Write(center_label),
                  Write(origin_label))
        self.play(GrowArrow(k_in), Write(k_in_label))
        self.wait(0.5)

        bragg_text = Text(
            "Diffraction condition: a reciprocal point lies on the circle.",
            font_size=22, color=YELLOW
        ).to_edge(DOWN, buff=0.4)
        self.play(Write(bragg_text))
        self.wait(0.8)

        # ---------- Rotate the crystal ----------
        # Build a tracker for rotation and a group of "live" lattice points
        # that we can rotate around the origin.
        live_points = VGroup(*[
            Dot([h, k, 0], radius=DOT_RADIUS, color=BLUE)
            for h in range(-LATTICE_RANGE, LATTICE_RANGE + 1)
            for k in range(-LATTICE_RANGE, LATTICE_RANGE + 1)
            if not (h == 0 and k == 0)
        ])

        # Replace the static lattice points with live ones (origin stays fixed)
        self.remove(lattice_points)
        self.add(live_points)
        # Re-add the origin point on top
        origin_dot = Dot(ORIGIN, radius=DOT_RADIUS * 1.3, color=WHITE)
        self.add(origin_dot, origin_label)

        # Highlights — outgoing wavevector arrow + glow when a point hits the circle
        k_out = always_redraw(lambda: Arrow(
            center_C, _nearest_on_circle_point(live_points, center_C, R),
            color=RED, buff=0, stroke_width=4,
            max_tip_length_to_length_ratio=0.08,
        ))
        k_out_label = MathTex(r"\vec{k}_{\rm out}", font_size=28,
                              color=RED).next_to(k_in_label, RIGHT, buff=0.5)

        diffraction_dot = always_redraw(lambda: Dot(
            _nearest_on_circle_point(live_points, center_C, R),
            radius=0.16, color=RED).set_opacity(
                _proximity_opacity(live_points, center_C, R)
            )
        )

        self.add(k_out, k_out_label, diffraction_dot)
        self.play(Rotate(live_points, angle=ROTATIONS, about_point=ORIGIN),
                  run_time=RUN_TIME, rate_func=linear)
        self.wait(0.5)


def _nearest_on_circle_point(group, center, radius):
    """Return the (3D) coordinate of the lattice point closest to lying on
    the Ewald circle. Used to visualise k_out as it sweeps."""
    best = None
    best_err = 1e9
    cx, cy, _ = center
    for d in group:
        x, y, _ = d.get_center()
        err = abs(np.hypot(x - cx, y - cy) - radius)
        if err < best_err:
            best_err = err
            best = d.get_center().copy()
    return best if best is not None else np.array([0, 0, 0])


def _proximity_opacity(group, center, radius, sigma=0.1):
    """Opacity that peaks (1.0) when *any* lattice point sits on the Ewald
    circle and falls off otherwise. Drives the red 'diffraction!' flash."""
    cx, cy, _ = center
    best_err = 1e9
    for d in group:
        x, y, _ = d.get_center()
        err = abs(np.hypot(x - cx, y - cy) - radius)
        best_err = min(best_err, err)
    return float(np.exp(-(best_err / sigma) ** 2))
