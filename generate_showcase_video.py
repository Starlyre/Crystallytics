"""
generate_showcase_video.py

Generates a professional 720p HD MP4 video showcase of Crystallytics
ready to post on LinkedIn and social media.
"""

import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import imageio

WIDTH = 1280
HEIGHT = 720
FPS = 24

FONT_DIR = "C:/Windows/Fonts"
font_title = ImageFont.truetype(f"{FONT_DIR}/segoeuib.ttf", 46)
font_heading = ImageFont.truetype(f"{FONT_DIR}/segoeuib.ttf", 30)
font_sub = ImageFont.truetype(f"{FONT_DIR}/segoeui.ttf", 20)
font_body = ImageFont.truetype(f"{FONT_DIR}/segoeui.ttf", 17)
font_body_bold = ImageFont.truetype(f"{FONT_DIR}/segoeuib.ttf", 17)
font_code = ImageFont.truetype(f"{FONT_DIR}/consola.ttf", 15)
font_metric_val = ImageFont.truetype(f"{FONT_DIR}/segoeuib.ttf", 32)
font_metric_lbl = ImageFont.truetype(f"{FONT_DIR}/segoeuib.ttf", 13)


def create_gradient_bg(color1, color2):
    """Creates a vertical gradient background."""
    base = Image.new("RGB", (WIDTH, HEIGHT), color1)
    top = Image.new("RGB", (WIDTH, HEIGHT), color2)
    mask = Image.new("L", (WIDTH, HEIGHT))
    mask_data = []
    for y in range(HEIGHT):
        mask_data.extend([int(255 * (y / HEIGHT))] * WIDTH)
    mask.putdata(mask_data)
    base.paste(top, (0, 0), mask)
    return base


def draw_card(draw, x, y, w, h, fill="#FFFFFF", outline="#E2E8F0", radius=12):
    draw.rounded_rectangle([x, y, x + w, y + h], radius=radius, fill=fill, outline=outline, width=1)


def draw_header(draw, progress):
    """Draws top navigation bar."""
    draw.rectangle([0, 0, WIDTH, 60], fill="#0F172A")
    draw.text((30, 16), "💎 Crystallytics", font=font_heading, fill="#FFFFFF")
    draw.text((220, 22), "Context-Aware Automated Analytics", font=font_sub, fill="#94A3B8")

    # Badges
    badges = ["ISO/IEC 25010", "ISO/IEC 27001", "⚡ Built with Google Antigravity"]
    bx = WIDTH - 480
    for b in badges:
        bw = draw.textlength(b, font=font_code) + 16
        draw.rounded_rectangle([bx, 18, bx + bw, 42], radius=6, fill="#1E293B", outline="#334155")
        draw.text((bx + 8, 22), b, font=font_code, fill="#38BDF8")
        bx += bw + 8

    # Progress bar at top
    draw.rectangle([0, 58, int(WIDTH * progress), 60], fill="#00C6FF")


