# Manim animations for MRS Tutorial MT01

Source scenes for [`../09_manim_animations.ipynb`](../09_manim_animations.ipynb).
Each `.py` file is a standalone Manim CE scene; pre-rendered MP4s are in
`videos/`.

| Scene | File | Output |
|---|---|---|
| Bragg's law | `01_bragg.py` | `videos/01_bragg.mp4` |
| Ewald sphere | `02_ewald.py` | `videos/02_ewald.mp4` |
| BaTiO3 phase transition | `03_phase_transition.py` | `videos/03_phase_transition.mp4` |
| Ostwald ripening | `04_ostwald.py` | `videos/04_ostwald.mp4` |

## Re-render

```bash
# System deps
sudo apt install ffmpeg libcairo2-dev libpango1.0-dev texlive-full   # Linux
brew install ffmpeg cairo pango py3cairo && brew install --cask mactex   # macOS

# Python
pip install manim

# Render one scene at low quality (fast)
manim -ql 01_bragg.py Bragg

# All four
for f in 0[1-4]_*.py; do
    scene=$(grep -m1 "^class " "$f" | sed 's/class \(.*\)(Scene):/\1/')
    manim -ql "$f" "$scene"
done

# Copy to videos/
cp media/videos/*/480p15/*.mp4 videos/
```

`-ql` = 480p15 (low quality, fast). Use `-qm` (720p30) or `-qh` (1080p60)
for production.
