"""
generate_showcase_v2.py

Crystallytics — Enhanced LinkedIn Showcase Video (v2)

Improvements over v1:
  • Smooth black fade-in / fade-out transitions between every scene
  • Animated bar charts that grow progressively left-to-right
  • Animated line chart that draws itself point-by-point
  • Typewriter caption effect on the hero splash
  • Pulsing "recording dot" on data-loading scene (simulates live activity)
  • Animated counting metric cards (numbers count up)
  • Richer particle/star field on dark scenes
  • Cleaner scene layout and larger readable fonts
  • 1280×720 HD, 24 FPS, H.264
"""

import os
import math
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import imageio

# ── Constants ────────────────────────────────────────────────────────────────
WIDTH, HEIGHT = 1280, 720
FPS = 24
FONT_DIR = "C:/Windows/Fonts"

# ── Fonts ─────────────────────────────────────────────────────────────────────
font_hero    = ImageFont.truetype(f"{FONT_DIR}/segoeuib.ttf", 58)
font_title   = ImageFont.truetype(f"{FONT_DIR}/segoeuib.ttf", 42)
font_heading = ImageFont.truetype(f"{FONT_DIR}/segoeuib.ttf", 28)
font_sub     = ImageFont.truetype(f"{FONT_DIR}/segoeui.ttf",  20)
font_body    = ImageFont.truetype(f"{FONT_DIR}/segoeui.ttf",  17)
font_body_b  = ImageFont.truetype(f"{FONT_DIR}/segoeuib.ttf", 17)
font_code    = ImageFont.truetype(f"{FONT_DIR}/consola.ttf",  14)
font_num_lg  = ImageFont.truetype(f"{FONT_DIR}/segoeuib.ttf", 36)
font_num_sm  = ImageFont.truetype(f"{FONT_DIR}/segoeuib.ttf", 13)
font_emoji   = ImageFont.truetype(f"{FONT_DIR}/seguiemj.ttf", 48) if os.path.exists(f"{FONT_DIR}/seguiemj.ttf") else font_title

# ── Colour palette ────────────────────────────────────────────────────────────
C = {
    "dark_bg":   (11,  15,  25),
    "dark_mid":  (22,  28,  52),
    "light_bg":  (248, 250, 252),
    "light_mid": (241, 245, 249),
    "white":     (255, 255, 255),
    "black":     (0,   0,   0),
    "slate":     (100, 116, 139),
    "nav":       (15,  23,  42),
    "sky":       (56,  189, 248),
    "blue":      (59,  130, 246),
    "indigo":    (99,  102, 241),
    "emerald":   (16,  185, 129),
    "violet":    (139, 92,  246),
    "amber":     (245, 158, 11),
    "text":      (15,  23,  42),
    "muted":     (71,  85,  105),
    "border":    (226, 232, 240),
    "grad_a":    (0,   114, 255),
    "grad_b":    (0,   198, 255),
}


# ── Helpers ───────────────────────────────────────────────────────────────────
def lerp(a, b, t):
    return a + (b - a) * t


def ease_out(t):
    return 1 - (1 - t) ** 3


def ease_in_out(t):
    if t < 0.5:
        return 4 * t * t * t
    p = 2 * t - 2
    return 0.5 * p * p * p + 1


def clamp(x, lo=0, hi=1):
    return max(lo, min(hi, x))


def gradient_bg(c1, c2, horizontal=False):
    base = Image.new("RGB", (WIDTH, HEIGHT), c1)
    top  = Image.new("RGB", (WIDTH, HEIGHT), c2)
    mask = Image.new("L", (WIDTH, HEIGHT))
    data = []
    for y in range(HEIGHT):
        for x in range(WIDTH):
            v = (x / WIDTH) if horizontal else (y / HEIGHT)
            data.append(int(255 * v))
    mask.putdata(data)
    base.paste(top, (0, 0), mask)
    return base


def draw_card(draw, x, y, w, h, fill="#FFFFFF", outline=None, radius=10, width=1):
    ol = outline or C["border"]
    if isinstance(ol, tuple):
        ol = ol
    if isinstance(fill, tuple):
        fill = fill
    draw.rounded_rectangle([x, y, x + w, y + h], radius=radius,
                            fill=fill, outline=ol, width=width)


