"""
run.py — Generador de G‑code basado en HersheyFonts.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from HersheyFonts import HersheyFonts
from mecode import G

DEFAULT_CONFIG_FILE = "config.json"


def load_config(path: str | os.PathLike) -> Dict[str, Any]:
    """Carga un archivo JSON y devuelve un diccionario.

    Lanza ``FileNotFoundError`` o ``json.JSONDecodeError`` si falla la
    apertura o el parseo.
    """
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"No se encontró el archivo de configuración: {path}")

    with path.open("r", encoding="utf-8") as fp:
        return json.load(fp)


def setup_logging(level_name: str = "INFO") -> None:
    """Configura el sistema de logging global."""
    level = getattr(logging, level_name.upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def generate_output_filename(font_name: str, outdir: Path) -> Path:
    """Genera un nombre de archivo único usando timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return outdir / f"{font_name}_{timestamp}.gcode"


def validate_font(hf: HersheyFonts, font_name: str) -> None:
    """Verifica que la fuente exista dentro de HersheyFonts."""
    try:
        hf.load_default_font(font_name)
    except (FileNotFoundError, ValueError) as exc:
        available = ", ".join(sorted(hf.fonts.keys()))  # type: ignore[attr-defined]
        logging.error("La fuente '%s' no existe. Fuentes disponibles: %s", font_name, available)
        raise SystemExit(1) from exc


def main() -> None:  # noqa: C901 ‑ ninguna función debe superar 50 líneas ➔ aquí es intencional
    parser = argparse.ArgumentParser(
        description="Genera G‑code a partir de texto usando HersheyFonts",
    )
    parser.add_argument("text", nargs="?", help="Texto a escribir (si falta, se solicitará por stdin)")
    parser.add_argument(
        "-c",
        "--config",
        default=DEFAULT_CONFIG_FILE,
        help="Ruta del archivo JSON de configuración (por defecto: %(default)s)",
    )

    args = parser.parse_args()

    # Cargar configuración
    try:
        cfg = load_config(args.config)
    except (FileNotFoundError, json.JSONDecodeError) as e:  # pragma: no cover
        logging.critical("Error al cargar la configuración: %s", e)
        sys.exit(1)

    setup_logging(cfg.get("log_level", "INFO"))

    texto = args.text or input("Texto a escribir: ").strip()
    if not texto:
        logging.error("No se ingresó texto. Abortando…")
        sys.exit(1)

    altura_mm: float = cfg.get("altura_mm", 10)
    feed: float = cfg.get("feed", 300)
    pen_delay: float = cfg.get("pen_delay", 0.2)
    fuente: str = cfg.get("fuente", "futural")
    outdir = Path(cfg.get("outdir", "gcode_output"))
    cmd_safe: str = cfg.get("cmd_safe", "M5")
    cmd_draw: str = cfg.get("cmd_draw", "M3")

    outdir.mkdir(parents=True, exist_ok=True)
    outfile = generate_output_filename(fuente, outdir)

    logging.info("Generando G‑code en '%s'…", outfile)

    hf = HersheyFonts()
    validate_font(hf, fuente)
    hf.normalize_rendering(altura_mm)

    with G(outfile=str(outfile), print_lines=False) as g:
        g.absolute()
        g.write("; === Header ===")
        g.write("G21")
        g.feed(feed)
        g.write(cmd_safe)
        g.dwell(pen_delay)

        for stroke in hf.strokes_for_text(texto):
            x0, y0 = stroke[0]
            g.move(x=x0, y=y0, rapid=True)
            g.write(cmd_draw)
            g.dwell(pen_delay)
            for x, y in stroke[1:]:
                g.move(x=x, y=y)
            g.write(cmd_safe)
            g.dwell(pen_delay)

        g.write("M2")

    logging.info("Proceso finalizado correctamente. Archivo creado: %s", outfile)


if __name__ == "__main__":
    main()
