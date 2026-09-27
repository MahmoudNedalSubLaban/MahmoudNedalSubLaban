"""Draw a measured extent schematic, not a full layout or a replacement via."""

import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


root = Path(__file__).resolve().parent
with (root / "measured-enclosures.csv").open(newline="") as stream:
    rows = list(csv.DictReader(stream))

plt.rcParams.update(
    {"font.family": "DejaVu Sans", "font.size": 11, "svg.hashsalt": "pdn-enclosure"}
)
fig, axes = plt.subplots(2, 1, figsize=(9, 5.9), sharex=True)
fig.patch.set_facecolor("white")
cut_color = "#d95f42"
metal_color = "#316da8"

for ax, case, title in zip(
    axes,
    ["edge", "positive"],
    ["A. Negative enclosure", "B. Positive but insufficient enclosure"],
):
    row = next(r for r in rows if r["case"] == case and r["layer"] == "metal4")
    scale = 1000 / int(row["dbu_per_micron"])
    cut_lo, cut_hi = float(row["cut_y_min_dbu"]) * scale, float(row["cut_y_max_dbu"]) * scale
    metal_lo = float(row["metal_y_min_dbu"]) * scale
    metal_hi = float(row["metal_y_max_dbu"]) * scale
    required = float(row["required_enclosure_dbu"]) * scale
    margin = min(cut_lo - metal_lo, metal_hi - cut_hi)
    ax.add_patch(Rectangle((cut_lo, 0.60), cut_hi - cut_lo, 0.22, color=cut_color))
    ax.add_patch(Rectangle((metal_lo, 0.13), metal_hi - metal_lo, 0.22, color=metal_color))
    ax.text(0, 0.71, f"Cut: {cut_hi - cut_lo:g} nm", ha="center", va="center", color="white")
    ax.text(0, 0.39, f"Landing: {metal_hi - metal_lo:g} nm", ha="center", color=metal_color)
    for pos in [cut_lo, cut_hi]:
        ax.plot([pos, pos], [0.03, 0.83], color=cut_color, linestyle=":", linewidth=1.2)
    if case == "edge":
        for start, end in [(cut_lo, metal_lo), (metal_hi, cut_hi)]:
            ax.annotate("", xy=(start, 0.21), xytext=(end, 0.21),
                        arrowprops={"arrowstyle": "<->", "color": "#a63226", "lw": 1.5})
            ax.text((start + end) / 2, 0.06, "60 nm protrusion", ha="center", fontsize=10, color="#a63226")
    ax.set_title(f"{title}  |  margin {margin:g} nm/side; required ≥ {required:g} nm",
                 loc="left", fontsize=12, fontweight="bold", pad=10)
    ax.set_yticks([0.24, 0.71], ["Landing metal", "Cut"])
    ax.set_ylim(-0.08, 0.97)
    ax.set_xlim(-90, 90)
    ax.spines[["top", "left", "right"]].set_visible(False)
    ax.spines["bottom"].set_color("#b8c0c9")
    ax.tick_params(axis="y", length=0, pad=12)
    ax.tick_params(axis="x", colors="#5a6570")

axes[1].set_xlabel("Affected y dimension (nm), displayed horizontally")
axes[1].set_xticks([-80, -60, -40, -20, 0, 20, 40, 60, 80])
fig.suptitle("Generated-via enclosure: measured one-dimensional extents", fontsize=15,
             fontweight="bold", x=0.05, ha="left", y=0.98)
fig.text(0.05, 0.026,
         "Original OpenDB rectangles · 2000 DBU/μm · Both landings share these y extents.\n"
         "Measured schematic, not a layout screenshot. No replacement connection is depicted.",
         fontsize=10, color="#52606d")
fig.subplots_adjust(left=0.17, right=0.98, top=0.87, bottom=0.19, hspace=0.65)
svg_path = root / "enclosure-geometry.svg"
fig.savefig(svg_path, metadata={"Date": None, "Creator": "Mahmoud Sub Laban"})
# Normalize generated whitespace without changing any SVG path coordinates.
svg_path.write_text("\n".join(line.rstrip() for line in svg_path.read_text().splitlines()) + "\n")
plt.close(fig)
