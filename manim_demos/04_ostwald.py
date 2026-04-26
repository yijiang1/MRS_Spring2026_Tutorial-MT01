"""Nucleation and Ostwald ripening.

Many small spherical particles in a fixed volume of solute. Each particle
exchanges atoms with the solute according to the Gibbs-Thomson driving
force: small particles have higher chemical potential (mu ~ 1/r), so they
shed atoms; large particles capture them. The result, observed by Ostwald
in 1896, is that the size distribution shifts to the right and the number
of particles decreases — *coarsening*.

The simplest quantitative model is LSW theory (Lifshitz-Slyozov-Wagner):
    dr_i/dt = K * (1/<r> - 1/r_i)
where <r> is the critical radius (here approximated by the volume-weighted
mean). Particles whose radius drops to zero dissolve.

We integrate this on a small population of ~30 particles and animate the
result with Manim. Mass is conserved by construction: the rate of total
volume change is zero on average over LSW dynamics, but for a finite
population we apply a tiny rescaling each step to keep total volume exact.
"""
from manim import *
import numpy as np


N_PARTICLES = 30
BOX_HALF = 3.0          # half-size of the simulation box (scene units)
R_INITIAL_MEAN = 0.18   # initial mean radius
R_INITIAL_STD = 0.06
N_FRAMES = 60           # number of timesteps to precompute
DT = 0.04               # timestep
K_LSW = 0.005           # diffusion-limited rate constant
SEED = 1


def simulate(seed=SEED):
    """Pre-compute particle positions and radii over time.

    Returns: list of (positions[N,2], radii[N]) snapshots, one per frame.
    Particles that dissolve get radius 0 (kept in the array for indexing
    stability; the renderer hides them)."""
    rng = np.random.default_rng(seed)

    # ---- Initial positions (rejection sampling for non-overlap) ----
    radii = np.clip(
        rng.normal(R_INITIAL_MEAN, R_INITIAL_STD, size=N_PARTICLES),
        0.06, 0.35,
    )
    positions = np.zeros((N_PARTICLES, 2))
    for i in range(N_PARTICLES):
        for _ in range(2000):
            xy = rng.uniform(-BOX_HALF + radii[i] + 0.05,
                              BOX_HALF - radii[i] - 0.05, size=2)
            ok = True
            for j in range(i):
                if radii[j] == 0:
                    continue
                if np.hypot(*(xy - positions[j])) < radii[i] + radii[j] + 0.05:
                    ok = False; break
            if ok:
                positions[i] = xy
                break

    snapshots = [(positions.copy(), radii.copy())]
    initial_volume = np.sum(radii ** 3)

    for _ in range(N_FRAMES):
        alive = radii > 0
        if alive.sum() == 0:
            break
        # Volume-weighted mean radius is the natural critical radius
        r_alive = radii[alive]
        r_crit = np.sum(r_alive ** 3) / np.sum(r_alive ** 2)

        dr = np.zeros_like(radii)
        dr[alive] = K_LSW * (1.0 / r_crit - 1.0 / r_alive)

        radii = radii + DT * dr
        radii = np.where(radii < 0.04, 0.0, radii)

        # Enforce mass conservation by tiny rescaling (numerical safety)
        cur_vol = np.sum(radii ** 3)
        if cur_vol > 0:
            radii = radii * (initial_volume / cur_vol) ** (1 / 3)

        snapshots.append((positions.copy(), radii.copy()))

    return snapshots


SNAPSHOTS = simulate()


