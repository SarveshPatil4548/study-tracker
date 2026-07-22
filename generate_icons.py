from PIL import Image, ImageDraw, ImageFilter
import os, random

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "icons")
os.makedirs(OUT, exist_ok=True)


def lerp(c1, c2, t):
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


def rounded_rect_mask(size, radius):
    mask = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(mask)
    r = radius
    d.rectangle([r, 0, size - r, size], fill=255)
    d.rectangle([0, r, size, size - r], fill=255)
    d.pieslice([0, 0, 2 * r, 2 * r], 180, 270, fill=255)
    d.pieslice([size - 2 * r, 0, size, 2 * r], 270, 360, fill=255)
    d.pieslice([0, size - 2 * r, 2 * r, size], 90, 180, fill=255)
    d.pieslice([size - 2 * r, size - 2 * r, size, size], 0, 90, fill=255)
    return mask


def draw_rocket_icon(size, maskable=False):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    s = size / 512.0
    pad = int(size * 0.10) if maskable else 0
    area = size - 2 * pad
    cx = size // 2
    corner = int(area * 0.20)

    bg_top = (0x1E, 0x1B, 0x4B)
    bg_bot = (0x31, 0x2E, 0x81)
    for y in range(pad, pad + area):
        t = (y - pad) / max(area - 1, 1)
        c = lerp(bg_top, bg_bot, t)
        draw.line([(pad, y), (pad + area, y)], fill=c + (255,))

    mask = rounded_rect_mask(size, corner)
    img.putalpha(mask)
    draw = ImageDraw.Draw(img)

    seed = 42
    rng = random.Random(seed)
    for _ in range(18):
        sx = rng.randint(int(pad + 10 * s), int(pad + area - 10 * s))
        sy = rng.randint(int(pad + 10 * s), int(pad + area - 10 * s))
        sr = rng.uniform(1.0, 2.5) * s
        alpha = rng.randint(80, 180)
        draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(255, 255, 255, alpha))

    rocket_cx = cx
    rocket_top = int(pad + 60 * s)
    rocket_bot = int(pad + area - 80 * s)
    rocket_h = rocket_bot - rocket_top

    body_left = int(rocket_cx - 38 * s)
    body_right = int(rocket_cx + 38 * s)
    body_top_y = rocket_top + int(50 * s)
    body_bot_y = rocket_bot - int(10 * s)

    nose_tip = (rocket_cx, rocket_top)
    nose_left = (int(rocket_cx - 32 * s), rocket_top + int(70 * s))
    nose_right = (int(rocket_cx + 32 * s), rocket_top + int(70 * s))
    draw.polygon([nose_tip, nose_left, nose_right], fill=(230, 225, 255, 255))

    draw.rectangle([body_left, body_top_y, body_right, body_bot_y], fill=(230, 225, 255, 255))

    base_y = body_bot_y
    taper = int(6 * s)
    draw.polygon([
        (body_left, base_y),
        (body_left + taper, rocket_bot),
        (body_right - taper, rocket_bot),
        (body_right, base_y),
    ], fill=(200, 195, 240, 255))

    fin_h = int(55 * s)
    fin_w = int(32 * s)
    fin_top = body_bot_y - int(15 * s)

    draw.polygon([
        (body_left, fin_top),
        (body_left - fin_w, fin_top + fin_h),
        (body_left, fin_top + fin_h - int(5 * s)),
    ], fill=(99, 80, 200, 255))
    draw.polygon([
        (body_right, fin_top),
        (body_right + fin_w, fin_top + fin_h),
        (body_right, fin_top + fin_h - int(5 * s)),
    ], fill=(99, 80, 200, 255))

    window_cy = body_top_y + int(40 * s)
    window_r = int(18 * s)
    draw.ellipse([
        rocket_cx - window_r, window_cy - window_r,
        rocket_cx + window_r, window_cy + window_r
    ], fill=(34, 211, 238, 255))
    inner_r = int(12 * s)
    draw.ellipse([
        rocket_cx - inner_r, window_cy - inner_r,
        rocket_cx + inner_r, window_cy + inner_r
    ], fill=(20, 180, 210, 255))
    shine_r = int(5 * s)
    shine_x = rocket_cx - int(4 * s)
    shine_y = window_cy - int(4 * s)
    draw.ellipse([
        shine_x - shine_r, shine_y - shine_r,
        shine_x + shine_r, shine_y + shine_r
    ], fill=(180, 240, 255, 180))

    flame_top_y = rocket_bot - int(2 * s)
    flame_bot_y = rocket_bot + int(40 * s)
    flame_mid_w = int(14 * s)
    flame_outer_w = int(24 * s)

    draw.polygon([
        (rocket_cx, flame_bot_y),
        (rocket_cx - flame_mid_w, flame_top_y + int(10 * s)),
        (rocket_cx + flame_mid_w, flame_top_y + int(10 * s)),
    ], fill=(255, 200, 50, 255))

    inner_top = flame_top_y + int(18 * s)
    inner_bot = flame_bot_y - int(8 * s)
    draw.polygon([
        (rocket_cx, inner_bot),
        (rocket_cx - int(8 * s), inner_top),
        (rocket_cx + int(8 * s), inner_top),
    ], fill=(255, 255, 180, 255))

    glow_layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow_layer)
    glow_cx = rocket_cx
    glow_cy = rocket_bot + int(20 * s)
    glow_r = int(50 * s)
    for r in range(glow_r, 0, -max(int(2 * s), 1)):
        alpha = int(40 * (1 - r / glow_r))
        gd.ellipse([
            glow_cx - r, glow_cy - r // 2,
            glow_cx + r, glow_cy + r // 2
        ], fill=(255, 180, 50, alpha))
    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(radius=int(12 * s)))
    img = Image.alpha_composite(img, glow_layer)
    draw = ImageDraw.Draw(img)

    dot_y = int(pad + area - 30 * s)
    dot_r = int(5 * s)
    dot_spacing = int(18 * s)
    num_dots = 5
    dots_start_x = cx - (num_dots - 1) * dot_spacing // 2

    for i in range(num_dots):
        dx = dots_start_x + i * dot_spacing
        if i < 3:
            color = (255, 255, 255, 220)
        else:
            color = (255, 255, 255, 60)
        draw.ellipse([dx - dot_r, dot_y - dot_r, dx + dot_r, dot_y + dot_r], fill=color)

    ck_cx = dots_start_x + dot_spacing
    ck_cy = dot_y
    ck_s = int(3.5 * s)
    draw.line([
        (ck_cx - ck_s, ck_cy),
        (ck_cx - int(1 * s), ck_cy + ck_s),
        (ck_cx + ck_s, ck_cy - ck_s),
    ], fill=(255, 255, 255, 240), width=max(int(2.5 * s), 1))

    return img


files = {
    "icon-192.png": (192, False),
    "icon-512.png": (512, False),
    "icon-maskable-192.png": (192, True),
    "icon-maskable-512.png": (512, True),
}

for fname, (sz, mask) in files.items():
    img = draw_rocket_icon(sz, maskable=mask)
    path = os.path.join(OUT, fname)
    img.save(path, "PNG")
    kb = os.path.getsize(path) / 1024
    label = "maskable" if mask else "any"
    print(f"  {fname:30s}  {sz}x{sz}  purpose={label:8s}  {kb:.1f} KB")

print("\nDone — all 4 icons written to static/icons/")
