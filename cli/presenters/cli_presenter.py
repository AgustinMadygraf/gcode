"""
CliPresenter: Maneja toda la interacción de entrada/salida con el usuario en la CLI.
Permite inyectar dependencias como i18n y manejo de colores.
"""

class CliPresenter:
    def __init__(self, i18n=None, color_service=None):
        self.i18n = i18n
        self.color_service = color_service

    def print(self, message, color=None):
        # Si es clave i18n, traducir
        if message in self.i18n._messages.get(self.i18n._default_lang, {}):
            message = self.i18n.get(message)
        if self.color_service and color:
            message = self.color_service.colorize(message, color)
        print(message)

    def input(self, prompt, color=None):
        if self.color_service and color:
            prompt = self.color_service.colorize(prompt, color)
        return input(prompt)

    def print_error(self, message, file=None, line=None, dev_mode=False, use_color=True):
        self.print_colored(message, level="error", file=file, line=line, dev_mode=dev_mode, use_color=use_color)

    def print_success(self, message, file=None, line=None, dev_mode=False, use_color=True):
        self.print_colored(message, level="info", file=file, line=line, dev_mode=dev_mode, use_color=use_color)

    def print_warning(self, message, file=None, line=None, dev_mode=False, use_color=True):
        self.print_colored(message, level="warning", file=file, line=line, dev_mode=dev_mode, use_color=use_color)

    def print_debug(self, message, file=None, line=None, dev_mode=False, use_color=True):
        self.print_colored(message, level="debug", file=file, line=line, dev_mode=dev_mode, use_color=use_color)

    def print_progress(self, current, total, prefix=None):
        from cli.progress_bar import print_progress_bar
        print_progress_bar(current, total, prefix=prefix)

    def print_event(self, event_type, payload):
        if event_type == 'gcode_generated':
            self.print(f"[EVENTO] G-code generado para: {payload['svg_file']} → {payload['gcode_file']}", color='green')
        elif event_type == 'gcode_rescaled':
            self.print(f"[EVENTO] G-code reescalado: {payload['input_file']} → {payload['output_file']} (escala: {payload['scale_factor']:.3f})", color='blue')
        # Se pueden agregar más eventos aquí

    def prompt_selection(self, prompt, options):
        print(prompt)
        for idx, opt in enumerate(options, 1):
            print(f"  [{idx}] {opt}")
        exit_keywords = {'salir', 'exit', 'quit'}
        while True:
            try:
                user_input = input("Seleccione una opción: ")
                if user_input.strip().lower() in exit_keywords:
                    print("\nSaliendo del programa. ¡Hasta luego!")
                    exit(0)
                selection = int(user_input)
                if 1 <= selection <= len(options):
                    return selection
                else:
                    print("Selección inválida. Intente nuevamente.")
            except ValueError:
                print("Por favor, ingrese un número válido.")
            except KeyboardInterrupt:
                print("\nSaliendo del programa por interrupción (Ctrl+C).")
                exit(0)

    def prompt_yes_no(self, prompt, default_yes=True):
        default = "S/n" if default_yes else "s/N"
        prompt_full = f"{prompt} ({default}): "
        while True:
            resp = input(prompt_full).strip().lower()
            if not resp:
                return default_yes
            if resp in ("s", "si", "y", "yes"):
                return True
            if resp in ("n", "no"):
                return False
            print("Por favor, responda 's' (sí) o 'n' (no).")

    def print_colored(self, message, level="info", file=None, line=None, dev_mode=False, use_color=True):
        """
        Imprime un mensaje con color y formato según nivel.
        Si dev_mode es True, agrega archivo y línea si se proveen.
        Niveles: debug (cyan), info (green), warning (yellow), error (magenta)
        """
        color_map = {
            "debug": "cyan",
            "info": "green",
            "warning": "yellow",
            "error": "magenta"
        }
        color = color_map.get(level, None) if use_color else None
        prefix_map = {
            "debug": "[DEBUG]",
            "info": "[INFO]",
            "warning": "[WARN]",
            "error": "[ERROR]"
        }
        prefix = prefix_map.get(level, "[INFO]")
        if dev_mode and file and line:
            prefix = f"{prefix} - {file}:{line}"
        msg = f"{prefix} {message}"
        if self.color_service and color:
            msg = self.color_service.colorize(msg, color)
        print(msg)

    # Métodos adicionales para mensajes específicos, progreso, etc. pueden agregarse aquí
