"""Driver for kg_rag_project: launch + drive the Streamlit app programmatically.

Usage (from project root, with venv activated):

    python .claude/skills/run-kg-rag-project/driver.py serve
        Launch streamlit on http://localhost:8501 in the foreground.

    python .claude/skills/run-kg-rag-project/driver.py health
        HTTP-probe localhost:8501/_stcore/health. Exits 0 if "ok", 1 otherwise.

    python .claude/skills/run-kg-rag-project/driver.py screenshot [URL] [OUT]
        Use Playwright Chromium to render the page (waiting for the WebSocket
        rerun to complete) and save a PNG. Defaults to
        http://localhost:8501 and <skill-dir>/screenshot.png.

    python .claude/skills/run-kg-rag-project/driver.py smoke
        Full sanity check: health + screenshot + assert non-trivial PNG size.

The driver does NOT start a background Streamlit for the screenshot/smoke
modes — bring it up yourself in another shell (`streamlit run app.py`)
or via the `serve` mode. This keeps process management explicit.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[3]  # project root
SKILL_DIR = Path(__file__).resolve().parent
DEFAULT_URL = "http://localhost:8501"
DEFAULT_OUT = SKILL_DIR / "screenshot.png"
HEALTH_URL = "http://localhost:8501/_stcore/health"


def cmd_serve(args: argparse.Namespace) -> int:
    """Foreground streamlit. Ctrl-C to stop."""
    venv_py = ROOT / "venv" / "Scripts" / "python.exe"
    if not venv_py.exists():
        print(f"venv python not found at {venv_py}", file=sys.stderr)
        return 2
    cmd = [
        str(venv_py),
        "-m", "streamlit", "run", str(ROOT / "app.py"),
        "--server.headless", "true",
        "--server.port", str(args.port),
        "--server.runOnSave", "true",
        "--browser.gatherUsageStats", "false",
    ]
    print(f"$ {' '.join(cmd)}")
    return subprocess.call(cmd, cwd=str(ROOT))


def cmd_health(args: argparse.Namespace) -> int:
    """Hit /_stcore/health. Exits 0 if 'ok', 1 if anything else."""
    deadline = time.time() + args.timeout
    last_err: Exception | None = None
    while time.time() < deadline:
        try:
            with urlopen(HEALTH_URL, timeout=3) as r:
                body = r.read().decode().strip()
                if body == "ok":
                    print(f"health: ok ({HEALTH_URL})")
                    return 0
                print(f"health: unexpected body {body!r}", file=sys.stderr)
                return 1
        except (URLError, ConnectionError, OSError) as e:
            last_err = e
            time.sleep(1)
    print(f"health: timeout after {args.timeout}s ({last_err})", file=sys.stderr)
    return 1


def cmd_screenshot(args: argparse.Namespace) -> int:
    """Render the Streamlit page with Playwright and save PNG."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print(
            "playwright not installed. Run:\n"
            "  venv\\Scripts\\python.exe -m pip install playwright\n"
            "  venv\\Scripts\\python.exe -m playwright install chromium",
            file=sys.stderr,
        )
        return 2

    url = args.url
    out = Path(args.out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport={"width": args.width, "height": args.height})
        page = ctx.new_page()
        print(f"-> {url}")
        page.goto(url, wait_until="domcontentloaded", timeout=30_000)
        # Streamlit hydrates via WebSocket; the hero title only appears after
        # the first rerun completes. Wait for our actual content, not just DOM.
        # Cold-start of the streamlit script imports langchain + grpc and
        # can take 30s+ before the first render reaches the browser, so
        # give the hero title up to 45s.
        try:
            page.wait_for_selector(".hero-title", timeout=45_000)
        except Exception as e:
            print(f"warn: hero title not visible ({e}); capturing anyway", file=sys.stderr)
        # Give animations a beat to settle.
        page.wait_for_timeout(800)
        page.screenshot(path=str(out), full_page=args.full_page)
        browser.close()

    size = out.stat().st_size
    print(f"saved {out} ({size} bytes)")
    return 0 if size > 10_000 else 1


def cmd_smoke(args: argparse.Namespace) -> int:
    """health → screenshot → asserts."""
    rc = cmd_health(argparse.Namespace(timeout=15))
    if rc != 0:
        return rc
    rc = cmd_screenshot(argparse.Namespace(
        url=DEFAULT_URL, out=str(DEFAULT_OUT),
        width=1440, height=900, full_page=False,
    ))
    if rc != 0:
        return rc
    print("smoke: ok")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="kg_rag_project driver")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_serve = sub.add_parser("serve", help="run streamlit in the foreground")
    p_serve.add_argument("--port", type=int, default=8501)
    p_serve.set_defaults(func=cmd_serve)

    p_health = sub.add_parser("health", help="probe /_stcore/health")
    p_health.add_argument("--timeout", type=int, default=10)
    p_health.set_defaults(func=cmd_health)

    p_shot = sub.add_parser("screenshot", help="render with Playwright + save PNG")
    p_shot.add_argument("url", nargs="?", default=DEFAULT_URL)
    p_shot.add_argument("out", nargs="?", default=str(DEFAULT_OUT))
    p_shot.add_argument("--width", type=int, default=1440)
    p_shot.add_argument("--height", type=int, default=900)
    p_shot.add_argument("--full-page", action="store_true")
    p_shot.set_defaults(func=cmd_screenshot)

    p_smoke = sub.add_parser("smoke", help="health + screenshot sanity check")
    p_smoke.set_defaults(func=cmd_smoke)

    args = p.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
