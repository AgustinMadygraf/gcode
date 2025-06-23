
; -----------------------------------------------------------
; sample_compacted.gcode
; Propósito: tests de compatibilidad para compresor de trayectorias
; -----------------------------------------------------------

; --- 1. Inicialización en coordenadas absolutas -----------------
G90          ; Modo absoluto
G21          ; Unidades en milímetros
G0   X10  Y10        ; Posicionamiento rápido
M3   S255            ; Baja lapicera / Activa herramienta
G4   P0.300          ; Pausa breve (previene manchas)

; --- 2. Declaramos feedrate una sola vez -------------------------
F4000        ; Velocidad para todos los movimientos lineales

; --- 3. Trazado en modo relativo (compacta varias líneas) --------
G91              ; Cambia a modo relativo
G1 X20  Y0       ; Lado 1
G1 X0   Y20      ; Lado 2
G1 X-20 Y0       ; Lado 3
G1 X0   Y-20     ; Lado 4


; --- 4. Vuelta a modo absoluto y prueba de arco -----------------
G90                 ; Regresa a modo absoluto
; ½ círculo horario de radio 10 mm: de (10,10) a (30,10)
G2 X30 Y10 I10 J0   ; Centro en (20,10), radio 10


; --- 5. Limpieza -------------------------------------------------
M5               ; Sube lapicera / Desactiva herramienta
G4 P0.200        ; Pausa corta tras apagar
G0 X0 Y0         ; Regreso a origen
M30              ; Fin de programa
