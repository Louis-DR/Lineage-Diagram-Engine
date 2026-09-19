import argparse
import html
import json
import shutil
import subprocess
from pathlib import Path

from tools.fixture_cases import build_all_fixtures
from tools.geometry_diagnostics import diagnose_fixture


def _find_browser() -> Path | None:
  for executable in ("msedge", "chromium", "google-chrome", "chrome"):
    found = shutil.which(executable)
    if found:
      return Path(found)

  candidates = (
    Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
  )
  return next((candidate for candidate in candidates if candidate.exists()), None)


def _segment_points(segment):
  upper = getattr(segment, "_upper_points", None)
  lower = getattr(segment, "_lower_points", None)
  if upper and lower:
    return list(upper), list(lower)
  return tuple(map(list, segment.compile()))


def _debug_overlay(fixture) -> str:
  parts = [
    '<g id="debug-overlay" pointer-events="none" font-family="monospace" font-size="8">'
  ]
  for event_x in fixture.event_xs:
    parts.append(
      f'<line x1="{event_x}" y1="0" x2="{event_x}" y2="{fixture.diagram.view_height}" '
      'stroke="#7c3aed" stroke-width="0.6" stroke-dasharray="3 2" opacity="0.7"/>'
    )
    parts.append(
      f'<text x="{event_x + 2}" y="10" fill="#5b21b6">{event_x:g}</text>'
    )

  colors = ("#111827", "#0369a1", "#9f1239", "#166534", "#92400e")
  for lineage_index, (name, lineage) in enumerate(fixture.lineages.items()):
    centers = []
    samples = []
    for segment in lineage._computed_segments:
      upper, lower = _segment_points(segment)
      segment_centers = [(top + bottom) / 2 for top, bottom in zip(upper, lower)]
      centers.extend(segment_centers)
      if segment_centers:
        step = max(1, len(segment_centers) // 12)
        samples.extend(segment_centers[::step])

    if not centers:
      continue
    color = colors[lineage_index % len(colors)]
    points = " ".join(f"{point.real:.3f},{point.imag:.3f}" for point in centers)
    parts.append(
      f'<polyline data-lineage="{html.escape(name)}" points="{points}" fill="none" '
      f'stroke="{color}" stroke-width="0.65" opacity="0.85"/>'
    )
    for point in samples:
      parts.append(
        f'<circle cx="{point.real:.3f}" cy="{point.imag:.3f}" r="1.1" fill="{color}"/>'
      )
    first = centers[0]
    parts.append(
      f'<text x="{first.real + 3:.3f}" y="{first.imag - 3:.3f}" fill="{color}">'
      f'{html.escape(name)}</text>'
    )

  parts.append("</g>")
  return "".join(parts)


def _rasterize(browser: Path, svg_path: Path, png_path: Path, width: int, height: int) -> dict:
  profile_path = png_path.parent / ".browser-profile"
  command = [
    str(browser),
    "--headless",
    "--disable-gpu",
    "--hide-scrollbars",
    "--no-first-run",
    f"--user-data-dir={profile_path.resolve()}",
    f"--window-size={width},{height}",
    f"--screenshot={png_path.resolve()}",
    svg_path.resolve().as_uri(),
  ]
  try:
    completed = subprocess.run(command, capture_output=True, text=True, timeout=30)
  except subprocess.TimeoutExpired as error:
    return {
      "ok": False,
      "returncode": None,
      "stderr": f"Browser screenshot timed out after {error.timeout} seconds.",
    }
  return {
    "ok": completed.returncode == 0 and png_path.exists(),
    "returncode": completed.returncode,
    "stderr": completed.stderr.strip(),
  }


def _write_gallery(output: Path, records: list[dict], browser: Path | None) -> None:
  cards = []
  for record in records:
    preview = record["png"] if record.get("png") else record["debug_svg"]
    counts = record["report"]["summary"]["by_kind"]
    count_text = ", ".join(f"{key}: {value}" for key, value in sorted(counts.items())) or "none"
    cards.append(f"""
      <article>
        <header>
          <h2>{html.escape(record['name'])}</h2>
          <p>{html.escape(record['description'])}</p>
        </header>
        <a href="{html.escape(record['debug_svg'])}"><img src="{html.escape(preview)}" alt="{html.escape(record['name'])}"></a>
        <p><strong>Violations:</strong> {html.escape(count_text)}</p>
        <p><a href="{html.escape(record['svg'])}">plain SVG</a> · <a href="{html.escape(record['report_json'])}">geometry JSON</a></p>
      </article>
    """)

  document = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Lineage engine fixture gallery</title>
  <style>
    :root {{ color-scheme: light; font-family: system-ui, sans-serif; background: #f4f1ea; color: #1f2937; }}
    body {{ margin: 0; padding: 2rem; }}
    h1 {{ margin-top: 0; }}
    .meta {{ color: #4b5563; }}
    main {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(360px, 1fr)); gap: 1.25rem; }}
    article {{ background: white; border: 1px solid #d6d3d1; border-radius: 8px; padding: 1rem; box-shadow: 0 8px 24px #29252412; }}
    h2 {{ margin: 0; font: 650 1.05rem ui-monospace, monospace; }}
    header p {{ min-height: 2.5em; }}
    img {{ display: block; width: 100%; background: white; border: 1px solid #e7e5e4; }}
    a {{ color: #075985; }}
  </style>
</head>
<body>
  <h1>Lineage engine fixture gallery</h1>
  <p class="meta">Browser rasterizer: {html.escape(str(browser) if browser else 'not found; SVG previews used')}</p>
  <main>{''.join(cards)}</main>
</body>
</html>
"""
  (output / "index.html").write_text(document, encoding="utf-8")


def main() -> int:
  parser = argparse.ArgumentParser(description="Render engine fixtures and a visual debug gallery.")
  parser.add_argument("--output", type=Path, default=Path("artifacts/fixtures"))
  parser.add_argument("--fail-on-violations", action="store_true")
  args = parser.parse_args()

  args.output.mkdir(parents=True, exist_ok=True)
  browser = _find_browser()
  records = []

  for fixture in build_all_fixtures():
    fixture_dir = args.output / fixture.name
    fixture_dir.mkdir(parents=True, exist_ok=True)

    report = diagnose_fixture(fixture)
    report_path = fixture_dir / "geometry.json"
    report_path.write_text(json.dumps(report, indent=2, allow_nan=False), encoding="utf-8")

    svg = fixture.diagram.to_svg()
    svg_path = fixture_dir / "fixture.svg"
    svg_path.write_text(svg, encoding="utf-8")

    debug_svg = svg.replace("</svg>", f"{_debug_overlay(fixture)}</svg>")
    debug_svg_path = fixture_dir / "debug.svg"
    debug_svg_path.write_text(debug_svg, encoding="utf-8")

    png_path = fixture_dir / "debug.png"
    raster = None
    if browser:
      raster = _rasterize(
        browser,
        debug_svg_path,
        png_path,
        int(fixture.diagram.view_width),
        int(fixture.diagram.view_height),
      )

    records.append({
      "name": fixture.name,
      "description": fixture.description,
      "svg": str(svg_path.relative_to(args.output)).replace("\\", "/"),
      "debug_svg": str(debug_svg_path.relative_to(args.output)).replace("\\", "/"),
      "png": str(png_path.relative_to(args.output)).replace("\\", "/") if raster and raster["ok"] else None,
      "report_json": str(report_path.relative_to(args.output)).replace("\\", "/"),
      "report": report,
      "raster": raster,
    })

  summary = {
    "fixture_count": len(records),
    "violation_count": sum(record["report"]["summary"]["violation_count"] for record in records),
    "browser": str(browser) if browser else None,
    "fixtures": records,
  }
  (args.output / "summary.json").write_text(json.dumps(summary, indent=2, allow_nan=False), encoding="utf-8")
  _write_gallery(args.output, records, browser)

  print(f"Fixture gallery written to {args.output / 'index.html'}")
  print(f"Detected {summary['violation_count']} violations across {len(records)} fixtures.")
  if args.fail_on_violations and summary["violation_count"]:
    return 1
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
