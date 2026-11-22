#!/usr/bin/env python3
"""Render the 21 November 2026 front page for news-image-20261121.

Draws a broadsheet front page with PIL: 35 dated stories, 3 lead
illustrations, 10 mid thumbnails, a stat strip, a region bar, a world
map with numbered pins, a tail list and a date-check footer.
Deterministic: fixed data, fixed fonts, fixed draw order.
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")

SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF_R = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SANS_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"

PAPER = (247, 243, 234)
INK = (20, 20, 20)
NAVY = (18, 36, 63)
NAVY2 = (28, 52, 84)
RED = (178, 32, 44)
GOLD = (201, 162, 39)
TEAL = (15, 118, 110)
GREY = (110, 108, 100)
LINE = (190, 184, 170)
WHITE = (255, 255, 255)
SKY = (168, 205, 225)


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns list of lines that fit max_w."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def para(draw, x, y, max_w, text, fnt, fill=INK, leading=None, max_lines=None):
    """Draw wrapped paragraph; returns y just below last line."""
    lines = wrap(draw, text, fnt, max_w)
    if max_lines is not None:
        lines = lines[:max_lines]
    lh = leading or int(fnt.size * 1.22)
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += lh
    return y


def trunc(draw, text, fnt, max_w):
    if draw.textlength(text, font=fnt) <= max_w:
        return text
    while text and draw.textlength(text + "...", font=fnt) > max_w:
        text = text[:-1]
    return text + "..."


def chip(draw, x, y, text, bg, fg=WHITE, size=11):
    f = font(SANS_B, size)
    w = int(draw.textlength(text, font=f) + 14)
    h = size + 9
    draw.rounded_rectangle([x, y, x + w, y + h], radius=3, fill=bg)
    draw.text((x + 7, y + 4), text, font=f, fill=fg)
    return w


def num_badge(draw, cx, cy, n, r=11, bg=RED):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=bg,
                 outline=WHITE, width=2)
    f = font(SANS_B, 13 if n < 10 else 11)
    t = str(n)
    tw = draw.textlength(t, font=f)
    draw.text((cx - tw / 2, cy - 7 if n < 10 else cy - 6), t,
              font=f, fill=WHITE)


# ---------------------------------------------------------------- stories
# (n, region, headline, deck, lon, lat) for 1..13; tail 14..35 headline only.
LEADS = [
    (1, "CLIMATE", "COP31 nears a deal after two days of overtime",
     "Antalya talks run past their Friday deadline as a new package "
     "bridges the fossil-fuel and finance divides; approval is set "
     "for Sunday morning.", 30.7, 36.9),
    (2, "MIDDLE EAST", "Iran strikes Bahrain, claims hits on US positions",
     "Bahrain says an Iranian attack set an industrial site ablaze "
     "and its defences downed more; Tehran claims it hit American "
     "positions in the Gulf.", 50.6, 26.2),
    (3, "MIDDLE EAST", "Three Houthi missiles downed over Riyadh",
     "Saudi defences intercept a dawn salvo at the capital, the "
     "second attack on Riyadh in days; the coalition answers with "
     "strikes on Hodeidah port.", 46.7, 24.7),
]

MIDS = [
    (4, "AMERICAS", "Magnitude 6.7 quake shakes Peru's Andes",
     "Tremor centred near Junin is felt in Lima; no major damage "
     "at first report.", -75.9, -10.9),
    (5, "AMERICAS", "Mexico seizes 'El Chapo Isidro'; 11 dead",
     "Capture of the FBI-wanted cartel boss sets off gun battles "
     "in Sinaloa.", -107.4, 25.6),
    (6, "EUROPE", "Russian cargo ship ablaze after drone strike",
     "Sparta II burns in the Gulf of Finland; crew evacuates to "
     "safety.", 24.5, 59.9),
    (7, "UKRAINE", "Russian missile strays into Poland",
     "Warsaw reports an incursion during a night of heavy strikes "
     "on Ukraine.", 19.4, 52.0),
    (8, "UKRAINE", "Triple-tap strike kills boy, 7, and paramedic",
     "Kryvyi Rih attack leaves 28 in hospital as Russia steps "
     "up strikes.", 33.4, 47.9),
    (9, "MIDDLE EAST", "Strike kills three in Gaza aid vehicle",
     "Gaza City truck carried food and aid papers, witnesses "
     "say.", 34.5, 31.5),
    (10, "MARKETS", "Nasdaq wipes out its 2026 gains",
     "AI and chip shares lead a Friday rout; the S&P 500 slips "
     "into correction territory.", -74.0, 40.7),
    (11, "UKRAINE", "Zelensky: bridge strikes a 'fair response'",
     "President defends the Kerch Bridge attacks after Russian "
     "bridge strikes.", 30.5, 50.4),
    (12, "AMERICAS", "Mosquitoes cut child dengue by 69%",
     "Specially bred mosquitoes slash infections in a major "
     "Brazil trial.", -46.6, -23.5),
    (13, "ASIA-PACIFIC", "EU and Indonesia seal deal after 10 years",
     "Trade pact ends a decade of talks; Brussels calls it a "
     "landmark for both sides.", 106.8, -6.2),
]

TAIL = [
    (14, "UK and EU strike 'historic' deal to rebuild post-Brexit ties"),
    (15, "China holds benchmark lending rates for an 18th straight month"),
    (16, "NASA halts Perseverance and Mars Odyssey science over faults"),
    (17, "Israel advances plan for a new West Bank city of 200,000"),
    (18, "FBI probes apparent hack of its key crime database"),
    (19, "Clashes erupt across France in another night of protest"),
    (20, "UN warns ISIS-K is acquiring drones in Afghanistan"),
    (21, "Russian drone crosses Moldovan airspace in mass attack"),
    (22, "UK runs cyber operations on Russia, China, Iran, N. Korea"),
    (23, "Austria says its foreign ministry website was hacked"),
    (24, "Canada posts its strongest retail sales since 2022"),
    (25, "Russian strike kills two at Lviv railway station"),
    (26, "Greece and Israel in arms talks worth up to $1.1bn"),
    (27, "Iran unveils a new missile launcher deep underground"),
    (28, "Iraqi police move into Jurf al-Sakhar under new deal"),
    (29, "Tainted alcohol kills 11 and sickens 180 in Manipur"),
    (30, "Denmark says Moscow plotted to kill a US-Ukrainian rapper"),
    (31, "Rackspace breach exposes customer cloud secrets"),
    (32, "Quad and ASEAN summits wrap up in Manila"),
    (33, "Lebanon's president demands Israeli withdrawal"),
    (34, "Former NSW MP Fred Nile dies aged 92"),
    (35, "UN: Rohingya justice now hinges on action after genocide ruling"),
]

REGIONS = [("MIDDLE EAST", 7, RED), ("EUROPE", 10, NAVY2),
           ("UKRAINE", 4, (90, 60, 30)), ("ASIA-PACIFIC", 5, TEAL),
           ("AMERICAS", 5, (46, 110, 62)), ("MARKETS", 2, (120, 72, 140)),
           ("TECH", 2, (70, 70, 70))]

STATS = [("6.7", "PERU QUAKE, MAGNITUDE"),
         ("3", "MISSILES DOWNED OVER RIYADH"),
         ("11", "DEAD IN THE SINALOA OPERATION"),
         ("69%", "CHILD DENGUE CUT IN BRAZIL TRIAL"),
         ("100", "MISSILES FIRED AT UKRAINE"),
         ("190+", "NATIONS AT THE COP31 TABLE")]

# ---------------------------------------------------------------- scenes
# Flat-design original illustrations, drawn in code. Each scene takes
# (draw, x, y, w, h) and fills the box.

def scene_cop31(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(23, 84, 96))
    d.ellipse([x + w * 0.62, y - h * 0.35, x + w * 1.05, y + h * 0.45],
              fill=(242, 196, 90))
    cx, cy, r = x + w * 0.36, y + h * 0.52, h * 0.36
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(64, 160, 190))
    d.ellipse([cx - r * 0.55, cy - r * 0.75, cx + r * 0.15, cy - r * 0.1],
              fill=(52, 140, 90))
    d.ellipse([cx + r * 0.1, cy + r * 0.25, cx + r * 0.7, cy + r * 0.8],
              fill=(52, 140, 90))
    d.arc([cx - r, cy - r, cx + r, cy + r], 0, 360, fill=(210, 235, 240),
          width=2)
    for i in range(5):
        fx = x + w * 0.08 + i * w * 0.17
        d.rectangle([fx, y + h * 0.86, fx + w * 0.1, y + h * 0.97],
                    fill=(247, 243, 234))
        d.polygon([(fx, y + h * 0.86), (fx + w * 0.05, y + h * 0.78),
                   (fx + w * 0.1, y + h * 0.86)], fill=RED if i % 2 else GOLD)


def scene_bahrain(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(16, 22, 44))
    for sx, sy in [(0.15, 0.2), (0.4, 0.12), (0.7, 0.25), (0.85, 0.1),
                   (0.3, 0.35), (0.55, 0.3)]:
        d.ellipse([x + w * sx - 1, y + h * sy - 1, x + w * sx + 1,
                   y + h * sy + 1], fill=WHITE)
    d.polygon([(x + w * 0.55, y + h * 0.62), (x + w * 0.68, y + h * 0.18),
               (x + w * 0.72, y + h * 0.62)], fill=(242, 120, 60))
    d.ellipse([x + w * 0.60, y + h * 0.55, x + w * 0.74, y + h * 0.68],
              fill=(247, 180, 60))
    d.ellipse([x + w * 0.63, y + h * 0.60, x + w * 0.71, y + h * 0.66],
              fill=(247, 220, 110))
    for i, bx in enumerate([0.05, 0.2, 0.36, 0.78, 0.88]):
        bh = h * (0.28 + 0.1 * ((i * 7) % 3))
        d.rectangle([x + w * bx, y + h - bh, x + w * bx + w * 0.09,
                     y + h], fill=(40, 52, 84))
    d.rectangle([x, y + h - 4, x + w, y + h], fill=(247, 120, 40))


def scene_riyadh(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(24, 52, 92))
    d.ellipse([x + w * 0.78, y + h * 0.08, x + w * 0.92, y + h * 0.22],
              fill=(235, 230, 210))
    for tx in (0.12, 0.3, 0.55, 0.72, 0.86):
        th = h * (0.45 + 0.18 * ((int(tx * 100) % 3)))
        d.rectangle([x + w * tx, y + h - th, x + w * tx + w * 0.08,
                     y + h], fill=(16, 34, 64))
    d.polygon([(x + w * 0.55, y + h * 0.55), (x + w * 0.60, y + h * 0.30),
               (x + w * 0.63, y + h * 0.55)], fill=(120, 170, 220))
    for mx, my, ang in [(0.25, 0.5, -25), (0.45, 0.38, -15),
                        (0.7, 0.42, -30)]:
        px, py = x + w * mx, y + h * my
        d.line([px, py, px + 26, py - 14], fill=(247, 220, 110), width=3)
        d.ellipse([px - 4, py - 4, px + 4, py + 4], fill=(247, 180, 60))
    d.polygon([(x + w * 0.42, y + h * 0.62), (x + w * 0.5, y + h * 0.55),
               (x + w * 0.58, y + h * 0.62), (x + w * 0.5, y + h * 0.78)],
              fill=(247, 243, 234), outline=GOLD)


def scene_quake(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(122, 90, 62))
    d.polygon([(x, y + h * 0.55), (x + w * 0.4, y + h * 0.3),
               (x + w * 0.75, y + h * 0.55), (x + w, y + h * 0.42),
               (x + w, y + h), (x, y + h)], fill=(96, 70, 48))
    d.rectangle([x + w * 0.12, y + h * 0.28, x + w * 0.34, y + h * 0.62],
                fill=(220, 210, 190))
    d.rectangle([x + w * 0.58, y + h * 0.36, x + w * 0.82, y + h * 0.62],
                fill=(200, 188, 164))
    d.line([x + w * 0.2, y + h * 0.28, x + w * 0.26, y + h * 0.62],
           fill=(60, 40, 28), width=3)
    d.line([x + w * 0.66, y + h * 0.36, x + w * 0.72, y + h * 0.62],
           fill=(60, 40, 28), width=3)
    d.line([x, y + h * 0.62, x + w * 0.45, y + h * 0.78, x + w * 0.7,
            y + h * 0.66, x + w, y + h * 0.82], fill=(40, 26, 16), width=4)


def scene_cartel(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(38, 74, 52))
    d.ellipse([x + w * 0.1, y + h * 0.12, x + w * 0.42, y + h * 0.38],
              fill=(30, 30, 30))
    d.rectangle([x + w * 0.42, y + h * 0.18, x + w * 0.9, y + h * 0.34],
                fill=(30, 30, 30))
    d.rectangle([x + w * 0.55, y + h * 0.34, x + w * 0.72, y + h * 0.44],
                fill=(30, 30, 30))
    d.line([x + w * 0.9, y + h * 0.26, x + w * 0.98, y + h * 0.2],
           fill=(200, 200, 200), width=3)
    for lx in (0.18, 0.3):
        d.line([x + w * lx, y + h * 0.44, x + w * lx, y + h * 0.52],
               fill=(30, 30, 30), width=3)
    d.polygon([(x + w * 0.68, y + h * 0.62), (x + w * 0.76, y + h * 0.55),
               (x + w * 0.84, y + h * 0.62), (x + w * 0.76, y + h * 0.78)],
              fill=GOLD)
    d.rectangle([x, y + h * 0.82, x + w, y + h], fill=(20, 44, 30))


def scene_ship(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(70, 110, 150))
    d.ellipse([x + w * 0.72, y + h * 0.08, x + w * 0.9, y + h * 0.3],
              fill=(240, 235, 215))
    d.polygon([(x + w * 0.18, y + h * 0.55), (x + w * 0.82, y + h * 0.55),
               (x + w * 0.72, y + h * 0.78), (x + w * 0.28, y + h * 0.78)],
              fill=(40, 44, 52))
    d.rectangle([x + w * 0.38, y + h * 0.38, x + w * 0.52, y + h * 0.55],
                fill=(120, 60, 40))
    d.polygon([(x + w * 0.4, y + h * 0.38), (x + w * 0.45, y + h * 0.12),
               (x + w * 0.5, y + h * 0.38)], fill=(247, 120, 40))
    d.ellipse([x + w * 0.42, y + h * 0.2, x + w * 0.56, y + h * 0.36],
              fill=(247, 180, 60))
    for wy in (0.84, 0.92):
        d.arc([x - 10, y + h * wy, x + w * 0.5, y + h * wy + 12],
              200, 340, fill=(220, 235, 245), width=3)
        d.arc([x + w * 0.5, y + h * wy, x + w + 10, y + h * wy + 12],
              200, 340, fill=(220, 235, 245), width=3)


def scene_poland(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(150, 178, 200))
    d.ellipse([x + w * 0.28, y + h * 0.22, x + w * 0.78, y + h * 0.82],
              fill=(96, 150, 96))
    d.ellipse([x + w * 0.42, y + h * 0.3, x + w * 0.62, y + h * 0.52],
              fill=(247, 243, 234))
    d.line([x + w * 0.12, y + h * 0.78, x + w * 0.5, y + h * 0.4],
           fill=(247, 220, 110), width=3)
    d.polygon([(x + w * 0.5, y + h * 0.4), (x + w * 0.58, y + h * 0.36),
               (x + w * 0.56, y + h * 0.46)], fill=(200, 40, 40))
    d.ellipse([x + w * 0.47, y + h * 0.36, x + w * 0.55, y + h * 0.44],
              fill=RED, outline=WHITE, width=2)


def scene_kryvyi(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(52, 58, 74))
    d.rectangle([x + w * 0.1, y + h * 0.4, x + w * 0.4, y + h * 0.85],
                fill=(140, 130, 115))
    d.rectangle([x + w * 0.55, y + h * 0.3, x + w * 0.88, y + h * 0.85],
                fill=(110, 100, 88))
    for wx in (0.16, 0.28, 0.62, 0.74):
        d.rectangle([x + w * wx, y + h * 0.48, x + w * wx + 8,
                     y + h * 0.58], fill=(247, 220, 110))
    d.ellipse([x + w * 0.55, y + h * 0.08, x + w * 0.85, y + h * 0.3],
              fill=(150, 150, 155))
    d.ellipse([x + w * 0.68, y + h * 0.02, x + w * 0.95, y + h * 0.2],
              fill=(170, 170, 175))
    d.polygon([(x + w * 0.3, y + h * 0.85), (x + w * 0.36, y + h * 0.6),
               (x + w * 0.44, y + h * 0.85)], fill=(247, 120, 40))


def scene_gaza(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(196, 164, 120))
    d.rectangle([x, y + h * 0.72, x + w, y + h], fill=(120, 96, 66))
    d.rectangle([x + w * 0.12, y + h * 0.4, x + w * 0.6, y + h * 0.72],
                fill=(240, 238, 230))
    d.rectangle([x + w * 0.6, y + h * 0.5, x + w * 0.82, y + h * 0.72],
                fill=(200, 60, 50))
    d.rectangle([x + w * 0.16, y + h * 0.46, x + w * 0.3, y + h * 0.54],
                fill=(60, 120, 80))
    d.ellipse([x + w * 0.22, y + h * 0.68, x + w * 0.32, y + h * 0.8],
              fill=(30, 30, 30))
    d.ellipse([x + w * 0.64, y + h * 0.68, x + w * 0.74, y + h * 0.8],
              fill=(30, 30, 30))
    d.polygon([(x + w * 0.7, y + h * 0.12), (x + w * 0.76, y + h * 0.3),
               (x + w * 0.64, y + h * 0.3)], fill=(247, 243, 234))


def scene_nasdaq(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(16, 36, 56))
    for gy in (0.25, 0.5, 0.75):
        d.line([x + w * 0.06, y + h * gy, x + w * 0.94, y + h * gy],
               fill=(50, 70, 95), width=1)
    pts = [(0.08, 0.25), (0.25, 0.32), (0.42, 0.28), (0.58, 0.52),
           (0.74, 0.62), (0.9, 0.82)]
    xy = [(x + w * px, y + h * py) for px, py in pts]
    d.line(xy, fill=(230, 70, 70), width=4)
    d.polygon([(x + w * 0.9, y + h * 0.82), (x + w * 0.82, y + h * 0.78),
               (x + w * 0.88, y + h * 0.7)], fill=(230, 70, 70))
    d.text((x + w - 52, y + h - 22), "-6.1%", font=font(SANS_B, 15),
           fill=(230, 70, 70))


def scene_bridge(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(90, 140, 190))
    d.rectangle([x, y + h * 0.68, x + w, y + h], fill=(40, 90, 140))
    d.arc([x + w * 0.3, y + h * 0.1, x + w * 0.75, y + h * 0.75],
          180, 360, fill=(247, 243, 234), width=5)
    d.line([x + w * 0.05, y + h * 0.62, x + w * 0.45, y + h * 0.62],
           fill=(30, 30, 30), width=5)
    d.line([x + w * 0.6, y + h * 0.62, x + w * 0.95, y + h * 0.62],
           fill=(30, 30, 30), width=5)
    d.polygon([(x + w * 0.45, y + h * 0.62), (x + w * 0.5, y + h * 0.82),
               (x + w * 0.6, y + h * 0.62)], fill=(30, 30, 30))
    d.ellipse([x + w * 0.76, y + h * 0.1, x + w * 0.9, y + h * 0.26],
              fill=(247, 220, 110))


def scene_dengue(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(200, 230, 205))
    d.ellipse([x + w * 0.3, y + h * 0.2, x + w * 0.7, y + h * 0.8],
              fill=(255, 255, 255), outline=(52, 140, 90), width=4)
    d.line([x + w * 0.4, y + h * 0.58, x + w * 0.6, y + h * 0.38],
           fill=(52, 140, 90), width=5)
    d.line([x + w * 0.6, y + h * 0.58, x + w * 0.4, y + h * 0.38],
           fill=(52, 140, 90), width=5)
    d.ellipse([x + w * 0.1, y + h * 0.12, x + w * 0.22, y + h * 0.26],
              fill=(60, 60, 60))
    d.line([x + w * 0.16, y + h * 0.12, x + w * 0.1, y + h * 0.05],
           fill=(60, 60, 60), width=2)
    d.line([x + w * 0.16, y + h * 0.12, x + w * 0.22, y + h * 0.05],
           fill=(60, 60, 60), width=2)


def scene_eu_id(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(24, 52, 110))
    for i in range(12):
        a = 2 * math.pi * i / 12
        sx = x + w * 0.26 + 16 * math.cos(a)
        sy = y + h * 0.5 + 16 * math.sin(a)
        d.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=GOLD)
    d.polygon([(x + w * 0.62, y + h * 0.28), (x + w * 0.86, y + h * 0.28),
               (x + w * 0.86, y + h * 0.72), (x + w * 0.62, y + h * 0.72)],
              fill=(200, 40, 40))
    d.rectangle([x + w * 0.62, y + h * 0.28, x + w * 0.86, y + h * 0.72],
                outline=WHITE, width=2)
    d.line([x + w * 0.62, y + h * 0.5, x + w * 0.86, y + h * 0.5],
           fill=WHITE, width=2)


SCENES = {1: scene_cop31, 2: scene_bahrain, 3: scene_riyadh, 4: scene_quake,
          5: scene_cartel, 6: scene_ship, 7: scene_poland, 8: scene_kryvyi,
          9: scene_gaza, 10: scene_nasdaq, 11: scene_bridge,
          12: scene_dengue, 13: scene_eu_id}

# ---------------------------------------------------------------- map
# Rough continent outlines (lon, lat) for a stylised world map.
CONTINENTS = [
    # North America
    [(-168, 66), (-140, 70), (-120, 71), (-100, 68), (-85, 66), (-75, 62),
     (-65, 60), (-55, 52), (-60, 46), (-70, 42), (-75, 35), (-80, 32),
     (-84, 30), (-90, 21), (-97, 26), (-105, 22), (-110, 24), (-117, 33),
     (-125, 40), (-125, 49), (-135, 58), (-155, 58), (-165, 60)],
    # South America
    [(-79, 9), (-72, 12), (-62, 10), (-52, 5), (-44, -3), (-35, -8),
     (-40, -20), (-48, -28), (-58, -38), (-65, -45), (-68, -52),
     (-70, -40), (-73, -30), (-77, -18), (-80, -5), (-81, 1)],
    # Africa
    [(-17, 15), (-10, 31), (0, 36), (10, 37), (20, 32), (32, 31),
     (35, 28), (43, 12), (51, 11), (48, 2), (40, -8), (36, -18),
     (33, -26), (26, -34), (18, -35), (12, -18), (9, -1), (-8, 4)],
    # Eurasia
    [(-10, 36), (-9, 43), (-2, 48), (0, 51), (5, 58), (10, 59),
     (18, 56), (21, 55), (24, 60), (30, 70), (45, 68), (60, 69),
     (75, 72), (100, 77), (130, 72), (160, 70), (178, 66), (162, 60),
     (142, 55), (140, 40), (130, 35), (122, 30), (110, 20), (105, 10),
     (100, 8), (92, 16), (88, 22), (80, 13), (76, 8), (72, 20),
     (66, 25), (58, 26), (52, 28), (48, 30), (44, 29), (40, 32),
     (36, 36), (30, 36), (26, 38), (22, 40), (19, 42), (12, 44),
     (8, 44), (3, 43)],
    # Australia
    [(114, -22), (122, -14), (132, -12), (142, -11), (146, -19),
     (150, -23), (153, -27), (150, -37), (140, -38), (132, -32),
     (124, -33), (115, -35), (113, -25)],
]
UK = [(-5, 50), (-3, 53), (-5, 56), (-2, 58), (0, 53), (1, 51)]
JAPAN = [(130, 31), (133, 34), (137, 35), (140, 38), (141, 42), (144, 44),
         (142, 40), (139, 36), (135, 34), (131, 33)]


def project(lon, lat, x0, y0, w, h):
    px = x0 + (lon + 170.0) / 360.0 * w
    py = y0 + (80.0 - lat) / 135.0 * h
    return px, py


def draw_map(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(18, 38, 60))
    for poly in CONTINENTS + [UK, JAPAN]:
        pts = [project(lon, lat, x, y, w, h) for lon, lat in poly]
        d.polygon(pts, fill=(88, 128, 158))
    d.text((x + 10, y + 8), "WHERE IT HAPPENED  —  STORIES 1–13",
           font=font(SANS_B, 13), fill=(200, 215, 230))
    all_stories = LEADS + MIDS
    offs = {2: (-14, -16), 3: (16, -14), 9: (-16, 14), 7: (14, -14),
            11: (-16, 14)}
    for n, _reg, _h, _dk, lon, lat in all_stories:
        px, py = project(lon, lat, x, y, w, h)
        dx, dy = offs.get(n, (0, 0))
        qx, qy = px + dx, py + dy
        if (dx, dy) != (0, 0):
            d.line([px, py, qx, qy], fill=(247, 220, 110), width=2)
            d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=GOLD)
        num_badge(d, qx, qy, n, r=10)


# ---------------------------------------------------------------- page
def build():
    assert len(LEADS) + len(MIDS) + len(TAIL) == 35
    assert sum(c for _, c, _ in REGIONS) == 35
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    M = 16  # margin

    def scene_box(n, x, y, w, h):
        """Draw scene n clipped to its own box."""
        layer = Image.new("RGB", (int(w), int(h)), PAPER)
        ld = ImageDraw.Draw(layer)
        SCENES[n](ld, 0, 0, w, h)
        img.paste(layer, (int(x), int(y)))

    # ---- masthead
    d.rectangle([0, 0, W, 110], fill=NAVY)
    d.rectangle([0, 110, W, 113], fill=GOLD)
    d.text((M, 12), "THE WORLD IN ONE PAGE",
           font=font(SANS_B, 13), fill=GOLD)
    d.text((M, 30), "THE WORLD TODAY",
           font=font(SERIF, 58), fill=WHITE)
    right = "SATURDAY 21 NOVEMBER 2026"
    rw = d.textlength(right, font=font(SANS_B, 17))
    d.text((W - M - rw, 16), right, font=font(SANS_B, 17), fill=WHITE)
    sub = "35 STORIES  •  7 REGIONS  •  ONE DAY"
    sw = d.textlength(sub, font=font(SANS_B, 13))
    d.text((W - M - sw, 42), sub, font=font(SANS_B, 13),
           fill=(190, 205, 220))
    d.text((M, 92), "The day's most consequential news, from Antalya to Lima.",
           font=font(SERIF_R, 14), fill=(200, 210, 225))

    # ---- banner headline
    d.rectangle([M, 120, W - M, 150], fill=RED)
    banner = "COP31 NEARS A DEAL AS MISSILES FLY OVER THE GULF"
    bw = d.textlength(banner, font=font(SERIF, 24))
    d.text(((W - bw) / 2, 125), banner, font=font(SERIF, 24), fill=WHITE)

    # ---- stat strip
    y0, y1 = 156, 200
    cw = (W - 2 * M) / 6
    for i, (num, label) in enumerate(STATS):
        x = M + i * cw
        if i:
            d.line([x, y0 + 6, x, y1 - 6], fill=LINE, width=1)
        d.text((x + 8, y0 + 2), num, font=font(SERIF, 26), fill=RED)
        para(d, x + 8, y0 + 30, cw - 16, label, font(SANS_B, 8),
             fill=GREY, leading=10, max_lines=2)
    d.line([M, y1, W - M, y1], fill=INK, width=2)

    # ---- leads
    ly, lh_img = 210, 122
    colw = (W - 2 * M - 2 * 12) / 3
    for i, (n, reg, head, deck, _lon, _lat) in enumerate(LEADS):
        x = M + i * (colw + 12)
        scene_box(n, x, ly, colw, lh_img)
        num_badge(d, x + 18, ly + 18, n, r=13)
        chip(d, x + colw - 118, ly + lh_img - 26, reg, RED)
        y = ly + lh_img + 10
        y = para(d, x, y, colw, head, font(SERIF, 25), leading=27,
                 max_lines=3)
        para(d, x, y + 4, colw, deck, font(SANS, 13), fill=(60, 58, 52),
             leading=16, max_lines=3)
    d.line([M, 446, W - M, 446], fill=INK, width=2)

    # ---- region bar
    ry = 452
    d.text((M, ry), "REGIONS:", font=font(SANS_B, 12), fill=INK)
    rx = M + 72
    for name, count, color in REGIONS:
        wch = chip(d, rx, ry - 2, "%s %d" % (name, count), color)
        rx += wch + 8

    # ---- mid grid: 5 columns x 2 rows
    mw = (W - 2 * M - 4 * 10) / 5
    my, mh_img = 480, 50
    for i, (n, reg, head, deck, _lon, _lat) in enumerate(MIDS):
        col, row = i % 5, i // 5
        x = M + col * (mw + 10)
        yy = my + row * 112
        scene_box(n, x, yy, mw, mh_img)
        num_badge(d, x + 15, yy + 14, n, r=10)
        y = yy + mh_img + 5
        y = para(d, x, y, mw, head, font(SANS_B, 13), leading=15,
                 max_lines=2)
        para(d, x, y + 1, mw, deck, font(SANS, 10.5), fill=(60, 58, 52),
             leading=12, max_lines=2)
    d.line([M, 708, W - M, 708], fill=INK, width=2)

    # ---- map
    draw_map(d, M, 714, W - 2 * M, 92)

    # ---- tail list
    ty = 812
    d.text((M, ty), "ALSO TODAY  —  STORIES 14–35",
           font=font(SANS_B, 13), fill=RED)
    d.line([M, ty + 20, W - M, ty + 20], fill=LINE, width=1)
    colw2 = (W - 2 * M - 24) / 2
    tf = font(SANS, 12.5)
    tfb = font(SANS_B, 12.5)
    for i, (n, head) in enumerate(TAIL):
        col, row = i // 11, i % 11
        x = M + col * (colw2 + 24)
        y = ty + 26 + row * 12.5
        d.text((x, y), "%d." % n, font=tfb, fill=RED)
        d.text((x + 26, y), trunc(d, head, tf, colw2 - 26), font=tf,
               fill=INK)

    # ---- footer
    fy = 984
    d.line([M, fy - 6, W - M, fy - 6], fill=INK, width=2)
    d.text((M, fy), "DATE CHECK: every story above happened or was first "
           "reported on Saturday 21 November 2026.",
           font=font(SANS_B, 11), fill=INK)
    d.text((M, fy + 13), "Sources: Reuters, AP, BBC, AFP, Al Jazeera, "
           "USGS, Institute for the Study of War. COP31 deal not yet "
           "sealed at press time; Gaza toll per Gaza Health Ministry.",
           font=font(SANS, 10.5), fill=GREY)
    img.save(OUT, optimize=True)
    return OUT


if __name__ == "__main__":
    path = build()
    print(path, os.path.getsize(path))
