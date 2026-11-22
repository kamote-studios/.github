"""Derive brand variants from the official Kamote Studios / OUTRUN source art.

Run from the repository root:  python design/build_brand.py
"""
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
BRAND = ROOT / "assets" / "brand"
WORK = ROOT / "design" / "_work"          # intermediate files used by the HTML templates
WORK.mkdir(parents=True, exist_ok=True)

NAVY = (17, 24, 51)        # #111833  ink colour for light backgrounds
NIGHT = (10, 15, 31)       # #0A0F1F  studio night background


def recolor(src: Image.Image, rgb) -> Image.Image:
    """Keep the alpha channel, replace the colour (source art is single-colour white)."""
    alpha = src.getchannel("A")
    out = Image.new("RGBA", src.size, rgb + (255,))
    out.putalpha(alpha)
    return out


def trim(img: Image.Image, pad: int = 0) -> Image.Image:
    l, t, r, b = img.getchannel("A").point(lambda a: 255 if a > 8 else 0).getbbox()
    return img.crop((max(l - pad, 0), max(t - pad, 0), min(r + pad, img.width), min(b + pad, img.height)))


logo = Image.open(BRAND / "kamote-studios-logo-white.png").convert("RGBA")
mascot = Image.open(BRAND / "kamote-studios-mascot-white.png").convert("RGBA")

# 1. Ink (navy) variants for light backgrounds — same canvas as the originals.
recolor(logo, NAVY).save(BRAND / "kamote-studios-logo-navy.png", optimize=True)
recolor(mascot, NAVY).save(BRAND / "kamote-studios-mascot-navy.png", optimize=True)

# 2. Tightly trimmed copies for layout work.
trim(logo).save(WORK / "logo-white-trim.png")
trim(recolor(logo, NAVY)).save(WORK / "logo-navy-trim.png")
trim(mascot).save(WORK / "mascot-white-trim.png")
trim(recolor(mascot, NAVY)).save(WORK / "mascot-navy-trim.png")

# 3. Organization avatar: white mascot on studio night (GitHub avatars need an opaque tile).
size = 1000
avatar = Image.new("RGBA", (size, size), NIGHT + (255,))
m = trim(mascot)
inner = int(size * 0.80)
m = m.resize((inner, int(inner * m.height / m.width)), Image.LANCZOS)
avatar.alpha_composite(m, ((size - m.width) // 2, (size - m.height) // 2))
avatar.convert("RGB").save(BRAND / "kamote-studios-avatar-1000.png", optimize=True)

print("brand variants written")

# 4. README-sized, trimmed marks ("-dark" = for GitHub dark theme, "-light" = for light theme).
README = ROOT / "assets" / "readme"
README.mkdir(parents=True, exist_ok=True)


def fit_width(img: Image.Image, width: int) -> Image.Image:
    return img.resize((width, round(img.height * width / img.width)), Image.LANCZOS)


fit_width(trim(logo), 600).save(README / "kamote-studios-logo-dark.png", optimize=True)
fit_width(trim(recolor(logo, NAVY)), 600).save(README / "kamote-studios-logo-light.png", optimize=True)
fit_width(trim(mascot), 264).save(README / "kamote-studios-mascot-dark.png", optimize=True)
fit_width(trim(recolor(mascot, NAVY)), 264).save(README / "kamote-studios-mascot-light.png", optimize=True)
print("readme marks written")