def render_scene_1(t, total_t):
    """Scene 1: Hero Splash Screen (0 - 4s)"""
    frame = create_gradient_bg((11, 15, 25), (30, 27, 75))
    draw = ImageDraw.Draw(frame)

    # Ambient glow circles
    glow_alpha = math.sin((t / total_t) * math.pi)
    center_y = int(HEIGHT * 0.42)

    # Diamond symbol
    draw.text((WIDTH // 2 - 40, center_y - 120), "💎", font=ImageFont.truetype(f"{FONT_DIR}/segoeui.ttf", 72), fill="#38BDF8")

    # Hero Title
    title_text = "Crystallytics"
    tw = draw.textlength(title_text, font=font_title)
    draw.text((WIDTH // 2 - tw // 2, center_y - 20), title_text, font=font_title, fill="#FFFFFF")

    # Subtitle
    sub_text = "AI-Powered, Context-Aware Automated Data Analytics"
    sw = draw.textlength(sub_text, font=font_heading)
    draw.text((WIDTH // 2 - sw // 2, center_y + 45), sub_text, font=font_heading, fill="#38BDF8")

    tag_text = "Crystallize your data • Tally the truth • Zero Hallucinations"
    tgw = draw.textlength(tag_text, font=font_sub)
    draw.text((WIDTH // 2 - tgw // 2, center_y + 95), tag_text, font=font_sub, fill="#94A3B8")

    # Pill Badges
    pills = ["ISO/IEC 25010 Quality Model", "ISO/IEC 27001 Zero-Retention", "⚡ Engineered with Google Antigravity"]
    total_w = sum(draw.textlength(p, font=font_body) + 30 for p in pills)
    px = (WIDTH - total_w) // 2
    for p in pills:
        pw = draw.textlength(p, font=font_body) + 24
        draw.rounded_rectangle([px, center_y + 155, px + pw, center_y + 195], radius=20, fill="#1E293B", outline="#0284C7", width=1)
        draw.text((px + 12, center_y + 164), p, font=font_body, fill="#E2E8F0")
        px += pw + 12

    return np.array(frame)


def render_scene_2(t, total_t):
    """Scene 2: Ingestion & 5 Health Metrics (4 - 10s)"""
    frame = create_gradient_bg((248, 250, 252), (241, 245, 249))
    draw = ImageDraw.Draw(frame)
    draw_header(draw, 0.25)

    # Ingestion Banner
    draw_card(draw, 40, 85, WIDTH - 80, 65, fill="#FFFFFF", outline="#CBD5E1")
    draw.text((65, 105), "📁 Loaded Dataset:", font=font_body_bold, fill="#0F172A")
    draw.text((215, 105), "sample_sales.csv (20 Rows, 7 Columns, UTF-8 In-Memory)", font=font_code, fill="#0284C7")
    draw.rounded_rectangle([WIDTH - 210, 98, WIDTH - 60, 138], radius=8, fill="#10B981")
    draw.text((WIDTH - 195, 107), "✓ Ingested 100%", font=font_body_bold, fill="#FFFFFF")

    # 5 Health Metric Cards
    metrics = [
        ("TOTAL ROWS", "20", "● Complete", "#10B981"),
        ("COLUMNS", "7", "● 4 Numeric", "#3B82F6"),
        ("MISSING CELLS", "0", "0.0% Missing", "#10B981"),
        ("DUPLICATES", "0", "0.0% Dupes", "#10B981"),
        ("MEMORY USAGE", "1.4 KB", "Client RAM", "#8B5CF6")
    ]

    card_w = (WIDTH - 80 - (4 * 16)) // 5
    for i, (lbl, val, sub, col) in enumerate(metrics):
        cx = 40 + i * (card_w + 16)
        draw_card(draw, cx, 170, card_w, 110, fill="#FFFFFF")
        draw.text((cx + 18, 185), lbl, font=font_metric_lbl, fill="#64748B")
        draw.text((cx + 18, 205), val, font=font_metric_val, fill="#0F172A")
        draw.text((cx + 18, 252), sub, font=font_metric_lbl, fill=col)

    # Inferred Domain Card
    draw_card(draw, 40, 305, WIDTH - 80, 105, fill="#EFF6FF", outline="#BFDBFE")
    draw.text((65, 320), "🧠 INFERRED SUBJECT CONTEXT", font=font_metric_lbl, fill="#1D4ED8")
    draw.text((65, 342), "Sales & Commercial", font=font_heading, fill="#1E293B")
    draw.text((365, 350), "(Confidence: High)", font=font_sub, fill="#4F46E5")
    draw.text((65, 380), "Detected Signals: revenue, product, unit, sale, orders", font=font_code, fill="#64748B")
    draw.rounded_rectangle([WIDTH - 240, 335, WIDTH - 65, 375], radius=6, fill="#ECFDF5", outline="#A7F3D0")
    draw.text((WIDTH - 225, 345), "🛡️ ISO 27001 Memory Stream", font=font_code, fill="#047857")

    # Lower Teaser Tabs
    tabs = ["🤖 AI Narrative & Insights", "📈 Automated Visualizations", "📋 Data Health", "🧹 1-Click Cleaning"]
    tx = 40
    for idx, tab_name in enumerate(tabs):
        active = (idx == 0)
        tw = draw.textlength(tab_name, font=font_body_bold) + 24
        if active:
            draw.line([(tx, 455), (tx + tw, 455)], fill="#0072FF", width=3)
        draw.text((tx + 12, 430), tab_name, font=font_body_bold, fill="#0072FF" if active else "#64748B")
        tx += tw + 10

    # Preview card
    draw_card(draw, 40, 470, WIDTH - 80, 220, fill="#FFFFFF")
    draw.text((65, 490), "Previewing Ingested Data Stream (First 5 Rows)", font=font_body_bold, fill="#0F172A")
    rows = [
        "2024-01-01 | Laptop     | North | Units: 12 | Price: $1200.00 | Rating: 4.5 | Revenue: $14,400.00",
        "2024-01-02 | Mouse      | South | Units: 45 | Price: $25.00   | Rating: 4.2 | Revenue: $1,125.00",
        "2024-01-03 | Keyboard   | East  | Units: 23 | Price: $75.00   | Rating: 4.8 | Revenue: $1,725.00",
        "2024-01-04 | Monitor    | West  | Units: 15 | Price: $300.00  | Rating: 3.9 | Revenue: $4,500.00",
        "2024-01-05 | Headphones | North | Units: 30 | Price: $80.00   | Rating: 4.6 | Revenue: $2,400.00",
    ]
    for r_idx, r in enumerate(rows):
        draw.text((65, 525 + r_idx * 30), r, font=font_code, fill="#334155")

    return np.array(frame)


def render_scene_3(t, total_t):
    """Scene 3: AI Narrative & Zero-Hallucination Insights (10 - 18s)"""
    frame = create_gradient_bg((248, 250, 252), (241, 245, 249))
    draw = ImageDraw.Draw(frame)
    draw_header(draw, 0.50)

    # Active Tab Header
    draw.text((40, 80), "🤖 Executive AI Narrative & Verified Insights", font=font_heading, fill="#0F172A")
    draw.text((40, 115), "Inference Engine: Google Gemini 2.5 Flash • Validated via Pydantic Schema", font=font_code, fill="#64748B")

    # Executive Summary Card
    draw_card(draw, 40, 145, WIDTH - 80, 100, fill="#FFFFFF", outline="#E2E8F0")
    draw.text((65, 160), "📋 Executive Summary", font=font_body_bold, fill="#0F172A")
    exec_p = "This dataset contains 20 transaction records across 7 columns classified as 'Sales & Commercial'. Total volume amounts to $96,005 with zero missing values and consistent high customer satisfaction ratings (avg 4.4/5.0)."
    draw.text((65, 190), exec_p, font=font_body, fill="#334155")

    # 4 Insight Columns (2x2 grid)
    gw = (WIDTH - 80 - 20) // 2
    gh = 175

    # 1. Key Findings (Green)
    draw_card(draw, 40, 265, gw, gh, fill="#FFFFFF")
    draw.rectangle([40, 265, 46, 265 + gh], fill="#10B981")
    draw.text((60, 280), "🎯 Key Verified Findings", font=font_body_bold, fill="#0F172A")
    draw.text((60, 310), "• Top Contributor: 'Laptop' leads revenue with $56,400 (58.7%).", font=font_body, fill="#334155")
    draw.text((60, 340), "• Volume Leader: 'Mouse' leads in units sold (183 units total).", font=font_body, fill="#334155")
    draw.text((60, 370), "• High-Margin Segment: North Region accounts for 32% of profit.", font=font_body, fill="#334155")

    # 2. Trends (Blue)
    draw_card(draw, 40 + gw + 20, 265, gw, gh, fill="#FFFFFF")
    draw.rectangle([40 + gw + 20, 265, 46 + gw + 20, 265 + gh], fill="#3B82F6")
    draw.text((60 + gw + 20, 280), "📈 Observed Trends", font=font_body_bold, fill="#0F172A")
    draw.text((60 + gw + 20, 310), "• Steady chronological sales volume across all 20 time steps.", font=font_body, fill="#334155")
    draw.text((60 + gw + 20, 340), "• Customer satisfaction strongly correlates with product quality.", font=font_body, fill="#334155")
    draw.text((60 + gw + 20, 370), "• Balanced regional diversification across North, South, East, West.", font=font_body, fill="#334155")

    # 3. Anomalies (Amber)
    draw_card(draw, 40, 460, gw, gh, fill="#FFFFFF")
    draw.rectangle([40, 460, 46, 460 + gh], fill="#F59E0B")
    draw.text((60, 475), "🔍 Potential Anomalies (1.5×IQR)", font=font_body_bold, fill="#0F172A")
    draw.text((60, 505), "• 1.5×IQR Outlier Scan: 0 severe anomalies detected in Revenue.", font=font_body, fill="#334155")
    draw.text((60, 535), "• Rating dispersion falls safely within normal standard deviations.", font=font_body, fill="#334155")
    draw.text((60, 565), "• No extreme revenue spikes identified outside statistical bounds.", font=font_body, fill="#334155")

    # 4. Actionable Next Steps (Purple)
    draw_card(draw, 40 + gw + 20, 460, gw, gh, fill="#FFFFFF")
    draw.rectangle([40 + gw + 20, 460, 46 + gw + 20, 460 + gh], fill="#8B5CF6")
    draw.text((60 + gw + 20, 475), "🚀 Recommended Next Steps", font=font_body_bold, fill="#0F172A")
    draw.text((60 + gw + 20, 505), "1. Investigate customer rating dynamics for Monitor segment.", font=font_body, fill="#334155")
    draw.text((60 + gw + 20, 535), "2. Test predictive elasticity on Mouse unit sales pricing.", font=font_body, fill="#334155")
    draw.text((60 + gw + 20, 565), "3. Export executive audit report (.md) for team review.", font=font_body, fill="#334155")

    # Export Button Bottom Left
    draw.rounded_rectangle([40, 650, 320, 690], radius=8, fill="#0072FF")
    draw.text((55, 660), "📥 Download Audit Report (.md)", font=font_body_bold, fill="#FFFFFF")

    return np.array(frame)


def render_scene_4(t, total_t):
    """Scene 4: Automated Visualizations & Chart.js (18 - 25s)"""
    frame = create_gradient_bg((248, 250, 252), (241, 245, 249))
    draw = ImageDraw.Draw(frame)
    draw_header(draw, 0.70)

    draw.text((40, 80), "📈 Automated Visualizations & Contextual Charts", font=font_heading, fill="#0F172A")
    draw.text((40, 115), "Charts automatically recommended with mathematical rationale cards", font=font_code, fill="#64748B")

    # Two Chart Cards
    cw = (WIDTH - 80 - 24) // 2

    # Left Chart: Line Trend
    draw_card(draw, 40, 150, cw, 480, fill="#FFFFFF")
    draw.text((65, 170), "Trend of Revenue over Date", font=font_body_bold, fill="#0F172A")
    draw.text((65, 195), "💡 Why this chart: Tracks chronological metric over Datetime", font=font_code, fill="#0284C7")

    # Draw Line Graph Simulation
    pts = [(90, 480), (140, 430), (190, 460), (240, 380), (290, 410), (340, 320), (390, 350), (440, 290), (490, 310), (540, 260), (590, 280)]
    for i in range(len(pts) - 1):
        draw.line([pts[i], pts[i + 1]], fill="#0072FF", width=4)
        draw.ellipse([pts[i][0] - 4, pts[i][1] - 4, pts[i][0] + 4, pts[i][1] + 4], fill="#00C6FF", outline="#0072FF")

    # Right Chart: Categorical Bar Chart
    draw_card(draw, 40 + cw + 24, 150, cw, 480, fill="#FFFFFF")
    draw.text((65 + cw + 24, 170), "Revenue by Product (Top 5)", font=font_body_bold, fill="#0F172A")
    draw.text((65 + cw + 24, 195), "💡 Why this chart: Compares metric sums across Categorical segments", font=font_code, fill="#0284C7")

    # Draw Bar Graph Simulation
    bars = [("Laptop", 56400, "#3B82F6"), ("Monitor", 19800, "#60A5FA"), ("Headphones", 9200, "#93C5FD"), ("Keyboard", 6450, "#BFDBFE"), ("Mouse", 4150, "#DBEAFE")]
    max_v = 56400
    by = 240
    for name, val, col in bars:
        draw.text((65 + cw + 24, by), name, font=font_body, fill="#334155")
        bw = int((val / max_v) * 320)
        draw.rounded_rectangle([190 + cw + 24, by, 190 + cw + 24 + bw, by + 26], radius=6, fill=col)
        draw.text((200 + cw + 24 + bw + 10, by + 3), f"${val:,}", font=font_code, fill="#0F172A")
        by += 65

    return np.array(frame)


def render_scene_5(t, total_t):
    """Scene 5: 1-Click Data Cleaning Engine (25 - 32s)"""
    frame = create_gradient_bg((248, 250, 252), (241, 245, 249))
    draw = ImageDraw.Draw(frame)
    draw_header(draw, 0.88)

    draw.text((40, 80), "🧹 1-Click Automated Data Cleaning Engine", font=font_heading, fill="#0F172A")
    draw.text((40, 115), "Instant deduplication, smart imputation (median/mean/mode), and 1.5×IQR outlier clipping", font=font_code, fill="#64748B")

    # Cleaning Recipe Card
    draw_card(draw, 40, 150, WIDTH - 80, 160, fill="#FFFFFF")
    draw.text((65, 170), "Configured Cleaning Recipe", font=font_body_bold, fill="#0F172A")

    options = [
        ("✓ Remove Exact Duplicate Rows", "Purges full-row duplicates across all dimensions"),
        ("✓ Smart Impute Missing Values", "Numeric: Median, Categorical: Mode"),
        ("✓ 1.5×IQR Outlier Winsorization", "Clips extreme anomalies into normal distribution bounds"),
        ("✓ String Whitespace Sanitization", "Strips leading and trailing spaces from text columns")
    ]

    ox = 65
    for opt, desc in options:
        draw.rounded_rectangle([ox, 210, ox + 270, 285], radius=8, fill="#F8FAFC", outline="#E2E8F0")
        draw.text((ox + 12, 222), opt, font=font_body_bold, fill="#0F172A")
        draw.text((ox + 12, 248), desc, font=font_metric_lbl, fill="#64748B")
        ox += 285

    # Audit Metrics Matrix
    draw_card(draw, 40, 330, WIDTH - 80, 140, fill="#ECFDF5", outline="#A7F3D0")
    draw.text((65, 345), "✅ Cleaning Audit Results", font=font_body_bold, fill="#065F46")

    audit_stats = [
        ("ROWS BEFORE / AFTER", "20 ➔ 20"),
        ("DUPLICATES PURGED", "0 Rows"),
        ("MISSING CELLS IMPUTED", "100% Complete"),
        ("OUTLIERS NORMALIZED", "0 Extreme Bounds")
    ]
    ax = 65
    for lbl, val in audit_stats:
        draw.rounded_rectangle([ax, 375, ax + 265, 445], radius=8, fill="#FFFFFF", outline="#A7F3D0")
        draw.text((ax + 15, 385), lbl, font=font_metric_lbl, fill="#64748B")
        draw.text((ax + 15, 405), val, font=font_metric_val, fill="#047857")
        ax += 285

    # Action Buttons
    draw.rounded_rectangle([40, 495, 290, 545], radius=8, fill="#10B981")
    draw.text((60, 510), "📥 Download Cleaned CSV", font=font_body_bold, fill="#FFFFFF")

    draw.rounded_rectangle([310, 495, 620, 545], radius=8, fill="#8B5CF6")
    draw.text((330, 510), "🔄 Re-profile Live Dashboard", font=font_body_bold, fill="#FFFFFF")

    return np.array(frame)


def render_scene_6(t, total_t):
    """Scene 6: Outro & Call to Action (32 - 38s)"""
    frame = create_gradient_bg((11, 15, 25), (30, 27, 75))
    draw = ImageDraw.Draw(frame)

    cy = int(HEIGHT * 0.40)
    draw.text((WIDTH // 2 - 40, cy - 110), "💎", font=ImageFont.truetype(f"{FONT_DIR}/segoeui.ttf", 64), fill="#38BDF8")

    title_text = "Crystallytics"
    tw = draw.textlength(title_text, font=font_title)
    draw.text((WIDTH // 2 - tw // 2, cy - 25), title_text, font=font_title, fill="#FFFFFF")

    sub_text = "Crystallize your datasets with verifiable AI analytics."
    sw = draw.textlength(sub_text, font=font_heading)
    draw.text((WIDTH // 2 - sw // 2, cy + 35), sub_text, font=font_heading, fill="#38BDF8")

    # Links Card
    draw_card(draw, WIDTH // 2 - 360, cy + 95, 720, 160, fill="#1E293B", outline="#38BDF8")

    draw.text((WIDTH // 2 - 320, cy + 120), "🌐 Interactive Live Demo (Runs in Browser):", font=font_body_bold, fill="#FFFFFF")
    draw.text((WIDTH // 2 - 320, cy + 145), "https://starlyre.github.io/Crystallytics/", font=font_sub, fill="#38BDF8")

    draw.text((WIDTH // 2 - 320, cy + 185), "💻 Open-Source Code on GitHub:", font=font_body_bold, fill="#FFFFFF")
    draw.text((WIDTH // 2 - 320, cy + 210), "https://github.com/Starlyre/Crystallytics", font=font_sub, fill="#10B981")

    # Footer
    foot = "Built with Python 3.11, JavaScript & Google Antigravity • ISO/IEC 25010 Standards"
    fw = draw.textlength(foot, font=font_code)
    draw.text((WIDTH // 2 - fw // 2, HEIGHT - 45), foot, font=font_code, fill="#64748B")

    return np.array(frame)


def main():
    output_path = "crystallytics_showcase.mp4"
    print(f"Rendering 720p HD showcase video to {output_path}...")

    # Scenes: (render_func, duration_in_seconds)
    scenes = [
        (render_scene_1, 5.0),
        (render_scene_2, 6.0),
        (render_scene_3, 8.0),
        (render_scene_4, 7.0),
        (render_scene_5, 7.0),
        (render_scene_6, 6.0),
    ]

    total_duration = sum(dur for _, dur in scenes)
    total_frames = int(total_duration * FPS)
    print(f"Total duration: {total_duration:.1f}s ({total_frames} frames at {FPS} FPS)")

    writer = imageio.get_writer(output_path, fps=FPS, codec="libx264", quality=8)

    frame_count = 0
    for scene_idx, (scene_func, duration) in enumerate(scenes, 1):
        num_frames = int(duration * FPS)
        for f in range(num_frames):
            t = f / FPS
            img_arr = scene_func(t, duration)
            writer.append_data(img_arr)
            frame_count += 1
            if frame_count % 50 == 0:
                print(f"Progress: {frame_count}/{total_frames} frames ({(frame_count/total_frames)*100:.1f}%)")

    writer.close()
    file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"Video rendering complete! File saved: {output_path} ({file_size_mb:.2f} MB)")


if __name__ == "__main__":
    main()
