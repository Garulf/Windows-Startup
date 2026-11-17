"""Render the README screenshots and hero image with flow-render.

Usage (from the repo root):

    uvx --from flow-render==0.15.0 --with pip python docs/screenshots/render.py

Each ``<shot>.json`` is a flow-render config whose results name one of the
plugin's icons in ``image``. Those icons are white, so they are tinted with the
theme's text colour to stay visible on the light theme.
"""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SHOTS_DIR = ROOT / "docs" / "screenshots"
ASSETS_DIR = ROOT / ".github" / "assets"
IMAGES = {
    "application": ROOT / "data" / "icon.png",
    "check-circle": ROOT / "src" / "plugin" / "icons" / "check-circle.png",
    "checkbox-blank-circle": ROOT / "src" / "plugin" / "icons" / "checkbox-blank-circle.png",
}
THEMES = {"dark": "#FFFFFF", "light": "#1B1B1B"}
HERO = {"shot": "hero", "theme": "dark", "css": ["win11-dark.css", "docs/screenshots/hero.css"]}


def tinted_png(name: str, color: str, out_dir: Path) -> Path:
    path = out_dir / f"{name}-{color.lstrip('#')}.png"
    if not path.exists():
        alpha = Image.open(IMAGES[name]).convert("RGBA").getchannel("A")
        image = Image.new("RGBA", alpha.size, color)
        image.putalpha(alpha)
        image.save(path)
    return path


def flow_render(args, out_path: Path) -> None:
    with tempfile.TemporaryDirectory() as out_dir:
        subprocess.run(["flow-render", *args, "-o", out_dir], check=True, cwd=ROOT)
        (rendered,) = Path(out_dir).glob("*.png")
        shutil.move(str(rendered), out_path)
    print(f"Wrote {out_path}")


def render_config(shot: str, theme: str, css, out_path: Path, work: Path) -> None:
    config = json.loads((SHOTS_DIR / f"{shot}.json").read_text(encoding="utf-8"))
    config["icon"] = str((SHOTS_DIR / config["icon"]).resolve())
    for result in config["results"]:
        result["icon"] = str(tinted_png(result.pop("image"), THEMES[theme], work))
    config["css"] = css
    config_path = work / f"{shot}-{theme}.json"
    config_path.write_text(json.dumps(config), encoding="utf-8")
    flow_render(["-c", str(config_path)], out_path)


def main() -> None:
    shots = sorted(path.stem for path in SHOTS_DIR.glob("*.json") if path.stem != HERO["shot"])
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        for shot in shots:
            for theme in THEMES:
                render_config(shot, theme, f"win11-{theme}.css", ASSETS_DIR / f"{shot}-{theme}.png", work)
        render_config(HERO["shot"], HERO["theme"], HERO["css"], ASSETS_DIR / "hero.png", work)

        package = subprocess.run([str(ROOT / "scripts" / "package.sh"), str(work / "dist")], check=True, capture_output=True, text=True)
        plugin_zip = package.stdout.strip().splitlines()[-1]
        for theme in THEMES:
            flow_render(["-u", plugin_zip, "-i", "-s", f"win11-{theme}", "--hide-caret"], ASSETS_DIR / f"install-{theme}.png")


if __name__ == "__main__":
    sys.exit(main())