class Ostwald(Scene):
    def construct(self):
        # ---------- Title ----------
        title = Text("Ostwald ripening: large particles eat small ones",
                     font_size=26).to_edge(UP, buff=0.3)
        subtitle = MathTex(
            r"\frac{dr_i}{dt} = K\left(\frac{1}{\langle r\rangle} - \frac{1}{r_i}\right)"
            r"\quad \text{(LSW theory)}",
            font_size=22, color=GREY,
        ).next_to(title, DOWN, buff=0.15)
        self.play(Write(title), Write(subtitle))

        # ---------- Box outline ----------
        box = Square(side_length=2 * BOX_HALF, color=GREY,
                     stroke_width=2).shift(LEFT * 2.5)
        box_offset = LEFT * 2.5
        self.play(Create(box))

        # ---------- Particles ----------
        positions, radii = SNAPSHOTS[0]
        circles = []
        for i in range(N_PARTICLES):
            c = Circle(radius=radii[i], color=BLUE_E, fill_opacity=0.7,
                       stroke_color=BLUE_A, stroke_width=1.5).move_to(
                np.array([positions[i, 0], positions[i, 1], 0]) + box_offset)
            circles.append(c)
        circle_group = VGroup(*circles)
        self.play(FadeIn(circle_group))

        # ---------- Side panel: histogram of radii ----------
        hist_axes = Axes(
            x_range=[0, 0.5, 0.1],
            y_range=[0, 12, 4],
            x_length=4.2,
            y_length=3.2,
            tips=False,
            axis_config={"color": GREY, "stroke_width": 2,
                         "include_numbers": False},
        ).shift(RIGHT * 3.5 + DOWN * 0.3)
        hist_x_label = MathTex(r"r", font_size=20).next_to(hist_axes.x_axis, DOWN)
        hist_y_label = MathTex(r"\#\,\text{particles}", font_size=18).next_to(
            hist_axes.y_axis, LEFT)
        hist_title = Text("Size distribution", font_size=18).next_to(
            hist_axes, UP, buff=0.1)
        self.play(Create(hist_axes), Write(hist_x_label),
                  Write(hist_y_label), Write(hist_title))

        bin_edges = np.linspace(0, 0.5, 9)

        def histogram_bars(snap_radii):
            alive = snap_radii[snap_radii > 0]
            counts, _ = np.histogram(alive, bins=bin_edges)
            bars = VGroup()
            for cnt, lo, hi in zip(counts, bin_edges[:-1], bin_edges[1:]):
                if cnt == 0:
                    continue
                bottom_left  = hist_axes.c2p(lo, 0)
                bottom_right = hist_axes.c2p(hi, 0)
                top_left     = hist_axes.c2p(lo, cnt)
                top_right    = hist_axes.c2p(hi, cnt)
                bar = Polygon(bottom_left, bottom_right, top_right, top_left,
                              color=BLUE_E, fill_opacity=0.6, stroke_width=1)
                bars.add(bar)
            return bars

        bars = histogram_bars(SNAPSHOTS[0][1])
        self.add(bars)

        # ---------- Live readout ----------
        readout_pos = box.get_corner(DR) + DOWN * 0.4
        readout = always_redraw(lambda: VGroup(
            Text(f"# particles alive: {int(np.sum(SNAPSHOTS[CURRENT_FRAME[0]][1] > 0))}",
                 font_size=18),
            Text(f"mean radius: {np.mean(SNAPSHOTS[CURRENT_FRAME[0]][1][SNAPSHOTS[CURRENT_FRAME[0]][1] > 0]):.3f}",
                 font_size=18),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.1).move_to(readout_pos))
        self.add(readout)

        # ---------- Animate the timesteps ----------
        # We step through snapshots, animating radius changes only (positions
        # are fixed). At each step we also rebuild the histogram bars.
        for frame_idx in range(1, len(SNAPSHOTS)):
            CURRENT_FRAME[0] = frame_idx
            new_radii = SNAPSHOTS[frame_idx][1]

            anims = []
            for i, c in enumerate(circles):
                if new_radii[i] > 0:
                    target = Circle(radius=new_radii[i], color=BLUE_E,
                                    fill_opacity=0.7, stroke_color=BLUE_A,
                                    stroke_width=1.5).move_to(c.get_center())
                    anims.append(Transform(c, target))
                else:
                    anims.append(c.animate.set_opacity(0))

            new_bars = histogram_bars(new_radii)
            anims.append(Transform(bars, new_bars))

            self.play(*anims, run_time=0.08, rate_func=linear)

        self.wait(1.5)


# Mutable holder so always_redraw lambdas can reference current frame index
CURRENT_FRAME = [0]
