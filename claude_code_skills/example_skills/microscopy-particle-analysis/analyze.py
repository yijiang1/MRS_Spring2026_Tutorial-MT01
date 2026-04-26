#!/usr/bin/env python3
"""Particle-size analysis on a microscopy image.

Usage:
    python analyze.py <image_path> [--min-area N] [--save-overlay path]

Output: JSON to stdout with particle count and radius statistics.
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

import numpy as np
from scipy import ndimage


def load_grayscale(path: Path) -> np.ndarray:
    """Load an image as a [0,1] grayscale float array."""
    try:
        from PIL import Image
        img = np.asarray(Image.open(path).convert("L"), dtype=np.float32) / 255.0
    except ImportError:
        import matplotlib.image as mpimg
        img = mpimg.imread(str(path))
        if img.ndim == 3:
            img = img[..., :3].mean(axis=-1)
        if img.dtype != np.float32 or img.max() > 1.0:
            img = img.astype(np.float32) / max(img.max(), 1.0)
    return img


def otsu_threshold(img: np.ndarray) -> float:
    hist, edges = np.histogram(img, bins=256, range=(0, 1))
    p = hist / hist.sum()
    omega = np.cumsum(p)
    mu = np.cumsum(p * (edges[:-1] + 0.5 * (edges[1] - edges[0])))
    sigma_b = (mu[-1] * omega - mu) ** 2 / (omega * (1 - omega) + 1e-12)
    return float(edges[:-1][int(np.argmax(sigma_b))])


def analyze(image_path: Path, min_area: int = 30,
            overlay_path: Path | None = None) -> dict:
    img = load_grayscale(image_path)
    thr = otsu_threshold(img)
    binary = (img > thr).astype(np.uint8)

    labels, n_raw = ndimage.label(binary)
    sizes = ndimage.sum(binary, labels, range(1, n_raw + 1))
    keep = np.where(sizes >= min_area)[0] + 1
    relabel = np.zeros(n_raw + 1, dtype=int)
    relabel[keep] = np.arange(1, len(keep) + 1)
    labels = relabel[labels]
    n = int(len(keep))

    if n == 0:
        return {"error": "No particles found above min_area threshold.",
                "threshold": thr, "min_area": min_area}

    areas = ndimage.sum(np.ones_like(labels), labels, range(1, n + 1))
    radii = np.sqrt(areas / np.pi)
    result = {
        "image_path":           str(image_path),
        "shape":                list(img.shape),
        "threshold_method":     "otsu",
        "threshold":            float(thr),
        "min_area_px":          int(min_area),
        "n_particles":          n,
        "mean_radius_px":       float(radii.mean()),
        "median_radius_px":     float(np.median(radii)),
        "std_radius_px":        float(radii.std()),
        "min_radius_px":        float(radii.min()),
        "max_radius_px":        float(radii.max()),
    }

    if overlay_path is not None:
        try:
            import matplotlib.pyplot as plt
            fig, axes = plt.subplots(1, 3, figsize=(13, 4))
            axes[0].imshow(img, cmap="gray"); axes[0].set_title("Original")
            axes[1].imshow(binary, cmap="gray"); axes[1].set_title(f"Otsu ({thr:.2f})")
            axes[2].imshow(labels, cmap="nipy_spectral"); axes[2].set_title(f"{n} particles")
            for a in axes: a.axis("off")
            plt.tight_layout()
            plt.savefig(overlay_path, dpi=120, bbox_inches="tight")
            plt.close(fig)
            result["overlay_path"] = str(overlay_path)
        except ImportError:
            result["overlay_path"] = None

    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("image_path", type=Path)
    ap.add_argument("--min-area", type=int, default=30)
    ap.add_argument("--save-overlay", type=Path, default=None)
    args = ap.parse_args()

    if not args.image_path.exists():
        print(json.dumps({"error": f"file not found: {args.image_path}"}))
        sys.exit(1)

    result = analyze(args.image_path,
                     min_area=args.min_area,
                     overlay_path=args.save_overlay)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
