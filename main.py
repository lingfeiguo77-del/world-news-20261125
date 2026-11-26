#!/usr/bin/env python3
"""news-image-20261125: sum up 25 November 2026 world news in one image.

Draws a 1024x1024 PNG front page with Pillow only. No network, no randomness,
no timestamps, no environment-dependent output. Runs twice -> identical bytes.

Output: /output/entry.png (override for local testing with NEWS_IMAGE_OUTPUT).
Python 3.13 compatible (also runs on 3.12). Requires Pillow.
"""

import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024

# --- palette (fixed) -------------------------------------------------------
BG = (11, 27, 46)        # deep navy
PANEL = (18, 40, 63)     # card panel
PANEL_EDGE = (38, 74, 106)
WHITE = (244, 246, 248)
MUTED = (168, 188, 205)  # subtitle grey-blue
KICKER = (126, 164, 196)
RED = (214, 48, 49)
RED_DARK = (178, 34, 34)
AMBER = (232, 163, 61)
ICON = (96, 140, 175)
ICON_DIM = (64, 98, 130)

# --- fonts ------------------------------------------------------------------
_HERE = Path(__file__).resolve().parent


def _font(name, size):
    candidates = [
        _HERE / "fonts" / name,
        Path("/usr/share/fonts/truetype/dejavu") / name,
    ]
    for path in candidates:
        if path.is_file():
            return ImageFont.truetype(str(path), size)
    raise FileNotFoundError("font not found: %s" % name)


def bold(size):
    return _font("DejaVuSans-Bold.ttf", size)


def regular(size):
    return _font("DejaVuSans.ttf", size)


