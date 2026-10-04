# Exodus: large ship drill sprite.
# Design: 1x3 platform bar + ONE huge drill bit (ready drills.rsi art, upscaled).
# South frame is built natively; other directions derive via flip/transpose.
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "Resources/Textures/_Mono/Structures/Machines/drills.rsi"
OUTPUT = ROOT / "Resources/Textures/_Exodus/Structures/Machines/large_ship_drill.rsi"
CANVAS = 128
DIRECTIONS = ("south", "north", "east", "west")

CONE_SCALE = 3
CONE_SIZE = 32 * CONE_SCALE


def load_cones():
    off = Image.open(SOURCE / "drill.png").convert("RGBA")
    sheet = Image.open(SOURCE / "drill_on.png").convert("RGBA")
    on = [sheet.crop((0, 0, 32, 32)), sheet.crop((32, 0, 64, 32))]
    return (
        off.resize((CONE_SIZE, CONE_SIZE), Image.Resampling.NEAREST),
        [f.resize((CONE_SIZE, CONE_SIZE), Image.Resampling.NEAREST) for f in on],
    )


CONE_OFF, CONE_ON = load_cones()
# South-facing cone (tip down) in both variants.
CONE_OFF_S = CONE_OFF.transpose(Image.FLIP_TOP_BOTTOM)
CONE_ON_S = [f.transpose(Image.FLIP_TOP_BOTTOM) for f in CONE_ON]


def draw_platform(draw):
    """1x3 machinery platform bar across the top (south layout).

    Detailed dark housing: recessed vents, panel seams, bolts, status LEDs.
    """
    outline = (32, 36, 48, 255)
    # Drawn one tier brighter: dark_grade pulls everything down to black metal.
    base = (97, 98, 114, 255)
    steel = (139, 141, 158, 255)
    steel_lt = (178, 181, 196, 255)
    top_lt = (216, 219, 229, 255)
    shadow = (64, 68, 86, 255)
    recess = (57, 61, 75, 255)
    black = (0, 0, 0, 255)

    draw.rectangle((16, 4, 111, 35), fill=base, outline=outline)
    draw.line((17, 5, 110, 5), fill=top_lt)
    draw.line((17, 34, 110, 34), fill=shadow)
    # Panel seams splitting thirds.
    for x in (48, 80):
        draw.line((x, 6, x, 33), fill=outline)
        draw.line((x + 1, 6, x + 1, 33), fill=steel)
    # Recessed vent blocks on the side thirds.
    for (vx0, vx1) in ((22, 42), (86, 106)):
        draw.rectangle((vx0, 12, vx1, 28), fill=recess, outline=outline)
        for sy in (14, 19, 24):
            draw.rectangle((vx0 + 2, sy, vx1 - 2, sy + 2), fill=black)
        draw.line((vx0 + 1, 13, vx1 - 1, 13), fill=top_lt)
    # Status LEDs on the middle third.
    draw.point((62, 12), fill=(240, 200, 80, 255))
    draw.point((66, 12), fill=(200, 60, 50, 255))
    # Face bolts top and bottom.
    for bx, by in ((24, 9), (104, 9), (24, 31), (104, 31)):
        draw.rectangle((bx - 1, by - 1, bx + 1, by + 1), fill=outline)
        draw.point((bx, by), fill=steel_lt)


def draw_chuck(draw):
    """Clamp housing the cone disappears into (south layout)."""
    outline = (32, 36, 48, 255)
    housing = (74, 78, 96, 255)
    housing_dk = (50, 54, 70, 255)
    steel = (139, 141, 158, 255)
    steel_lt = (178, 181, 196, 255)
    shadow = (64, 68, 86, 255)

    draw.rectangle((20, 26, 108, 52), fill=housing, outline=outline)
    draw.line((21, 27, 107, 27), fill=steel)
    draw.line((21, 51, 107, 51), fill=shadow)
    # Brushed face lines across the chuck.
    for gy in (34, 44):
        draw.line((21, gy, 107, gy), fill=housing_dk)
        draw.line((21, gy + 1, 107, gy + 1), fill=steel)
    # Vertical end ribs framing the cone.
    for rx in (22, 104):
        draw.line((rx, 28, rx, 50), fill=outline)
        draw.line((rx + 1, 28, rx + 1, 50), fill=steel_lt)
    # Corner bolts clear of the cone silhouette (cone spans ~x25-100 here).
    for bx, by in ((22, 30), (106, 30), (22, 48), (106, 48)):
        draw.rectangle((bx - 1, by - 1, bx + 1, by + 1), fill=outline)
        draw.point((bx, by), fill=steel_lt)


def build_south(cone, bob):
    frame = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    draw = ImageDraw.Draw(frame)
    draw_platform(draw)
    frame.alpha_composite(cone, (16, 28 + bob))
    draw = ImageDraw.Draw(frame)
    draw_chuck(draw)
    return frame


def dark_grade(frame):
    """Pull steel toward near-black metal, keep edges, lamps and LEDs alive."""
    px = frame.load()
    w, h = frame.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a == 0:
                continue
            if r > b + 30:
                continue  # warm accents, red/yellow LEDs
            if (r + g + b) // 3 > 170:
                continue  # bright edges, lamps and glints stay readable
            px[x, y] = (
                round(r * 0.52),
                round(g * 0.55),
                round(b * 0.60),
                a,
            )
    return frame


def save_frames(name, frames, columns):
    rows = (len(frames) + columns - 1) // columns
    sheet = Image.new("RGBA", (CANVAS * columns, CANVAS * rows), (0, 0, 0, 0))
    for index, frame in enumerate(frames):
        sheet.paste(dark_grade(frame), ((index % columns) * CANVAS, (index // columns) * CANVAS))
    sheet.save(OUTPUT / f"{name}.png", optimize=True)


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)

    south_off = build_south(CONE_OFF_S, 0)
    save_frames("off", [
        south_off,
        south_off.transpose(Image.FLIP_TOP_BOTTOM),
        south_off.transpose(Image.ROTATE_90),
        south_off.transpose(Image.ROTATE_270),
    ], 2)

    # Cone frames alternate, bob ping-pongs: all 4 phases differ, hull static.
    on_frames = []
    for phase in range(4):
        cone = CONE_ON_S[phase % 2]
        south = build_south(cone, (0, 1, 0, 1)[phase])
        on_frames.extend([
            south,
            south.transpose(Image.FLIP_TOP_BOTTOM),
            south.transpose(Image.ROTATE_90),
            south.transpose(Image.ROTATE_270),
        ])
    # Reorder to direction-major (4 phases per direction) like the RSI expects.
    ordered = []
    for direction in range(4):
        for phase in range(4):
            ordered.append(on_frames[phase * 4 + direction])
    save_frames("on", ordered, 4)


if __name__ == "__main__":
    main()
