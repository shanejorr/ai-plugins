#!/usr/bin/env python3
"""
Convert a Markdown file to EPUB or KEPUB for e-readers.

Usage:
    python md_to_epub.py input.md output.epub
    python md_to_epub.py input.md output.kepub.epub
    python md_to_epub.py input.md output.epub --title "Title" --author "Author"

Format is determined by the output filename:
- *.kepub.epub -> KEPUB (Kobo-specific, enables reading stats and annotations)
- *.epub       -> standard EPUB (works on any e-reader)

If only a base name is given, defaults to .kepub.epub. Override with --format epub.

Diagrams (Mermaid, PlantUML, GraphViz, ...)
-------------------------------------------
Fenced code blocks tagged as a diagram language are rendered to an image and
embedded in the book, so the reader sees the picture instead of the diagram
source. ```mermaid``` is always eligible; the Kroki backend additionally handles
```plantuml```, ```graphviz```/```dot```, and others.

Backends (``--diagram-backend``):
- auto  (default): render Mermaid with the local Mermaid CLI (`mmdc`) if it is
        installed; otherwise leave the diagram source as a code block and warn.
- mmdc:  render Mermaid with the local Mermaid CLI. Install it with
         `npm install -g @mermaid-js/mermaid-cli`.
- kroki: POST diagram source to a Kroki server (default https://kroki.io) and
         embed the returned image. No local install, but the diagram source
         leaves your machine. Handles Mermaid, PlantUML, GraphViz, and more.
- none:  do not render diagrams; leave the fenced source as a code block.

A diagram that cannot be rendered is left untouched as its original fenced code
block, so nothing is ever lost.

Images
------
Every image the Markdown links to (``![alt](path)`` or raw ``<img>``) is copied
into the book. Local paths resolve relative to the Markdown file; ``data:`` URIs
are decoded; http(s) images are downloaded unless ``--no-remote-images`` is set.
Images are normalized so both Kobo and reMarkable display them: WebP, SVG, TIFF,
CMYK, and progressive-JPEG sources are re-encoded to PNG/JPEG, transparency is
flattened onto white, and anything larger than ``--max-image-size`` is scaled
down. An image that cannot be loaded becomes a short text placeholder.
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
import uuid

def _ensure_packages(required, marker):
    """Guarantee `required` is importable by THIS interpreter.

    `required` maps import name -> pip package name. The skill can be launched
    by whatever `python3` happens to be first on PATH (conda, Homebrew, the
    system Python, ...), and only some of those interpreters may have the
    dependencies installed. Rather than fail when the "wrong" interpreter runs
    us, install the missing packages into `sys.executable` -- the interpreter
    actually executing this script -- and re-exec. Because the install and the
    run always target the same interpreter, they can never diverge, which is
    exactly the failure mode this guards against.

    Set READING_PIPELINE_NO_AUTO_INSTALL=1 to disable auto-install and get a
    manual instruction instead. `marker` is an env var used to break a
    potential re-exec loop if an install "succeeds" but the import still fails.
    """
    import importlib.util

    def _missing(name):
        try:
            return importlib.util.find_spec(name) is None
        except (ImportError, ValueError):
            return True

    missing = [imp for imp in required if _missing(imp)]
    if not missing:
        return
    pkgs = sorted({required[imp] for imp in missing})
    manual = " ".join([sys.executable, "-m", "pip", "install", *pkgs])

    if os.environ.get("READING_PIPELINE_NO_AUTO_INSTALL") == "1":
        sys.stderr.write(
            "ERROR: missing packages: %s\n"
            "Auto-install is disabled (READING_PIPELINE_NO_AUTO_INSTALL=1). "
            "Install them manually:\n  %s\n" % (", ".join(pkgs), manual)
        )
        sys.exit(1)
    if os.environ.get(marker) == "1":
        sys.stderr.write(
            "ERROR: packages still missing after an install attempt: %s\n"
            "Install them manually with the interpreter running this script:\n"
            "  %s\n" % (", ".join(pkgs), manual)
        )
        sys.exit(1)

    sys.stderr.write(
        "[reading-pipeline] installing missing packages into %s: %s\n"
        % (sys.executable, ", ".join(pkgs))
    )
    for extra in ([], ["--break-system-packages"], ["--user"],
                  ["--user", "--break-system-packages"]):
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "-q", *extra, *pkgs]
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
        os.execve(
            sys.executable,
            [sys.executable, os.path.abspath(__file__), *sys.argv[1:]],
            dict(os.environ, **{marker: "1"}),
        )

    sys.stderr.write(
        "ERROR: could not auto-install required packages. Run manually:\n  %s\n"
        % manual
    )
    sys.exit(1)


_ensure_packages(
    {"ebooklib": "ebooklib", "markdown": "markdown", "PIL": "Pillow"},
    "_CONVERT_TO_EPUB_BOOTSTRAPPED",
)

from ebooklib import epub
import markdown
from PIL import Image


# Image formats every target reader displays reliably. Kobo's EPUB renderer
# (Adobe RMSDK) and reMarkable both handle baseline JPEG, PNG, and GIF; WebP,
# AVIF, TIFF, BMP, CMYK JPEGs, and progressive JPEGs are hit-or-miss, so those
# are re-encoded.
SAFE_IMAGE_FORMATS = {
    "JPEG": ("jpg", "image/jpeg"),
    "PNG": ("png", "image/png"),
    "GIF": ("gif", "image/gif"),
}

IMG_TAG_RE = re.compile(r"<img\b[^>]*>", re.IGNORECASE)
IMG_SRC_RE = re.compile(r"""\bsrc\s*=\s*(["'])(.*?)\1""", re.IGNORECASE | re.DOTALL)
IMG_ALT_RE = re.compile(r"""\balt\s*=\s*(["'])(.*?)\1""", re.IGNORECASE | re.DOTALL)


# Fence language tag -> Kroki diagram type. Used by the `kroki` backend to route
# each block to the right renderer. Mermaid is the only type the local `mmdc`
# backend handles.
KROKI_DIAGRAM_TYPES = {
    "mermaid": "mermaid",
    "plantuml": "plantuml",
    "puml": "plantuml",
    "c4plantuml": "c4plantuml",
    "graphviz": "graphviz",
    "dot": "graphviz",
    "ditaa": "ditaa",
    "blockdiag": "blockdiag",
    "seqdiag": "seqdiag",
    "actdiag": "actdiag",
    "nwdiag": "nwdiag",
    "erd": "erd",
    "nomnoml": "nomnoml",
    "svgbob": "svgbob",
    "d2": "d2",
    "wavedrom": "wavedrom",
}

# A fenced diagram block, e.g.
#   ```mermaid
#   graph TD; A --> B
#   ```
# Captures the language tag and the inner source. Only fences that start at the
# beginning of a line (optionally indented) are matched.
FENCED_DIAGRAM_RE = re.compile(
    r"^[ \t]*```[ \t]*(?P<lang>[A-Za-z0-9_+-]+)[ \t]*\r?\n"
    r"(?P<code>.*?)\r?\n"
    r"^[ \t]*```[ \t]*$",
    re.DOTALL | re.MULTILINE,
)

# Placeholder tokens use only capital letters + digits so python-markdown never
# treats them as emphasis, code, or anything else while converting the section.
_TOKEN_TMPL = "@@DIAGRAMPLACEHOLDER{idx}@@"


def md_to_html(md_text: str) -> str:
    """Convert markdown text to HTML with tables and fenced code support."""
    return markdown.markdown(
        md_text,
        extensions=["tables", "fenced_code", "toc", "md_in_html"],
    )


def _render_with_mmdc(
    code: str,
    tmpdir: str,
    idx: int,
    img_format: str,
    theme: str,
    background: str,
    scale: int,
) -> bytes | None:
    """Render one Mermaid block with the local Mermaid CLI. None on failure."""
    mmdc = shutil.which("mmdc")
    if not mmdc:
        return None

    in_path = os.path.join(tmpdir, f"diagram_{idx}.mmd")
    out_path = os.path.join(tmpdir, f"diagram_{idx}.{img_format}")
    with open(in_path, "w", encoding="utf-8") as f:
        f.write(code)

    # Headless / root Linux boxes need Chromium's --no-sandbox to launch.
    puppeteer_cfg = os.path.join(tmpdir, "puppeteer-config.json")
    if not os.path.exists(puppeteer_cfg):
        with open(puppeteer_cfg, "w", encoding="utf-8") as f:
            f.write('{"args": ["--no-sandbox"]}')

    cmd = [
        mmdc,
        "-i", in_path,
        "-o", out_path,
        "-b", background,
        "-t", theme,
        "-p", puppeteer_cfg,
    ]
    if img_format == "png":
        cmd += ["-s", str(scale)]  # scale factor only affects raster output

    try:
        subprocess.run(cmd, check=True, capture_output=True, timeout=180)
    except FileNotFoundError:
        return None
    except subprocess.CalledProcessError as e:
        detail = (e.stderr or b"").decode("utf-8", "replace").strip()
        sys.stderr.write(f"  ! mmdc failed on diagram {idx}: {detail[:400]}\n")
        return None
    except subprocess.TimeoutExpired:
        sys.stderr.write(f"  ! mmdc timed out on diagram {idx}\n")
        return None

    if not os.path.exists(out_path):
        return None
    with open(out_path, "rb") as f:
        return f.read()


def _render_with_kroki(
    code: str,
    diagram_type: str,
    img_format: str,
    server: str,
) -> bytes | None:
    """Render one block via a Kroki server. None on failure."""
    import urllib.error
    import urllib.request

    url = f"{server.rstrip('/')}/{diagram_type}/{img_format}"
    req = urllib.request.Request(
        url,
        data=code.encode("utf-8"),
        method="POST",
        headers={"Content-Type": "text/plain"},
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.read()
    except urllib.error.HTTPError as e:
        detail = (e.read() or b"").decode("utf-8", "replace").strip()
        sys.stderr.write(f"  ! Kroki rejected {diagram_type} diagram: {detail[:400]}\n")
        return None
    except urllib.error.URLError as e:
        sys.stderr.write(f"  ! Kroki request failed ({diagram_type}): {e}\n")
        return None


def embed_diagrams(
    md_text: str,
    book: "epub.EpubBook",
    backend: str,
    img_format: str,
    kroki_url: str,
    theme: str,
    background: str,
    scale: int,
) -> tuple[str, dict[str, str]]:
    """Render fenced diagram blocks to images embedded in ``book``.

    Returns ``(new_md_text, token_to_html)``: each rendered diagram block in the
    markdown is swapped for a unique placeholder token, and ``token_to_html``
    maps that token to the ``<figure>`` HTML that should replace it after the
    section is converted to HTML. Blocks that cannot be rendered are left as
    their original fenced code block.
    """
    if backend == "none":
        return md_text, {}

    supported = {"mermaid"} if backend in ("auto", "mmdc") else set(KROKI_DIAGRAM_TYPES)
    tmpdir = tempfile.mkdtemp(prefix="md_to_epub_diagrams_")
    token_to_html: dict[str, str] = {}
    stats = {"n": 0, "rendered": 0, "skipped": 0}

    def replace(match: "re.Match[str]") -> str:
        lang = match.group("lang").lower()
        if lang not in supported:
            return match.group(0)  # not a diagram we handle; leave untouched

        stats["n"] += 1
        idx = stats["n"]
        code = match.group("code")

        if backend in ("auto", "mmdc"):
            data = _render_with_mmdc(code, tmpdir, idx, img_format, theme, background, scale)
        else:  # kroki
            data = _render_with_kroki(code, KROKI_DIAGRAM_TYPES[lang], img_format, kroki_url)

        if data is None:
            stats["skipped"] += 1
            return match.group(0)  # keep the source so nothing is lost

        media_type = "image/svg+xml" if img_format == "svg" else "image/png"
        file_name = f"images/diagram_{idx}.{img_format}"
        book.add_item(
            epub.EpubImage(
                uid=f"diagram_{idx}",
                file_name=file_name,
                media_type=media_type,
                content=data,
            )
        )
        token = _TOKEN_TMPL.format(idx=idx)
        alt = f"{lang} diagram {idx}"
        token_to_html[token] = (
            f'<figure class="diagram"><img src="{file_name}" alt="{alt}"/></figure>'
        )
        stats["rendered"] += 1
        # Blank lines keep the token as its own paragraph after markdown parsing.
        return f"\n\n{token}\n\n"

    try:
        new_md = FENCED_DIAGRAM_RE.sub(replace, md_text)
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

    if stats["rendered"]:
        print(f"Rendered {stats['rendered']} diagram(s) to images.")
    if stats["skipped"]:
        print(
            f"WARNING: {stats['skipped']} diagram(s) could not be rendered and "
            f"were left as code blocks."
        )
        if backend in ("auto", "mmdc") and not shutil.which("mmdc"):
            print("  Install the Mermaid CLI: npm install -g @mermaid-js/mermaid-cli")
            print("  Or re-run with --diagram-backend kroki (sends diagram source to a Kroki server).")
    return new_md, token_to_html


class ImageEmbedder:
    """Copy every image an ``<img>`` tag references into the book.

    Sources can be local paths (resolved relative to the Markdown file),
    ``file://`` URLs, ``data:`` URIs, or ``http(s)`` URLs (downloaded unless
    remote fetching is disabled). Each image is normalized for e-ink and color
    e-readers: unsafe formats are re-encoded to PNG/JPEG, transparency is
    flattened onto white (transparent pixels vanish in dark mode and render
    unpredictably on reMarkable), and oversized images are scaled down.

    An image that cannot be loaded is replaced with a short text placeholder so
    the book stays valid and the reader knows something was there.
    """

    def __init__(self, book, base_dir: str, fetch_remote: bool, max_size: int):
        self.book = book
        self.base_dir = base_dir
        self.fetch_remote = fetch_remote
        self.max_size = max_size
        self.cache: dict[str, str | None] = {}
        self.embedded = 0
        self.converted = 0
        self.failed: list[str] = []

    def rewrite(self, html: str) -> str:
        return IMG_TAG_RE.sub(self._replace_tag, html)

    def _replace_tag(self, match: "re.Match[str]") -> str:
        tag = match.group(0)
        src_match = IMG_SRC_RE.search(tag)
        if not src_match or not src_match.group(2).strip():
            return tag
        src = src_match.group(2).strip()

        if src not in self.cache:
            self.cache[src] = self._embed(src)
        file_name = self.cache[src]

        if file_name is None:
            alt_match = IMG_ALT_RE.search(tag)
            label = (alt_match.group(2).strip() if alt_match else "") or src
            return f'<em class="missing-image">[Image unavailable: {label}]</em>'
        return tag[: src_match.start(2)] + file_name + tag[src_match.end(2):]

    def _embed(self, src: str) -> str | None:
        data = self._load(src)
        if data is None:
            self.failed.append(src)
            return None
        normalized = self._normalize(data, src)
        if normalized is None:
            self.failed.append(src)
            return None
        content, ext, media_type = normalized

        self.embedded += 1
        file_name = f"images/img_{self.embedded:03d}.{ext}"
        self.book.add_item(
            epub.EpubImage(
                uid=f"img_{self.embedded:03d}",
                file_name=file_name,
                media_type=media_type,
                content=content,
            )
        )
        return file_name

    def _load(self, src: str) -> bytes | None:
        import base64
        import html
        import urllib.parse
        import urllib.request

        src = html.unescape(src)
        if src.startswith("data:"):
            header, _, payload = src.partition(",")
            try:
                if header.endswith(";base64"):
                    return base64.b64decode(payload)
                return urllib.parse.unquote_to_bytes(payload)
            except ValueError:
                return None

        if re.match(r"https?://", src, re.IGNORECASE):
            if not self.fetch_remote:
                return None
            req = urllib.request.Request(src, headers={"User-Agent": "Mozilla/5.0"})
            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    return resp.read()
            except Exception as e:  # network errors, HTTP errors, bad URLs
                sys.stderr.write(f"  ! could not download image {src}: {e}\n")
                return None

        if src.lower().startswith("file://"):
            path = urllib.parse.unquote(urllib.parse.urlparse(src).path)
        else:
            path = urllib.parse.unquote(re.split(r"[?#]", src, maxsplit=1)[0])
        path = os.path.expanduser(path)
        if not os.path.isabs(path):
            path = os.path.join(self.base_dir, path)
        try:
            with open(path, "rb") as f:
                return f.read()
        except OSError:
            return None

    def _rasterize_svg(self, data: bytes) -> bytes | None:
        """Render SVG to PNG with rsvg-convert or ImageMagick, if installed."""
        tool = shutil.which("rsvg-convert")
        if tool:
            cmd = [tool, "-f", "png", "-b", "white", "-z", "2"]
        elif shutil.which("magick"):
            cmd = ["magick", "-background", "white", "-density", "192", "svg:-", "png:-"]
        else:
            return None
        try:
            result = subprocess.run(cmd, input=data, capture_output=True, check=True, timeout=60)
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError):
            return None
        return result.stdout or None

    def _normalize(self, data: bytes, src: str) -> tuple[bytes, str, str] | None:
        import io

        head = data[:512].lstrip().lower()
        if head.startswith(b"<svg") or (head.startswith(b"<?xml") and b"<svg" in data[:2048].lower()):
            png = self._rasterize_svg(data)
            if png is None:
                # Kobo shows SVG; reMarkable may not. Keep it rather than drop it.
                sys.stderr.write(
                    f"  ! no SVG rasterizer (rsvg-convert or magick) found; embedding {src} "
                    "as SVG, which some readers (e.g. reMarkable) may not display\n"
                )
                return data, "svg", "image/svg+xml"
            data = png

        try:
            img = Image.open(io.BytesIO(data))
            img.load()
        except Exception:
            sys.stderr.write(f"  ! not a readable image: {src}\n")
            return None

        fmt = img.format
        has_alpha = img.mode in ("RGBA", "LA", "PA") or (
            img.mode == "P" and "transparency" in img.info
        )
        oversized = max(img.size) > self.max_size
        animated = getattr(img, "n_frames", 1) > 1
        progressive = fmt == "JPEG" and (
            img.info.get("progressive") or img.info.get("progression")
        )
        odd_mode = img.mode not in ("RGB", "L", "P", "RGBA", "LA", "PA", "1")

        if fmt in SAFE_IMAGE_FORMATS and not (
            has_alpha or oversized or animated or progressive or odd_mode
        ):
            ext, media_type = SAFE_IMAGE_FORMATS[fmt]
            return data, ext, media_type

        # Re-encode. E-readers do not animate, so keep the first frame only.
        self.converted += 1
        img.seek(0)
        if has_alpha:
            rgba = img.convert("RGBA")
            flat = Image.new("RGB", rgba.size, "white")
            flat.paste(rgba, mask=rgba.getchannel("A"))
            img = flat
        elif img.mode not in ("RGB", "L"):
            img = img.convert("RGB")
        if oversized:
            img.thumbnail((self.max_size, self.max_size), Image.LANCZOS)

        out = io.BytesIO()
        if fmt == "JPEG":
            # Photos stay JPEG (baseline, so older Kobo firmware shows them).
            img.save(out, format="JPEG", quality=90, optimize=True, progressive=False)
            return out.getvalue(), "jpg", "image/jpeg"
        img.save(out, format="PNG", optimize=True)
        return out.getvalue(), "png", "image/png"


def resolve_output_path(output_path: str, fmt: str | None) -> str:
    """Decide on the final output path based on extension and --format flag."""
    if fmt == "kepub":
        if not output_path.endswith(".kepub.epub"):
            base = output_path[:-5] if output_path.endswith(".epub") else output_path
            output_path = base + ".kepub.epub"
    elif fmt == "epub":
        if output_path.endswith(".kepub.epub"):
            output_path = output_path[: -len(".kepub.epub")] + ".epub"
        elif not output_path.endswith(".epub"):
            output_path = output_path + ".epub"
    else:
        # No --format flag; infer from extension. Default to .kepub.epub if neither.
        if not (output_path.endswith(".epub") or output_path.endswith(".kepub.epub")):
            output_path = output_path + ".kepub.epub"
    return output_path


def create_epub(
    md_path: str,
    output_path: str,
    title: str | None = None,
    author: str | None = None,
    fmt: str | None = None,
    diagram_backend: str = "auto",
    diagram_format: str = "png",
    kroki_url: str = "https://kroki.io",
    mermaid_theme: str = "default",
    diagram_background: str = "white",
    diagram_scale: int = 2,
    fetch_remote_images: bool = True,
    max_image_size: int = 1600,
):
    """Create an EPUB or KEPUB from a markdown file."""
    with open(md_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    # Auto-detect title from first H1 if not provided
    if not title:
        m = re.search(r"^#\s+(.+)$", md_text, re.MULTILINE)
        if m:
            title = m.group(1).strip()
        else:
            title = os.path.splitext(os.path.basename(md_path))[0].replace("_", " ").title()

    if not author:
        # Try the explicit "**Authors:**" or "**Author:**" pattern
        m = re.search(r"\*\*Authors?:\*\*\s*(.+)", md_text)
        author = m.group(1).strip() if m else "Unknown"

    # Build the epub
    book = epub.EpubBook()
    book.set_identifier(str(uuid.uuid4()))
    book.set_title(title)
    book.set_language("en")
    book.add_author(author)
    book.add_metadata("DC", "publisher", "Claude")

    # Render any Mermaid/diagram fences to embedded images before splitting, so
    # the reader gets pictures instead of raw diagram source. Must run after the
    # book exists (images are added to it) and before sectioning/HTML.
    md_text, diagram_tokens = embed_diagrams(
        md_text,
        book,
        backend=diagram_backend,
        img_format=diagram_format,
        kroki_url=kroki_url,
        theme=mermaid_theme,
        background=diagram_background,
        scale=diagram_scale,
    )

    # Linked images are resolved relative to the Markdown file and copied into
    # the book; without this the EPUB would hold dangling <img> references.
    images = ImageEmbedder(
        book,
        base_dir=os.path.dirname(os.path.abspath(md_path)),
        fetch_remote=fetch_remote_images,
        max_size=max_image_size,
    )

    # CSS for clean e-reader formatting
    css = epub.EpubItem(
        uid="style",
        file_name="style/default.css",
        media_type="text/css",
        content="""
body {
    font-family: serif;
    line-height: 1.6;
    margin: 1em;
}
h1 { font-size: 1.5em; margin-top: 1em; margin-bottom: 0.5em; }
h2 { font-size: 1.3em; margin-top: 1em; margin-bottom: 0.4em; }
h3 { font-size: 1.1em; margin-top: 0.8em; margin-bottom: 0.3em; }
table { border-collapse: collapse; width: 100%; margin: 1em 0; font-size: 0.9em; }
th, td { border: 1px solid #999; padding: 0.4em 0.6em; text-align: left; }
th { background-color: #f0f0f0; font-weight: bold; }
blockquote { margin: 1em 0; padding-left: 1em; border-left: 3px solid #ccc; color: #555; }
code { font-family: monospace; font-size: 0.9em; background: #f5f5f5; padding: 0.1em 0.3em; }
pre { background: #f5f5f5; padding: 1em; overflow-x: auto; }
hr { border: none; border-top: 1px solid #ccc; margin: 1.5em 0; }
p { margin: 0.5em 0; }
dl dt { font-weight: bold; margin-top: 0.5em; }
dl dd { margin-left: 1.5em; margin-bottom: 0.5em; }
img { max-width: 100%; height: auto; page-break-inside: avoid; }
.missing-image { color: #777; font-size: 0.9em; }
figure { margin: 1em 0; text-align: center; }
figure.diagram { page-break-inside: avoid; }
figure.diagram img { max-width: 100%; }
figcaption { font-size: 0.85em; color: #555; margin-top: 0.3em; }
""".encode("utf-8"),
    )
    book.add_item(css)

    # Split markdown into chapters by H2 headings.
    sections = re.split(r"(?=^## )", md_text, flags=re.MULTILINE)

    chapters = []
    toc = []

    for i, section in enumerate(sections):
        if not section.strip():
            continue

        heading_match = re.match(r"^##\s+(.+)$", section, re.MULTILINE)
        if heading_match:
            section_title = heading_match.group(1).strip()
        elif i == 0:
            # Pre-H2 content (title, metadata, anything above the first H2)
            section_title = title
        else:
            section_title = f"Section {i}"

        html_content = images.rewrite(md_to_html(section))

        # Swap diagram placeholders back in for the rendered <figure> images.
        for token, figure_html in diagram_tokens.items():
            if token in html_content:
                html_content = html_content.replace(f"<p>{token}</p>", figure_html)
                html_content = html_content.replace(token, figure_html)

        chapter_html = f"""<?xml version='1.0' encoding='utf-8'?>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>{section_title}</title>
    <link rel="stylesheet" type="text/css" href="style/default.css"/>
</head>
<body>
{html_content}
</body>
</html>"""

        safe_name = re.sub(r"[^a-zA-Z0-9]", "_", section_title.lower())[:40]
        chapter = epub.EpubHtml(
            title=section_title,
            file_name=f"ch_{i:02d}_{safe_name}.xhtml",
            lang="en",
        )
        chapter.content = chapter_html.encode("utf-8")
        chapter.add_item(css)

        book.add_item(chapter)
        chapters.append(chapter)
        toc.append(chapter)

    book.toc = toc
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    book.spine = ["nav"] + chapters

    if images.embedded:
        print(
            f"Embedded {images.embedded} image(s)"
            + (f" ({images.converted} converted for e-reader compatibility)." if images.converted else ".")
        )
    if images.failed:
        print(f"WARNING: {len(images.failed)} image(s) could not be embedded and were replaced with a placeholder:")
        for src in images.failed[:10]:
            print(f"  - {src}")
        if len(images.failed) > 10:
            print(f"  ... and {len(images.failed) - 10} more")

    output_path = resolve_output_path(output_path, fmt)
    epub.write_epub(output_path, book, {})
    print(f"Created: {output_path}")
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Convert Markdown to EPUB or KEPUB")
    parser.add_argument("input", help="Input markdown file")
    parser.add_argument("output", help="Output file path (.epub or .kepub.epub)")
    parser.add_argument("--title", help="Book title (auto-detected from H1 if omitted)")
    parser.add_argument("--author", help="Author name (auto-detected from **Authors:** line if omitted)")
    parser.add_argument(
        "--format",
        choices=["epub", "kepub"],
        help="Force output format. If omitted, inferred from output filename; defaults to kepub.",
    )
    parser.add_argument(
        "--diagram-backend",
        choices=["auto", "mmdc", "kroki", "none"],
        default="auto",
        help="How to render Mermaid/diagram fences. auto: local mmdc if installed, "
        "else leave as code. mmdc: require local Mermaid CLI. kroki: POST to a "
        "Kroki server (also handles PlantUML, GraphViz, etc.). none: leave as code. "
        "Default: auto.",
    )
    parser.add_argument(
        "--diagram-format",
        choices=["png", "svg"],
        default="png",
        help="Rendered diagram image format. PNG is the most e-reader-compatible "
        "(default); SVG is sharper but not supported everywhere.",
    )
    parser.add_argument(
        "--kroki-url",
        default="https://kroki.io",
        help="Kroki server base URL for --diagram-backend kroki (default https://kroki.io). "
        "Point at a self-hosted instance to keep diagram source private.",
    )
    parser.add_argument(
        "--mermaid-theme",
        choices=["default", "neutral", "dark", "forest"],
        default="default",
        help="Mermaid theme for local mmdc rendering (default: default).",
    )
    parser.add_argument(
        "--diagram-background",
        default="white",
        help="Background for locally rendered diagrams: a color or 'transparent' "
        "(default: white, so labels stay legible in dark-mode readers).",
    )
    parser.add_argument(
        "--diagram-scale",
        type=int,
        default=2,
        help="PNG scale factor for local mmdc rendering; higher is crisper "
        "(default: 2).",
    )
    parser.add_argument(
        "--no-remote-images",
        action="store_true",
        help="Do not download http(s) images; replace them with a text placeholder. "
        "Local and data: URI images are always embedded.",
    )
    parser.add_argument(
        "--max-image-size",
        type=int,
        default=1600,
        help="Scale images so their longest side is at most this many pixels "
        "(default: 1600, close to Kobo Color and reMarkable Paper Pro screens).",
    )
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: Input file not found: {args.input}")
        sys.exit(1)

    create_epub(
        args.input,
        args.output,
        title=args.title,
        author=args.author,
        fmt=args.format,
        diagram_backend=args.diagram_backend,
        diagram_format=args.diagram_format,
        kroki_url=args.kroki_url,
        mermaid_theme=args.mermaid_theme,
        diagram_background=args.diagram_background,
        diagram_scale=args.diagram_scale,
        fetch_remote_images=not args.no_remote_images,
        max_image_size=args.max_image_size,
    )


if __name__ == "__main__":
    main()