# --- text helpers -----------------------------------------------------------
def wrap(draw, text, font, max_width):
    """Greedy word wrap; returns list of lines, each <= max_width."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = word if not cur else cur + " " + word
        if draw.textlength(trial, font=font) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_lines(draw, text, font_sizes, max_width, max_lines, bold_flag):
    """Pick the largest font size whose wrap fits in max_lines."""
    for size in font_sizes:
        font = bold(size) if bold_flag else regular(size)
        lines = wrap(draw, text, font, max_width)
        if len(lines) <= max_lines:
            return font, lines
    font = bold(font_sizes[-1]) if bold_flag else regular(font_sizes[-1])
    return font, wrap(draw, text, font, max_width)[:max_lines]


def draw_lines(draw, lines, font, x, y, fill, leading):
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        y += leading
    return y


# --- icons (pure vector shapes, bottom-right corner of each card) -----------
def icon_ships(draw, x, y):
    # two tanker silhouettes on waves
    for sx, sy, s in ((x, y + 34, 1.0), (x + 52, y + 14, 0.72)):
        w, h = int(74 * s), int(20 * s)
        draw.polygon([(sx, sy), (sx + w, sy), (sx + w - 8 * s, sy + h),
                      (sx + 8 * s, sy + h)], fill=ICON)
        draw.rectangle([sx + 14 * s, sy - 12 * s, sx + 30 * s, sy], fill=ICON)
        draw.line([sx + 22 * s, sy - 22 * s, sx + 22 * s, sy - 12 * s],
                  fill=ICON, width=2)
    for wy in (y + 66, y + 76):
        draw.arc([x - 6, wy - 8, x + 130, wy + 8], 0, 180, fill=ICON_DIM, width=2)


def icon_tower(draw, x, y):
    draw.rectangle([x + 44, y + 6, x + 72, y + 78], fill=ICON)
    draw.line([x + 58, y - 6, x + 58, y + 6], fill=ICON, width=3)
    draw.polygon([(x + 20, y + 78), (x + 44, y + 40), (x + 44, y + 78)],
                 fill=ICON_DIM)
    draw.polygon([(x + 72, y + 78), (x + 96, y + 52), (x + 96, y + 78)],
                 fill=ICON_DIM)
    for wy in range(y + 16, y + 72, 12):
        draw.rectangle([x + 50, wy, x + 66, wy + 5], fill=BG)


def icon_scales(draw, x, y):
    draw.line([x + 58, y + 6, x + 58, y + 66], fill=ICON, width=3)
    draw.line([x + 14, y + 18, x + 102, y + 18], fill=ICON, width=3)
    draw.polygon([(x + 58, y + 2), (x + 52, y + 10), (x + 64, y + 10)],
                 fill=ICON)
    for cx in (x + 14, x + 102):
        draw.line([cx, y + 18, cx, y + 34], fill=ICON, width=2)
        draw.arc([cx - 16, y + 30, cx + 16, y + 58], 0, 180, fill=ICON, width=3)
    draw.rectangle([x + 34, y + 66, x + 82, y + 74], fill=ICON)


def icon_rocket(draw, x, y):
    draw.ellipse([x + 20, y + 32, x + 96, y + 74], outline=ICON_DIM, width=2)
    draw.polygon([(x + 58, y + 2), (x + 72, y + 34), (x + 44, y + 34)],
                 fill=ICON)
    draw.rectangle([x + 44, y + 34, x + 72, y + 62], fill=ICON)
    draw.polygon([(x + 44, y + 48), (x + 30, y + 66), (x + 44, y + 62)],
                 fill=ICON_DIM)
    draw.polygon([(x + 72, y + 48), (x + 86, y + 66), (x + 72, y + 62)],
                 fill=ICON_DIM)
    draw.ellipse([x + 50, y + 38, x + 66, y + 54], fill=BG,
                 outline=WHITE, width=2)
    draw.polygon([(x + 52, y + 66), (x + 58, y + 78), (x + 64, y + 66)],
                 fill=AMBER)


ICONS = (icon_ships, icon_tower, icon_scales, icon_rocket)

STORIES = (
    {
        "num": "01",
        "kicker": "MIDDLE EAST \u2014 STRAIT OF HORMUZ",
        "title": "TANKERS HIT IN STRAIT OF HORMUZ",
        "sub": "Two oil tankers struck naval mines and caught fire, "
               "Iran's Revolutionary Guard says",
        "stat": "2 TANKERS HIT",
    },
    {
        "num": "02",
        "kicker": "SAUDI ARABIA \u2014 RIYADH",
        "title": "HOUTHIS HIT RIYADH'S TALLEST TOWER",
        "sub": "Strike on the capital's tallest tower injures 11, "
               "Saudi civil defense says",
        "stat": "11 INJURED",
    },
    {
        "num": "03",
        "kicker": "UNITED STATES \u2014 TECH TRIAL",
        "title": "HUAWEI CONVICTED IN US TRIAL",
        "sub": "Jury finds trade-secret theft and bank fraud; "
               "clears racketeering charge",
        "stat": "GUILTY ON 2 COUNTS",
    },
    {
        "num": "04",
        "kicker": "SPACE \u2014 TIANGONG STATION",
        "title": "PAKISTAN ASTRONAUT REACHES TIANGONG",
        "sub": "Shenzhou-24 docks; first foreign astronaut boards "
               "China's space station",
        "stat": "1ST FOREIGN ASTRONAUT",
    },
)

TICKER = ("ALSO:  US proposes new tariffs on 14 partners  \u00b7  "
          "Russia strikes Odesa, 2 killed  \u00b7  "
          "COP31 climate talks end without a deal")


def draw_card(draw, story, x, y, w, h, icon_fn):
    draw.rounded_rectangle([x, y, x + w, y + h], radius=14,
                           fill=PANEL, outline=PANEL_EDGE, width=2)
    pad = 24
    tx, tw = x + pad, w - 2 * pad
    cy = y + 20
    # number + kicker
    draw.text((tx, cy), story["num"], font=bold(26), fill=RED)
    draw.text((tx + 52, cy + 5), story["kicker"], font=bold(17), fill=KICKER)
    cy += 48
    # title (auto-fit, max 3 lines)
    tfont, tlines = fit_lines(draw, story["title"], (38, 34, 30), tw, 3, True)
    cy = draw_lines(draw, tlines, tfont, tx, cy, WHITE, int(tfont.size * 1.12))
    cy += 8
    # subtitle (auto-fit, max 3 lines)
    sfont, slines = fit_lines(draw, story["sub"], (23, 21, 19), tw, 3, False)
    draw_lines(draw, slines, sfont, tx, cy, MUTED, int(sfont.size * 1.35))
    # stat chip, bottom-left
    chip_font = bold(20)
    label = story["stat"]
    cw = int(draw.textlength(label, font=chip_font)) + 28
    ch = 38
    cx, cyy = tx, y + h - 20 - ch
    draw.rounded_rectangle([cx, cyy, cx + cw, cyy + ch], radius=8, fill=RED_DARK)
    draw.text((cx + 14, cyy + 8), label, font=chip_font, fill=WHITE)
    # icon, bottom-right
    icon_fn(draw, x + w - 24 - 116, y + h - 20 - 84)


def main():
    out = Path(os.environ.get("NEWS_IMAGE_OUTPUT", "/output/entry.png"))
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # --- header ------------------------------------------------------------
    draw.text((40, 26), "WORLD NEWS", font=bold(66), fill=WHITE)
    draw.text((40, 100), "WEDNESDAY, 25 NOVEMBER 2026",
              font=bold(26), fill=AMBER)
    draw.rectangle([40, 140, W - 40, 144], fill=RED)

    # --- 2x2 story cards ----------------------------------------------------
    margin, gap = 32, 24
    cw = (W - 2 * margin - gap) // 2
    chh = 363
    top = 164
    for i, story in enumerate(STORIES):
        cx = margin + (i % 2) * (cw + gap)
        cy = top + (i // 2) * (chh + gap)
        draw_card(draw, story, cx, cy, cw, chh, ICONS[i])

    # --- footer ticker -------------------------------------------------------
    fy = top + 2 * chh + gap + 18
    draw.rectangle([0, fy - 10, W, fy + 52], fill=(8, 20, 34))
    # shrink ticker font until the whole line fits (never truncate mid-word)
    tsize = 21
    while tsize > 12:
        tfont = regular(tsize)
        if draw.textlength(TICKER, font=tfont) <= W - 80:
            break
        tsize -= 1
    draw.text((40, fy + 2), TICKER, font=tfont, fill=MUTED)

    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, format="PNG")
    os.chmod(out, 0o644)
    print("wrote %s (%dx%d)" % (out, W, H))


if __name__ == "__main__":
    main()
