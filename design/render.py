"""Render the HTML templates in design/templates/ to PNG with headless Chrome (2x, transparent).

Run from the repository root:  python design/render.py [name ...]
Requires Google Chrome or Microsoft Edge, and the Windows "Bahnschrift" / "Segoe UI" fonts.
"""
import subprocess, sys, shutil, tempfile
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
TPL = ROOT / "design" / "templates"
OUT = ROOT / "assets" / "readme"

BROWSERS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    shutil.which("chrome") or "", shutil.which("msedge") or "", shutil.which("google-chrome") or "",
]
BROWSER = next(b for b in BROWSERS if b and Path(b).exists())

# name: (template file, css width, css height, output file)
JOBS = {}


def job(name, tpl, w, h, out, query=""):
    JOBS[name] = (tpl, w, h, out, query)


# ---- job table ---------------------------------------------------------------
job("hero-dark", "hero.html", 1000, 340, "kamote-studios-hero-dark.png", "?theme=dark")
job("hero-light", "hero.html", 1000, 340, "kamote-studios-hero-light.png", "?theme=light")
job("outrun-card", "outrun-card.html", 1000, 520, "outrun-feature-card.png")
for theme in ("dark", "light"):
    for plat in ("windows", "android"):
        job(f"badge-{plat}-{theme}", "badge.html", 230, 68,
            f"badge-{plat}-{theme}.png", f"?platform={plat}&theme={theme}")
    job(f"divider-{theme}", "divider.html", 1000, 40, f"divider-road-{theme}.png", f"?theme={theme}")
for icon in ("pursuit", "battery", "city", "garage", "scoreboard", "controls", "specs", "windows", "android"):
    job(f"icon-{icon}", "icon.html", 64, 64, f"icon-{icon}.png", f"?icon={icon}")
# -----------------------------------------------------------------------------


def render(name, scale=2):
    tpl, w, h, out, query = JOBS[name]
    OUT.mkdir(parents=True, exist_ok=True)
    url = (TPL / tpl).as_uri() + query
    with tempfile.TemporaryDirectory() as tmp:
        shot = Path(tmp) / "shot.png"
        subprocess.run([
            BROWSER, "--headless=new", "--disable-gpu", "--hide-scrollbars",
            "--no-first-run", "--no-default-browser-check", "--allow-file-access-from-files",
            f"--user-data-dir={Path(tmp) / 'profile'}", f"--force-device-scale-factor={scale}",
            "--default-background-color=00000000", f"--window-size={w},{h}",
            "--virtual-time-budget=3000", f"--screenshot={shot}", url,
        ], check=True, capture_output=True, timeout=90)
        img = Image.open(shot).convert("RGBA").crop((0, 0, w * scale, h * scale))
        dest = OUT / out
        img.save(dest, optimize=True)
    print(f"{name:22s} -> assets/readme/{out}  {img.size}  {dest.stat().st_size//1024} KB")


if __name__ == "__main__":
    for n in (sys.argv[1:] or JOBS):
        for key in [k for k in JOBS if k == n or k.startswith(n + "-")] or [n]:
            render(key)
