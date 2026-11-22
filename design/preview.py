"""Preview profile/README.md locally in GitHub light and dark themes — before pushing.

The README uses absolute raw.githubusercontent.com URLs (required on the organization page),
so VS Code's preview cannot show images until they are pushed. This script swaps those URLs
for local files, resolves each <picture> for the chosen theme, and renders with GitHub-like CSS.

    pip install markdown-it-py
    python design/preview.py                 # writes design/_work/preview-{light,dark}.html
    python design/preview.py --png           # also screenshots them with headless Chrome
"""
import re, sys, subprocess, tempfile
from pathlib import Path
from markdown_it import MarkdownIt

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "profile" / "README.md"
WORK = ROOT / "design" / "_work"
RAW = "https://raw.githubusercontent.com/Kamote-Studios/.github/main/"

# Approximation of GitHub's markdown-body styles (Primer tokens, 2024+).
THEMES = {
    "light": dict(fg="#1f2328", muted="#59636e", bg="#ffffff", border="#d1d9e0", stripe="#f6f8fa",
                  link="#0969da", code="rgba(129,139,152,.12)", kbd="#f6f8fa"),
    "dark":  dict(fg="#f0f6fc", muted="#9198a1", bg="#0d1117", border="#3d444d", stripe="#151b23",
                  link="#4493f8", code="rgba(101,108,118,.2)", kbd="#151b23"),
}

CSS = """
body{{margin:0;background:{bg};color:{fg};font:16px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans",Helvetica,Arial,sans-serif}}
.page{{max-width:{width}px;margin:24px auto;border:1px solid {border};border-radius:6px;padding:24px}}
.page>:first-child{{margin-top:0}}
a{{color:{link};text-decoration:none}}
h2,h3{{margin:24px 0 16px;font-weight:600;line-height:1.25}}
h2{{font-size:1.5em;padding-bottom:.3em;border-bottom:1px solid {border}b3}}
h3{{font-size:1.25em}}
p,blockquote,table{{margin:0 0 16px}}
blockquote{{padding:0 1em;color:{muted};border-left:.25em solid {border}}}
img{{max-width:100%;box-sizing:content-box;border-style:none}}
table{{display:block;width:max-content;max-width:100%;overflow:auto;border-spacing:0;border-collapse:collapse}}
table th,table td{{padding:6px 13px;border:1px solid {border}}}
table th{{font-weight:600}}
table tr{{background:{bg};border-top:1px solid {border}b3}}
table tr:nth-child(2n){{background:{stripe}}}
table img{{background:transparent}}
td>:last-child{{margin-bottom:0}}
code{{padding:.2em .4em;font-size:85%;background:{code};border-radius:6px;font-family:ui-monospace,SFMono-Regular,Consolas,monospace}}
kbd{{display:inline-block;padding:4px;font:11px/10px ui-monospace,SFMono-Regular,Consolas,monospace;color:{fg};vertical-align:middle;background:{kbd};border:1px solid {border}b3;border-radius:6px;box-shadow:inset 0 -1px 0 {border}b3}}
sub{{font-size:75%}}
"""


def resolve_pictures(html: str, theme: str) -> str:
    def pick(m):
        block = m.group(0)
        src = re.search(rf'media="\(prefers-color-scheme: {theme}\)"\s+srcset="([^"]+)"', block)
        img = re.search(r"<img[^>]*>", block).group(0)
        return re.sub(r'src="[^"]+"', f'src="{src.group(1)}"', img) if src else img
    return re.sub(r"<picture>.*?</picture>", pick, html, flags=re.S)


def build(theme: str, width: int = 880) -> Path:
    md = MarkdownIt("commonmark", {"html": True}).enable("table")
    source = re.sub(r"<!--.*?-->", "", README.read_text(encoding="utf-8"), flags=re.S)
    body = md.render(source)
    body = resolve_pictures(body, theme).replace(RAW, (ROOT.as_uri() + "/"))
    WORK.mkdir(parents=True, exist_ok=True)
    out = WORK / f"preview-{theme}{'' if width == 880 else '-' + str(width)}.html"
    out.write_text(f"<!doctype html><meta charset=utf-8><title>README preview · {theme}</title>"
                   f"<style>{CSS.format(width=width, **THEMES[theme])}</style>"
                   f"<div class=page>{body}</div>", encoding="utf-8")
    return out


def screenshot(page: Path, width: int, height: int = 5200):
    sys.path.insert(0, str(Path(__file__).parent))
    from render import BROWSER
    from PIL import Image
    png = page.with_suffix(".png")
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run([BROWSER, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                        f"--user-data-dir={Path(tmp) / 'p'}", "--allow-file-access-from-files",
                        f"--window-size={width},{height}", "--virtual-time-budget=4000",
                        f"--screenshot={png}", page.as_uri()], check=True, capture_output=True, timeout=120)
    # trim the empty canvas below the page
    img = Image.open(png).convert("RGB")
    bg = img.getpixel((2, img.height - 2))
    rows = [y for y in range(img.height - 1, 0, -8) if any(img.getpixel((x, y)) != bg for x in range(0, img.width, 7))]
    img.crop((0, 0, img.width, min(img.height, rows[0] + 40))).save(png)
    print("screenshot:", png)


if __name__ == "__main__":
    for theme in THEMES:
        for width in (880, 360):
            page = build(theme, width)
            print("preview:", page)
            if "--png" in sys.argv:
                screenshot(page, width + 2 * 26 + 40)
