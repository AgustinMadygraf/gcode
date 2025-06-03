from HersheyFonts import HersheyFonts
from mecode       import G

TEXTO, ALTURA_MM = "HOLA AGUSTÍN", 10
FEED, SAFE_CMD, DRAW_CMD = 300, "M5", "M3"   # feed un poco más bajo
PEN_DELAY = 0.20        # segundos; ajustá 0.15-0.30 según tu servo
FUENTE = "futural"

hf = HersheyFonts()
hf.load_default_font(FUENTE)
hf.normalize_rendering(ALTURA_MM)

with G(outfile="hola_agustin.gcode", print_lines=False) as g:
    g.absolute()
    g.write("; === Header ===")
    g.write("G21")
    g.feed(FEED)
    g.write(SAFE_CMD)
    g.dwell(PEN_DELAY)           # espera a que suba del todo

    for stroke in hf.strokes_for_text(TEXTO):
        x0, y0 = stroke[0]
        g.move(x=x0, y=y0, rapid=True)   # salto rápido
        g.write(DRAW_CMD)                # pluma abajo
        g.dwell(PEN_DELAY)               # *** nuevo ***
        for x, y in stroke[1:]:
            g.move(x=x, y=y)             # trazo
        g.write(SAFE_CMD)                # pluma arriba
        g.dwell(PEN_DELAY)               # *** nuevo ***

    g.write("M2")
