# Kamote Studios · `.github`

Organization-wide files for **Kamote Studios**. The public profile shown on
[github.com/Kamote-Studios](https://github.com/Kamote-Studios) is [`profile/README.md`](profile/README.md).

## Repository layout

```
.github/
├── profile/
│   └── README.md                  Organization profile (rendered on the org page)
├── assets/
│   ├── brand/                     Studio identity: master files
│   ├── outrun/                    OUTRUN game art: master files
│   └── readme/                    Graphics generated for the profile README
└── design/
    ├── build_brand.py             Derives colour variants and trimmed marks from the masters
    ├── render.py                  Renders design/templates/*.html to PNG with headless Chrome
    ├── preview.py                 Previews the profile README in GitHub light and dark themes
    └── templates/                 HTML/CSS sources for every generated graphic
```

## Brand assets

| File | Use |
| --- | --- |
| `assets/brand/kamote-studios-logo-white.png` | Full logo for dark backgrounds (master) |
| `assets/brand/kamote-studios-logo-navy.png` | Full logo for light backgrounds |
| `assets/brand/kamote-studios-mascot-white.png` | Mascot mark for dark backgrounds (master) |
| `assets/brand/kamote-studios-mascot-navy.png` | Mascot mark for light backgrounds |
| `assets/brand/kamote-studios-avatar-1000.png` | GitHub organization avatar (*Settings → Profile*) |
| `assets/outrun/outrun-icon-1024.png` | OUTRUN app icon (master) |
| `assets/outrun/outrun-key-art-3840x2160.png` | OUTRUN official key art, 4K (master) |

**Naming:** files in `assets/brand` and `assets/outrun` are named by colour or size. Files in
`assets/readme` that end in `-dark` / `-light` are the versions shown in GitHub's dark / light theme.

### Palette

Sampled from the OUTRUN icon and used across all README graphics.

| Token | Hex | Role |
| --- | --- | --- |
| Night | `#0A0F1F` | Primary dark surface |
| Ink | `#111833` | Logo and text on light surfaces |
| Siren Red | `#E5394F` | Accent (left light) |
| Siren Blue | `#2E6BF0` | Accent (right light) |
| Tape Yellow | `#FFCC4F` | Highlights on dark; use `#D99A12` on light |
| Mist | `#A3AECD` | Secondary text on dark |

## Editing the profile

- Images are linked by absolute `raw.githubusercontent.com/.../main/...` URLs, which display reliably on the
  organization page. New or changed images appear only after they are pushed to `main`, so use
  `design/preview.py` to check your changes locally first.
- Every image that sits directly on the page has a light and a dark version, switched with
  `<picture>` + `prefers-color-scheme`. Keep that pattern for new graphics.
- The *Available on Windows / Android* buttons have no links yet. When download pages exist, wrap each
  `<picture>` in `<a href="…">…</a>`.

## Regenerating graphics

Requires Windows (for the *Bahnschrift* and *Segoe UI* fonts), Google Chrome or Microsoft Edge, and
Python 3 with Pillow. The preview also needs `markdown-it-py`.

```sh
python design/build_brand.py      # colour variants, trimmed marks, avatar
python design/render.py           # every README graphic
python design/render.py hero      # one group: hero, outrun-card, badge, divider, icon
python design/preview.py --png    # design/_work/preview-{light,dark}.html and .png
```
