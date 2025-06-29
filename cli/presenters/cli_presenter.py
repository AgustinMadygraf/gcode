"""
CliPresenter: Maneja toda la interacción de entrada/salida con el usuario en la CLI.
Permite inyectar dependencias como i18n y manejo de colores.
"""

from infrastructure.logger import logger

class CliPresenter:
    def __init__(self, i18n=None, color_service=None, logger_instance=None):
        self.i18n = i18n
        self.color_service = color_service
        self.logger = logger_instance or logger

    def print(self, message, color=None):
        # Si es clave i18n, traducir
        if message in self.i18n._messages.get(self.i18n._default_lang, {}):
            message = self.i18n.get(message)
        if self.color_service and color:
            message = self.color_service.colorize(message, color)
        self.logger.info(message)

    def input(self, prompt, color=None):
        if self.color_service and color:
            prompt = self.color_service.colorize(prompt, color)
        # Mostrar el prompt solo una vez, con prefijo [INPUT]
        prompt_final = f"[INPUT] {prompt}" if not prompt.strip().startswith('[INPUT]') else prompt
        return input(prompt_final)

    def print_error(self, message, file=None, line=None, dev_mode=False, use_color=True):
        self.print_colored(message, level="error", file=file, line=line, dev_mode=dev_mode, use_color=use_color)

    def print_success(self, message, file=None, line=None, dev_mode=False, use_color=True):
        # Solo pasar el mensaje, el logger agrega el prefijo
        self.logger.info(message)

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
        input_prompt = f"[INPUT] {prompt}" if not prompt.strip().startswith('[INPUT]') else prompt
        for idx, opt in enumerate(options, 1):
            self.print_option(f"  [{idx}] {opt}")
        exit_keywords = {'salir', 'exit', 'quit'}
        while True:
            try:
                user_input = input("Seleccione una opción: ")
                if user_input.strip().lower() in exit_keywords:
                    self.logger.info("\nSaliendo del programa. ¡Hasta luego!")
                    exit(0)
                selection = int(user_input)
                if 1 <= selection <= len(options):
                    return selection
                else:
                    self.logger.warning("Selección inválida. Intente nuevamente.")
            except ValueError:
                self.logger.warning("Por favor, ingrese un número válido.")
            except KeyboardInterrupt:
                self.logger.info("\nSaliendo del programa por interrupción (Ctrl+C).")
                exit(0)

    def prompt_yes_no(self, prompt, default_yes=True):
        default = "S/n" if default_yes else "s/N"
        prompt_full = f"[INPUT] {prompt} ({default}): "
        self.print_option("  [s] Sí")
        self.print_option("  [n] No")
        while True:
            user_input = input(prompt_full).strip().lower()
            if not user_input:
                return default_yes
            if user_input in ("s", "si", "y", "yes"):
                return True
            if user_input in ("n", "no"):
                return False
            self.logger.warning("Por favor, responda 's' (sí) o 'n' (no).")

    def print_colored(self, message, level="info", file=None, line=None, dev_mode=False, use_color=True):
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
        if level == "debug":
            self.logger.debug(msg)
        elif level == "warning":
            self.logger.warning(msg)
        elif level == "error":
            self.logger.error(msg)
        else:
            self.logger.info(msg)

    def print_option(self, message, color=None):
        # Si es clave i18n, traducir
        if message in self.i18n._messages.get(self.i18n._default_lang, {}):
            message = self.i18n.get(message)
        # El color se ignora, se usa el del logger.option
        self.logger.option(message)

    # Métodos adicionales para mensajes específicos, progreso, etc. pueden agregarse aquí
