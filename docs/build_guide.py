# /// script
# requires-python = ">=3.12"
# dependencies = ["markdown==3.8.2"]
# ///
"""Rebuild the offline guide: uv run docs/build_guide.py (no game setup needed)."""

from html import escape
from pathlib import Path
import re

import markdown

ROOT = Path(__file__).resolve().parents[1]
PAGES = [
    ("start", "Get started", "README.md"),
    ("tutorial", "Learn Typer", "docs/tutorial.md"),
    ("exercises", "Build your CLI", "docs/exercises.md"),
    ("rules", "Game rules", "docs/game-rules.md"),
    ("api", "API guide", "docs/api-guide.md"),
    ("usage", "Your usage guide", "USAGE.md"),
]
sections = []
for anchor, label, filename in PAGES:
    source = (ROOT / filename).read_text(encoding="utf-8")
    body = markdown.markdown(source, extensions=["fenced_code", "tables"])
    for target, _, other in PAGES:
        for link in (other, Path(other).name):
            body = body.replace(f'href="{link}"', f'href="#{target}"')
    body = body.replace('href="docs/index.html"', 'href="#start"')
    body = body.replace('href="BRANDING.md"', 'href="../BRANDING.md"')
    # Files that are intentionally edited as Markdown remain links to those sources.
    body = re.sub(r'href="(?!https?://|#|\.\./)([^"]+\.md)"', r'href="../\1"', body)
    sections.append(f'<section id="{anchor}" aria-label="{label}">{body}</section>')
nav = "".join(f'<a href="#{a}">{escape(label)}</a>' for a, label, _ in PAGES)
style = """
html{scroll-padding-top:24px}body{margin:0}header{padding:56px max(24px,calc((100vw - 1120px)/2));background:var(--ffe-color-surface-secondary-default)}header p{max-width:720px;font-size:1.25rem}header h1{font-size:clamp(2.5rem,5vw,4rem);margin:16px 0}header small{font-family:'SpareBank1 Medium',sans-serif}nav{display:flex;gap:16px 24px;flex-wrap:wrap;margin-top:32px}main{max-width:1120px;margin:auto;padding:32px 24px 64px}section{max-width:900px;margin:0 auto 48px;padding:32px;background:var(--ffe-color-background-default);border:1px solid var(--ffe-color-border-primary-subtle);border-radius:16px}section h1{font-size:2rem}h2{font-size:1.6rem;margin-top:40px}h3{font-size:1.2rem}p,li{font-size:1.1rem}li{margin:8px 0}pre{overflow-x:auto;white-space:pre;font-size:1rem}table{width:100%;border-collapse:collapse;display:block;overflow:auto}td,th{text-align:left;padding:12px;border-bottom:1px solid var(--ffe-color-border-primary-subtle)}footer{max-width:900px;margin:0 auto;padding:0 24px 40px}.skip{position:absolute;left:16px;top:-100px}.skip:focus{top:12px;background:white;padding:12px}@media(max-width:600px){section{padding:20px}main{padding:24px 12px}pre{padding:16px}}
"""
(ROOT / "docs/index.html").write_text(
    '<!doctype html><html lang="en"><meta charset="utf-8">'
    '<meta name="viewport" content="width=device-width,initial-scale=1">'
    '<title>Orbital Courier · Workshop guide</title>'
    f'<link rel="stylesheet" href="brand/theme.css"><style>{style}</style>'
    '<a class="skip" href="#start">Skip to the guide</a><header>'
    '<small>Python CLI workshop</small><h1>Build a CLI people can use.</h1>'
    '<p>Learn Typer, turn the supplied game functions into clear commands, '
    'and help a new user complete their first delivery.</p>'
    f'<nav aria-label="Workshop sections">{nav}</nav></header><main>'
    + "\n".join(sections)
    + '</main><footer>Visual foundations: <a href="../BRANDING.md">SpareBank 1 FFE</a>. '
    'Works offline. Edit the Markdown sources and run '
    '<code>uv run docs/build_guide.py</code> to refresh this guide.</footer></html>',
    encoding="utf-8",
)
print("Built docs/index.html")
