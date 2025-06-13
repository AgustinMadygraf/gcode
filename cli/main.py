"""
Main CLI entry point for SVG to G-code conversion.
"""

from pathlib import Path
import sys

from src.config import (
    SVG_INPUT_DIR, GCODE_OUTPUT_DIR,
    FEED, CMD_DOWN, CMD_UP,
    STEP_MM, DWELL_MS, MAX_HEIGHT_MM
)
from src.svg_loader import SvgLoader
from domain.gcode_generator import GCodeGenerator
from domain.path_transform_strategy import MirrorVerticalStrategy
from infrastructure.logger import logger


def select_svg_file() -> Path:
    """Select an SVG file from the input directory."""
    svg_dir = SVG_INPUT_DIR
    svg_files = sorted(svg_dir.glob("*.svg"))
    if not svg_files:
        sys.exit("No SVG files found in svg_input.")
    logger.info("Available SVG files:")
    for idx, f in enumerate(svg_files, 1):
        logger.info("  %d. %s", idx, f.name)
    while True:
        try:
            sel = int(input(f"Select an SVG file (1-{len(svg_files)}): "))
            if 1 <= sel <= len(svg_files):
                return svg_files[sel-1]
        except (ValueError, TypeError):
            pass
        logger.warning("Invalid selection. Try again.")

def next_gcode_filename(svg_file: Path) -> Path:
    """Generate a new output filename with _vXX.gcode suffix."""
    out_dir = GCODE_OUTPUT_DIR
    stem = svg_file.stem
    for i in range(100):
        candidate = out_dir / f"{stem}_v{i:02d}.gcode"
        if not candidate.exists():
            return candidate
    sys.exit("Too many output files for this SVG.")

def main():
    "Main function to run the SVG to G-code conversion."
    svg_file = select_svg_file()
    logger.debug("Selected SVG file: %s", svg_file)

    gcode_file = next_gcode_filename(svg_file)
    logger.debug("Output G-code file: %s", gcode_file)

    svg = SvgLoader(svg_file)
    logger.debug('Created object "svg" from class "SvgLoader"')

    paths = svg.get_paths()
    logger.debug("Extracted %d paths from SVG.", len(paths))

    svg_attr = svg.get_attributes()
    logger.debug("SVG attributes: %s", svg_attr)

    # Calcular bbox y centro para las estrategias
    xmin, xmax, ymin, ymax = (
        svg.get_bbox() if hasattr(svg, 'get_bbox') else (None, None, None, None)
    )
    if xmin is None:
        # fallback: calcular bbox manualmente
        xs, ys = [], []
        for p in paths:
            for seg in p:
                for t in range(21):
                    z = seg.point(t/20)
                    xs.append(z.real)
                    ys.append(z.imag)
        xmin, xmax, ymin, ymax = min(xs), max(xs), min(ys), max(ys)
    _cx, cy = (xmin + xmax) / 2, (ymin + ymax) / 2
    # Definir estrategias de transformación (ejemplo: vertical mirror)
    transform_strategies = [MirrorVerticalStrategy(cy)]

    generator = GCodeGenerator(
        feed=FEED,
        cmd_down=CMD_DOWN,
        cmd_up=CMD_UP,
        step_mm=STEP_MM,
        dwell_ms=DWELL_MS,
        max_height_mm=MAX_HEIGHT_MM,
        logger=logger,
        transform_strategies=transform_strategies
    )
    logger.debug("Initialized GCodeGenerator with parameters: %s", generator)

    gcode_lines = generator.generate(paths, svg_attr)
    logger.debug("Generated G-code with %d lines.", len(gcode_lines))

    with gcode_file.open("w", encoding="utf-8") as f:
        f.write("\n".join(gcode_lines))
    logger.info("G-code file written to: %s", gcode_file)