def draw_header(draw, progress_frac, subtitle=""):
    draw.rectangle([0, 0, WIDTH, 58], fill=C["nav"])
    draw.text((28, 14), "💎 Crystallytics", font=font_heading, fill=C["white"])
    if subtitle:
        sw = draw.textlength(subtitle, font=font_code)
        draw.text((WIDTH // 2 - sw // 2, 20), subtitle, font=font_code, fill=C["sky"])

    badges = ["ISO/IEC 25010", "ISO/IEC 27001", "⚡ Google Antigravity"]
    bx = WIDTH - 420
    for b in badges:
        bw = int(draw.textlength(b, font=font_code)) + 16
        draw.rounded_rectangle([bx, 16, bx + bw, 42], radius=5,
                                fill=(30, 41, 59), outline=(51, 65, 85), width=1)
        draw.text((bx + 8, 20), b, font=font_code, fill=C["sky"])
        bx += bw + 8

    # Gradient progress bar
    bar_w = int(WIDTH * clamp(progress_frac))
    for px in range(bar_w):
        t = px / max(WIDTH - 1, 1)
        r = int(lerp(C["grad_a"][0], C["grad_b"][0], t))
        g = int(lerp(C["grad_a"][1], C["grad_b"][1], t))
        b = int(lerp(C["grad_a"][2], C["grad_b"][2], t))
        draw.line([(px, 56), (px, 58)], fill=(r, g, b))


def star_field(draw, seed=42, count=120, t=0.0):
    rng = random.Random(seed)
    for _ in range(count):
        x = rng.randint(0, WIDTH)
        y = rng.randint(0, HEIGHT)
        base_a = rng.randint(60, 200)
        twinkle = int(base_a * (0.7 + 0.3 * math.sin(t * 3 + rng.random() * 6)))
        r = rng.randint(1, 2)
        draw.ellipse([x - r, y - r, x + r, y + r], fill=(twinkle, twinkle, twinkle))


def apply_fade(frame_arr, alpha):
    """Blend frame with black for fade in/out. alpha=1 → full frame, 0 → black."""
    if alpha >= 1.0:
        return frame_arr
    overlay = np.zeros_like(frame_arr)
    return (frame_arr * alpha + overlay * (1 - alpha)).astype(np.uint8)


# ── SCENE RENDERERS ───────────────────────────────────────────────────────────

TYPEWRITER_FULL = "AI-Powered • Context-Aware • Zero Hallucinations"


def render_scene_1(t, total_t):
    """Scene 1: Hero Splash (0–6s) — typewriter subtitle, pulsing diamond, star field."""
    frame = gradient_bg(C["dark_bg"], C["dark_mid"])
    draw  = ImageDraw.Draw(frame)

    star_field(draw, seed=7, count=160, t=t)

    # Pulsing glow behind diamond
    pulse = 0.4 + 0.6 * abs(math.sin(t * 2.2))
    for r in range(80, 10, -10):
        a = int(20 * pulse * (1 - r / 80))
        col = (int(C["sky"][0] * a / 255), int(C["sky"][1] * a / 255), int(C["sky"][2] * a / 255))
        draw.ellipse([WIDTH // 2 - r, 240 - r, WIDTH // 2 + r, 240 + r], fill=col)

    # Diamond  (use regular font with emoji character)
    draw.text((WIDTH // 2 - 36, 190), "💎", font=font_heading, fill=C["sky"])

    # Main title — fade in during first 1.5 s
    title_alpha = clamp(t / 1.2)
    if title_alpha > 0:
        title = "Crystallytics"
        tw = draw.textlength(title, font=font_hero)
        # Manual alpha blend via two-pass: draw on transparent then paste
        txt_img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        txt_d   = ImageDraw.Draw(txt_img)
        txt_d.text((WIDTH // 2 - tw // 2, 285), title, font=font_hero,
                   fill=(255, 255, 255, int(255 * title_alpha)))
        frame.paste(Image.new("RGB", (WIDTH, HEIGHT), (0, 0, 0)),
                    mask=txt_img.split()[3])
        frame.paste(txt_img.convert("RGB"), mask=txt_img.split()[3])
        draw = ImageDraw.Draw(frame)  # refresh draw handle

    # Typewriter subtitle
    tw_total_chars = len(TYPEWRITER_FULL)
    chars_shown = int(clamp((t - 1.0) / 2.5) * tw_total_chars)
    tw_text = TYPEWRITER_FULL[:chars_shown]
    if tw_text:
        sw = draw.textlength(tw_text, font=font_heading)
        draw.text((WIDTH // 2 - sw // 2, 358), tw_text, font=font_heading, fill=C["sky"])

    # Tagline
    if t > 2.5:
        tag = "Crystallize your data  •  Tally the truth"
        tgw = draw.textlength(tag, font=font_sub)
        a = clamp((t - 2.5) / 1.0)
        draw.text((WIDTH // 2 - tgw // 2, 405), tag, font=font_sub,
                  fill=(int(148 * a), int(163 * a), int(184 * a)))

    # Pill badges slide in from bottom
    if t > 3.2:
        pills = ["ISO/IEC 25010 Quality Model", "ISO/IEC 27001 Zero-Retention", "⚡ Google Antigravity"]
        total_w = sum(int(draw.textlength(p, font=font_body)) + 32 for p in pills) + 24
        px = (WIDTH - total_w) // 2
        slide_a = clamp((t - 3.2) / 0.8)
        base_y  = 455
        draw_y  = int(lerp(base_y + 40, base_y, ease_out(slide_a)))
        for p in pills:
            pw = int(draw.textlength(p, font=font_body)) + 28
            draw.rounded_rectangle([px, draw_y, px + pw, draw_y + 36],
                                   radius=18, fill=(30, 41, 59), outline=C["indigo"], width=1)
            draw.text((px + 14, draw_y + 8), p, font=font_body, fill=(226, 232, 240))
            px += pw + 12

    # GitHub pill
    if t > 4.0:
        gh = "github.com/Starlyre/Crystallytics"
        gw = int(draw.textlength(gh, font=font_code)) + 24
        gx = (WIDTH - gw) // 2
        a  = clamp((t - 4.0) / 0.8)
        draw.rounded_rectangle([gx, 500, gx + gw, 526], radius=6,
                                fill=(22, 28, 52), outline=C["emerald"], width=1)
        draw.text((gx + 12, 507), gh, font=font_code,
                  fill=(int(C["emerald"][0] * a), int(C["emerald"][1] * a), int(C["emerald"][2] * a)))

    return np.array(frame)


def render_scene_2(t, total_t):
    """Scene 2: Data Ingestion & Health Metrics (6–13s) — count-up metrics, live dot."""
    frame = gradient_bg(C["light_bg"], C["light_mid"])
    draw  = ImageDraw.Draw(frame)
    draw_header(draw, 0.20, "Tab 1 · Data Ingestion & Health Profiling")

    # Ingestion Banner
    draw_card(draw, 36, 76, WIDTH - 72, 60, fill=C["white"], outline=C["border"])
    draw.text((60, 92), "📁  Loaded:", font=font_body_b, fill=C["text"])
    draw.text((155, 92), "sample_sales.csv  —  20 rows × 7 columns  —  UTF-8  —  In-Memory stream", font=font_code, fill=(2, 132, 199))

    # Pulsing "LIVE" dot
    pulse = 0.5 + 0.5 * math.sin(t * 5)
    dot_col = (int(16 + 239 * pulse), int(185 - 100 * pulse), int(129 - 60 * pulse))
    draw.ellipse([WIDTH - 185, 94, WIDTH - 165, 114], fill=dot_col)
    draw.text((WIDTH - 158, 93), "LIVE STREAM", font=font_code, fill=dot_col)

    # Metric cards with count-up animation
    metrics = [
        ("TOTAL ROWS",    20,    "Complete",          C["emerald"]),
        ("COLUMNS",       7,     "4 Numeric",         C["blue"]),
        ("MISSING CELLS", 0,     "0.0% Missing",      C["emerald"]),
        ("DUPLICATES",    0,     "0.0% Dupes",        C["emerald"]),
        ("MEMORY (KB)",   1,     "Client RAM Only",   C["violet"]),
    ]
    card_w = (WIDTH - 72 - 4 * 14) // 5
    anim   = ease_out(clamp(t / 1.5))
    for i, (lbl, final_val, sub, col) in enumerate(metrics):
        cx = 36 + i * (card_w + 14)
        draw_card(draw, cx, 152, card_w, 108, fill=C["white"])
        draw.text((cx + 16, 164), lbl, font=font_num_sm, fill=C["slate"])
        shown = int(final_val * anim)
        draw.text((cx + 16, 184), str(shown), font=font_num_lg, fill=C["text"])
        draw.text((cx + 16, 232), "● " + sub, font=font_num_sm, fill=col)

    # Domain Inference Card
    draw_card(draw, 36, 278, WIDTH - 72, 90, fill=(239, 246, 255), outline=(191, 219, 254))
    draw.text((60, 292), "🧠  INFERRED SUBJECT CONTEXT", font=font_num_sm, fill=(29, 78, 216))
    draw.text((60, 316), "Sales & Commercial",           font=font_heading, fill=C["text"])
    draw.text((310, 325), "(Confidence: High)",           font=font_sub,     fill=C["indigo"])
    draw.text((60, 348), "Signals detected: revenue, product, unit_sold, sale, orders", font=font_code, fill=C["slate"])
    draw_card(draw, WIDTH - 265, 300, 220, 36, fill=(236, 253, 245), outline=(167, 243, 208))
    draw.text((WIDTH - 252, 310), "🛡️  ISO 27001 · Zero Retention", font=font_code, fill=(4, 120, 87))

    # Data preview table
    draw_card(draw, 36, 384, WIDTH - 72, 192, fill=C["white"])
    draw.text((60, 398), "Data Preview — First 5 Rows", font=font_body_b, fill=C["text"])
    headers = ["Date", "Product", "Region", "Units", "Price", "Rating", "Revenue"]
    hx = 60
    for h in headers:
        draw.text((hx, 424), h, font=font_body_b, fill=C["muted"])
        hx += 165
    rows = [
        ["2024-01-01", "Laptop",     "North", "12", "$1200.00", "4.5", "$14,400"],
        ["2024-01-02", "Mouse",      "South", "45", "$25.00",   "4.2", "$1,125"],
        ["2024-01-03", "Keyboard",   "East",  "23", "$75.00",   "4.8", "$1,725"],
        ["2024-01-04", "Monitor",    "West",  "15", "$300.00",  "3.9", "$4,500"],
        ["2024-01-05", "Headphones", "North", "30", "$80.00",   "4.6", "$2,400"],
    ]
    for ri, row in enumerate(rows):
        bg = (248, 250, 252) if ri % 2 == 0 else C["white"]
        draw.rectangle([36, 445 + ri * 26, WIDTH - 36, 471 + ri * 26], fill=bg)
        for ci, cell in enumerate(row):
            draw.text((60 + ci * 165, 450 + ri * 26), cell, font=font_code, fill=C["text"])

    # Tab nav hints at bottom
    tabs = ["🤖 AI Narrative", "📈 Visualizations", "📋 Data Health", "🧹 1-Click Clean"]
    tx = 36
    for i, tab in enumerate(tabs):
        tw2 = int(draw.textlength(tab, font=font_body_b)) + 20
        col = C["blue"] if i == 0 else C["slate"]
        if i == 0:
            draw.line([(tx, 715), (tx + tw2, 715)], fill=C["blue"], width=2)
        draw.text((tx + 10, 697), tab, font=font_body_b, fill=col)
        tx += tw2 + 16

    return np.array(frame)


def render_scene_3(t, total_t):
    """Scene 3: AI Narrative (13–21s) — cards slide in sequentially."""
    frame = gradient_bg(C["light_bg"], C["light_mid"])
    draw  = ImageDraw.Draw(frame)
    draw_header(draw, 0.45, "Tab 2 · AI Narrative & Zero-Hallucination Insights")

    draw.text((36, 74), "🤖  Executive AI Narrative", font=font_heading, fill=C["text"])
    draw.text((36, 108), "Gemini 2.5 Flash  •  Pydantic Schema Validation  •  Python computes — AI interprets",
              font=font_code, fill=C["slate"])

    # Exec summary
    draw_card(draw, 36, 136, WIDTH - 72, 80, fill=C["white"])
    draw.text((60, 150), "📋  Executive Summary", font=font_body_b, fill=C["text"])
    draw.text((60, 176), "20 transaction records · $96,005 total revenue · 0 missing values · Avg rating 4.4/5.0",
              font=font_body, fill=(51, 65, 85))

    # 4 insight cards that slide in one after another
    cards = [
        ("🎯 Key Findings",          C["emerald"],
         ["• Laptop: $56,400 revenue (58.7% share)",
          "• Mouse: 183 units — volume leader",
          "• North Region: 32% of total profit"]),
        ("📈 Observed Trends",       C["blue"],
         ["• Steady growth across 20 time steps",
          "• Rating correlates with product quality",
          "• Balanced 4-region diversification"]),
        ("🔍 Anomaly Detection",     C["amber"],
         ["• 1.5×IQR scan: 0 severe anomalies",
          "• Rating dispersion within normal σ",
          "• No extreme revenue spikes"]),
        ("🚀 Recommended Actions",   C["violet"],
         ["1. Investigate Monitor rating dip",
          "2. Test Mouse pricing elasticity",
          "3. Export audit report for review"]),
    ]
    gw = (WIDTH - 72 - 18) // 2
    gh = 185
    for idx, (title, col, bullets) in enumerate(cards):
        row, coli = divmod(idx, 2)
        cx = 36 + coli * (gw + 18)
        cy = 232 + row * (gh + 14)
        delay = idx * 0.5
        anim  = ease_out(clamp((t - delay) / 0.6))
        slide_y = int(lerp(cy + 30, cy, anim))
        if anim > 0:
            draw_card(draw, cx, slide_y, gw, gh, fill=C["white"])
            # Left accent stripe
            draw.rectangle([cx, slide_y, cx + 5, slide_y + gh], fill=col)
            draw.text((cx + 18, slide_y + 14), title, font=font_body_b, fill=C["text"])
            for bi, bullet in enumerate(bullets):
                draw.text((cx + 18, slide_y + 44 + bi * 28), bullet, font=font_body, fill=(51, 65, 85))

    # Zero-hallucination badge
    if t > 1.8:
        bw = int(draw.textlength("✅  Zero-Hallucination Guarantee  — Python computes, AI narrates", font=font_code)) + 24
        draw.rounded_rectangle([WIDTH // 2 - bw // 2, HEIGHT - 42,
                                 WIDTH // 2 + bw // 2, HEIGHT - 14],
                                radius=8, fill=(236, 253, 245), outline=(167, 243, 208), width=1)
        draw.text((WIDTH // 2 - bw // 2 + 12, HEIGHT - 36),
                  "✅  Zero-Hallucination Guarantee  — Python computes, AI narrates",
                  font=font_code, fill=(4, 120, 87))

    return np.array(frame)


def render_scene_4(t, total_t):
    """Scene 4: Animated Charts (21–29s) — bar chart grows, line chart draws."""
    frame = gradient_bg(C["light_bg"], C["light_mid"])
    draw  = ImageDraw.Draw(frame)
    draw_header(draw, 0.68, "Tab 3 · Automated Visualizations")

    draw.text((36, 74), "📈  Context-Aware Chart Recommender", font=font_heading, fill=C["text"])
    draw.text((36, 108), "Charts auto-selected with mathematical rationale  •  Chart.js powered", font=font_code, fill=C["slate"])

    cw = (WIDTH - 72 - 24) // 2

    # ── LEFT: Animated Line Chart ──────────────────────────────────
    draw_card(draw, 36, 136, cw, 540, fill=C["white"])
    draw.text((60, 152), "Revenue Trend over Date", font=font_body_b, fill=C["text"])
    draw.text((60, 176), "💡 Datetime axis → Line chart recommended", font=font_code, fill=(2, 132, 199))

    # Chart area
    chart_x, chart_y = 60, 210
    chart_w, chart_h = cw - 48, 420
    draw.rectangle([chart_x, chart_y, chart_x + chart_w, chart_y + chart_h],
                   fill=(248, 250, 252), outline=C["border"])

    # Grid lines
    for gi in range(5):
        gy = chart_y + chart_h - gi * (chart_h // 4)
        draw.line([(chart_x, gy), (chart_x + chart_w, gy)], fill=C["border"], width=1)
        label = f"${gi * 25}K"
        draw.text((chart_x - 44, gy - 8), label, font=font_code, fill=C["slate"])

    # Data points (10 points)
    revenues = [14.4, 1.1, 1.7, 4.5, 2.4, 9.8, 1.9, 19.8, 1.5, 39.6]  # $K
    max_r = max(revenues)
    pts = []
    for i, r in enumerate(revenues):
        px = chart_x + int((i / (len(revenues) - 1)) * chart_w)
        py = chart_y + chart_h - int((r / (max_r * 1.1)) * chart_h)
        pts.append((px, py))

    # Animated draw: show pts up to anim_frac
    anim_frac = ease_out(clamp(t / (total_t * 0.6)))
    pts_shown = max(1, int(anim_frac * len(pts)))

    # Gradient fill under line
    if pts_shown > 1:
        poly = [(chart_x, chart_y + chart_h)] + pts[:pts_shown] + [(pts[pts_shown - 1][0], chart_y + chart_h)]
        draw.polygon(poly, fill=(219, 234, 254))

    for i in range(min(pts_shown - 1, len(pts) - 1)):
        draw.line([pts[i], pts[i + 1]], fill=C["blue"], width=3)
    for p in pts[:pts_shown]:
        draw.ellipse([p[0] - 5, p[1] - 5, p[0] + 5, p[1] + 5], fill=C["blue"], outline=C["white"])
        # value label
        label_i = pts.index(p)
        draw.text((p[0] - 12, p[1] - 20), f"${revenues[label_i]:.0f}K", font=font_code, fill=C["blue"])

    # ── RIGHT: Animated Bar Chart ──────────────────────────────────
    draw_card(draw, 36 + cw + 24, 136, cw, 540, fill=C["white"])
    draw.text((60 + cw + 24, 152), "Revenue by Product (Top 5)", font=font_body_b, fill=C["text"])
    draw.text((60 + cw + 24, 176), "💡 Categorical axis → Bar chart recommended", font=font_code, fill=(2, 132, 199))

    bars = [
        ("Laptop",      56400, (59,  130, 246)),
        ("Monitor",     19800, (99,  102, 241)),
        ("Headphones",  9200,  (139, 92,  246)),
        ("Keyboard",    6450,  (16,  185, 129)),
        ("Mouse",       4150,  (245, 158, 11)),
    ]
    max_v = bars[0][1]
    bar_x0 = 36 + cw + 24 + 48
    max_bw = cw - 100
    bar_top = 230
    bar_step = 68

    for bi, (name, val, col) in enumerate(bars):
        bar_delay = bi * 0.3
        bar_anim  = ease_out(clamp((t - bar_delay) / 0.6))
        bw = int((val / max_v) * max_bw * bar_anim)
        by = bar_top + bi * bar_step
        # label
        draw.text((bar_x0 - 90, by + 8), name, font=font_body_b, fill=C["text"])
        # bar
        if bw > 0:
            draw.rounded_rectangle([bar_x0, by, bar_x0 + bw, by + 36],
                                   radius=6, fill=col)
        # value
        if bar_anim > 0.3:
            draw.text((bar_x0 + bw + 8, by + 8), f"${int(val * bar_anim):,}", font=font_code, fill=C["text"])

    return np.array(frame)


def render_scene_5(t, total_t):
    """Scene 5: 1-Click Cleaning Engine (29–37s)."""
    frame = gradient_bg(C["light_bg"], C["light_mid"])
    draw  = ImageDraw.Draw(frame)
    draw_header(draw, 0.88, "Tab 4 · 1-Click Data Cleaning Engine")

    draw.text((36, 74), "🧹  Automated 1-Click Data Cleaning", font=font_heading, fill=C["text"])
    draw.text((36, 108), "Deduplication  •  Smart Imputation (Median/Mode)  •  1.5×IQR Outlier Clipping  •  Whitespace Sanitization",
              font=font_code, fill=C["slate"])

    # Recipe card
    draw_card(draw, 36, 136, WIDTH - 72, 148, fill=C["white"])
    draw.text((60, 152), "⚙️  Configured Cleaning Recipe", font=font_body_b, fill=C["text"])

    opts = [
        ("✓ Remove Duplicate Rows",        "Purges full-row duplicates"),
        ("✓ Smart Impute Missing Values",   "Numeric: Median  •  Categorical: Mode"),
        ("✓ 1.5×IQR Outlier Winsorization", "Clips anomalies to safe bounds"),
        ("✓ Whitespace Sanitization",       "Strips leading & trailing spaces"),
    ]
    ox = 60
    for oi, (opt, desc) in enumerate(opts):
        delay = oi * 0.3
        a = ease_out(clamp((t - delay) / 0.5))
        oy_base = 190
        oy = int(lerp(oy_base + 20, oy_base, a))
        bw = 265
        draw_card(draw, ox, oy, bw, 68, fill=(248, 250, 252), outline=C["border"])
        draw.text((ox + 12, oy + 10), opt,  font=font_body_b, fill=C["text"])
        draw.text((ox + 12, oy + 34), desc, font=font_code,   fill=C["slate"])
        ox += bw + 16

    # Audit results (green)
    if t > 1.2:
        draw_card(draw, 36, 302, WIDTH - 72, 136, fill=(236, 253, 245), outline=(167, 243, 208))
        draw.text((60, 316), "✅  Cleaning Audit Results", font=font_body_b, fill=(6, 95, 70))
        audit = [
            ("ROWS BEFORE / AFTER", "20  ➔  20"),
            ("DUPLICATES PURGED",   "0 Rows"),
            ("CELLS IMPUTED",       "100% Complete"),
            ("OUTLIERS CLIPPED",    "0 Extreme Bounds"),
        ]
        ax = 60
        for lbl, val in audit:
            draw_card(draw, ax, 348, 265, 72, fill=C["white"], outline=(167, 243, 208))
            draw.text((ax + 12, 358), lbl, font=font_num_sm,  fill=C["slate"])
            draw.text((ax + 12, 378), val, font=font_num_lg,  fill=(4, 120, 87))
            ax += 285

    # Before / After mini table comparison
    if t > 2.4:
        a = ease_out(clamp((t - 2.4) / 0.8))
        # Before panel
        draw_card(draw, 36, 458, (WIDTH - 72 - 24) // 2, 220, fill=C["white"])
        draw.text((60, 472), "Before  ⚠️", font=font_body_b, fill=C["amber"])
        dirty = [
            ["Mouse",    "South",   "NaN",    "$25.00"],
            ["Laptop",   "North",   "12",     "NaN"  ],
            ["Monitor",  "West",    "15",     "$300" ],
            ["Laptop",   "North",   "12",     "$1200"],  # duplicate
        ]
        for ri, row in enumerate(dirty):
            for ci, cell in enumerate(row):
                col_txt = C["amber"] if cell in ("NaN", ) else C["text"]
                draw.text((60 + ci * 120, 500 + ri * 28), cell, font=font_code, fill=col_txt)

        # After panel
        draw_card(draw, 36 + (WIDTH - 72 - 24) // 2 + 24, 458, (WIDTH - 72 - 24) // 2, 220, fill=(236, 253, 245))
        ax2 = 36 + (WIDTH - 72 - 24) // 2 + 24 + 24
        draw.text((ax2, 472), "After  ✅", font=font_body_b, fill=C["emerald"])
        clean = [
            ["Mouse",   "South",   "12",  "$25.00"],
            ["Laptop",  "North",   "12",  "$1200"],
            ["Monitor", "West",    "15",  "$300"],
        ]
        for ri, row in enumerate(clean):
            for ci, cell in enumerate(row):
                draw.text((ax2 + ci * 120, 500 + ri * 28), cell, font=font_code, fill=(4, 120, 87))

    # Action buttons
    if t > 3.2:
        draw.rounded_rectangle([36, HEIGHT - 55, 290, HEIGHT - 15], radius=8, fill=C["emerald"])
        draw.text((52, HEIGHT - 44), "📥  Download Cleaned CSV", font=font_body_b, fill=C["white"])
        draw.rounded_rectangle([310, HEIGHT - 55, 590, HEIGHT - 15], radius=8, fill=C["violet"])
        draw.text((326, HEIGHT - 44), "🔄  Re-Profile Dashboard", font=font_body_b, fill=C["white"])

    return np.array(frame)


def render_scene_6(t, total_t):
    """Scene 6: Outro & CTA (37–44s)."""
    frame = gradient_bg(C["dark_bg"], C["dark_mid"])
    draw  = ImageDraw.Draw(frame)

    star_field(draw, seed=13, count=180, t=t)

    cy = int(HEIGHT * 0.38)

    # Pulsing ring around diamond
    pulse = 0.5 + 0.5 * math.sin(t * 2.5)
    for r in range(100, 20, -15):
        a_val = int(15 * pulse * (1 - r / 100))
        draw.ellipse([WIDTH // 2 - r, cy - 90 - r, WIDTH // 2 + r, cy - 90 + r],
                     fill=(int(C["sky"][0] * a_val / 255),
                           int(C["sky"][1] * a_val / 255),
                           int(C["sky"][2] * a_val / 255)))

    draw.text((WIDTH // 2 - 20, cy - 110), "💎", font=font_heading, fill=C["sky"])

    title = "Crystallytics"
    tw = draw.textlength(title, font=font_hero)
    a_title = ease_out(clamp(t / 1.0))
    draw.text((WIDTH // 2 - tw // 2, cy - 50),
              title, font=font_hero,
              fill=(int(255 * a_title), int(255 * a_title), int(255 * a_title)))

    if t > 0.8:
        sub = "Crystallize your data  •  Tally the truth"
        sw = draw.textlength(sub, font=font_heading)
        a2 = ease_out(clamp((t - 0.8) / 0.8))
        draw.text((WIDTH // 2 - sw // 2, cy + 20), sub, font=font_heading,
                  fill=(int(C["sky"][0] * a2), int(C["sky"][1] * a2), int(C["sky"][2] * a2)))

    # Links card
    if t > 1.5:
        a3 = ease_out(clamp((t - 1.5) / 1.0))
        card_w = 760
        draw_card(draw, WIDTH // 2 - card_w // 2, cy + 72, card_w, 170,
                  fill=(22, 28, 52), outline=C["sky"], radius=14, width=2)

        draw.text((WIDTH // 2 - card_w // 2 + 24, cy + 92),
                  "🌐  Live Interactive Demo:", font=font_body_b, fill=C["white"])
        draw.text((WIDTH // 2 - card_w // 2 + 24, cy + 118),
                  "https://starlyre.github.io/Crystallytics/", font=font_sub, fill=C["sky"])

        draw.text((WIDTH // 2 - card_w // 2 + 24, cy + 160),
                  "💻  Open-Source Code:", font=font_body_b, fill=C["white"])
        draw.text((WIDTH // 2 - card_w // 2 + 24, cy + 186),
                  "https://github.com/Starlyre/Crystallytics", font=font_sub, fill=C["emerald"])

    # Feature pills
    if t > 2.6:
        a4 = ease_out(clamp((t - 2.6) / 0.8))
        features = ["Python 3.11", "JavaScript ES2024", "Chart.js", "Gemini 2.5 Flash",
                    "Streamlit", "ISO/IEC 25010", "Zero Hallucination"]
        total_w = sum(int(draw.textlength(f, font=font_code)) + 24 for f in features) + 12 * (len(features) - 1)
        fx = (WIDTH - total_w) // 2
        for feat in features:
            fw = int(draw.textlength(feat, font=font_code)) + 24
            draw.rounded_rectangle([fx, HEIGHT - 72, fx + fw, HEIGHT - 44],
                                   radius=12, fill=(30, 41, 59), outline=(51, 65, 85))
            draw.text((fx + 12, HEIGHT - 65), feat, font=font_code,
                      fill=(int(C["sky"][0] * a4), int(C["sky"][1] * a4), int(C["sky"][2] * a4)))
            fx += fw + 12

    # Author footer
    foot = "Built by Tom Tuazon  •  github.com/Starlyre  •  #Python #DataAnalytics #AI #GoogleAntigravity"
    fw = draw.textlength(foot, font=font_code)
    draw.text((WIDTH // 2 - fw // 2, HEIGHT - 26), foot, font=font_code, fill=(71, 85, 105))

    return np.array(frame)


# ── Fade transition frames ────────────────────────────────────────────────────
FADE_FRAMES = int(0.5 * FPS)   # 12 frames = 0.5-second cross-fade through black


def fade_out_frames(scene_func, duration, scene_start_t=None):
    """Yield numpy frames for a scene then fade to black over FADE_FRAMES."""
    total_t = duration
    n = int(duration * FPS)
    frames = []
    for f in range(n):
        t = f / FPS
        arr = scene_func(t, total_t)
        # Last FADE_FRAMES: blend to black
        if f >= n - FADE_FRAMES:
            alpha = 1.0 - (f - (n - FADE_FRAMES)) / FADE_FRAMES
            arr = apply_fade(arr, alpha)
        frames.append(arr)
    return frames


def fade_in_frames(frames):
    """Apply fade-in-from-black to the first FADE_FRAMES of a frame list."""
    for i in range(min(FADE_FRAMES, len(frames))):
        alpha = i / FADE_FRAMES
        frames[i] = apply_fade(frames[i], alpha)
    return frames


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    output_path = "crystallytics_showcase_v2.mp4"
    print(f"[VIDEO] Rendering enhanced 720p HD showcase -> {output_path}")
    print(f"    Resolution: {WIDTH}x{HEIGHT}  FPS: {FPS}")

    scenes = [
        (render_scene_1, 7.0),   # Hero
        (render_scene_2, 8.0),   # Data Ingestion
        (render_scene_3, 9.0),   # AI Narrative
        (render_scene_4, 9.0),   # Charts (animated)
        (render_scene_5, 9.0),   # Cleaning Engine
        (render_scene_6, 7.0),   # Outro CTA
    ]

    total_duration = sum(d for _, d in scenes)
    total_frames   = int(total_duration * FPS)
    print(f"    Total: {total_duration:.0f}s  {total_frames} frames\n")

    writer = imageio.get_writer(output_path, fps=FPS, codec="libx264", quality=9,
                                ffmpeg_params=["-preset", "slow", "-crf", "18"])

    written = 0
    for si, (func, dur) in enumerate(scenes, 1):
        print(f"  Scene {si}/{len(scenes)} : {func.__doc__.split('(')[0].strip()} ({dur:.0f}s)...")
        all_frames = fade_out_frames(func, dur)
        all_frames = fade_in_frames(all_frames)
        for arr in all_frames:
            writer.append_data(arr)
            written += 1
            if written % 60 == 0:
                pct = written / total_frames * 100
                print(f"    {written}/{total_frames} frames  ({pct:.0f}%)")

    writer.close()
    mb = os.path.getsize(output_path) / 1024 / 1024
    print(f"\n[DONE]  {output_path}  ({mb:.2f} MB)")
    print(f"    Total rendered: {written} frames")


if __name__ == "__main__":
    main()
