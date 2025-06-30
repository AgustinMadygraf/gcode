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
        self.logger.info(message, stacklevel=3)

    def input(self, prompt, color=None):
        if self.color_service and color:
            prompt = self.color_service.colorize(prompt, color)
        # Mostrar el prompt solo una vez, con prefijo [INPUT]
        prompt_final = f"[INPUT] {prompt}" if not prompt.strip().startswith('[INPUT]') else prompt
        return input(prompt_final)

    def print_error(self, message, file=None, line=None, dev_mode=False, use_color=True):
        self.print_colored(message, level="error", file=file, line=line, dev_mode=dev_mode, use_color=use_color)

    def print_success(self, message, file=None, line=None, dev_mode=False, use_color=True):
        self.logger.info(message, stacklevel=3)

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
                    self.logger.info(self.i18n.get('INFO_EXIT'))
                    exit(0)
                selection = int(user_input)
                if 1 <= selection <= len(options):
                    return selection
                else:
                    self.logger.warning(self.i18n.get('WARN_INVALID_SELECTION'))
            except ValueError:
                self.logger.warning(self.i18n.get('WARN_INVALID_NUMBER'))
            except KeyboardInterrupt:
                self.logger.info(self.i18n.get('INFO_EXIT_INTERRUPT'))
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
            self.logger.warning(self.i18n.get('WARN_YES_NO'))

    def print_colored(self, message, level="info", file=None, line=None, dev_mode=False, use_color=True):
        # Eliminar prefijos manuales, dejar que el logger maneje formato y color
        if level == "debug":
            self.logger.debug(message, stacklevel=3)
        elif level == "warning":
            self.logger.warning(message, stacklevel=3)
        elif level == "error":
            self.logger.error(message, stacklevel=3)
        else:
            self.logger.info(message, stacklevel=3)

    def print_option(self, message, color=None):
        # Si es clave i18n, traducir
        if message in self.i18n._messages.get(self.i18n._default_lang, {}):
            message = self.i18n.get(message)
        # El color se ignora, se usa el del logger.option
        self.logger.option(message)

    def prompt_surface_preset(self, presets, plotter_max_area):
        """Submenú interactivo para seleccionar preset de superficie o ingresar dimensiones personalizadas."""
        options = []
        preset_keys = list(presets.keys())
        for k in preset_keys:
            dims = presets[k]
            options.append(f"{k} ({dims[0]}x{dims[1]} mm)")
        options.append("Custom dimensions (manual input)")
        self.print_option("[0] Cancelar")
        selection = self.prompt_selection("Seleccione un preset de superficie o ingrese dimensiones personalizadas:", options)
        if selection == len(options):
            # Custom
            while True:
                try:
                    w = float(self.input("Ingrese el ancho (mm): "))
                    h = float(self.input("Ingrese el alto (mm): "))
                    dims = [w, h]
                    break
                except ValueError:
                    self.print_warning("Por favor, ingrese valores numéricos válidos.")
            preset_name = "CUSTOM"
        else:
            preset_name = preset_keys[selection-1]
            dims = presets[preset_name]
        # Validar contra área máxima
        if dims[0] > plotter_max_area[0] or dims[1] > plotter_max_area[1]:
            self.print_warning(f"El área seleccionada ({dims[0]}x{dims[1]} mm) excede el área máxima de la plotter ({plotter_max_area[0]}x{plotter_max_area[1]} mm).")
            escalar = self.prompt_yes_no("¿Desea escalar el área objetivo para que entre en el área máxima? (No = excluir parte del dibujo)")
            if escalar:
                scale_w = plotter_max_area[0] / dims[0]
                scale_h = plotter_max_area[1] / dims[1]
                scale = min(scale_w, scale_h)
                dims = [round(dims[0]*scale, 2), round(dims[1]*scale, 2)]
                self.print_success(f"Área objetivo escalada a {dims[0]}x{dims[1]} mm.")
            else:
                self.print_warning("Se excluirá parte del dibujo que exceda el área máxima.")
        return dims, preset_name

    # Métodos adicionales para mensajes específicos, progreso, etc. pueden agregarse aquí
