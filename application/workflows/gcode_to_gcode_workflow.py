"""
Workflow para GCODE a GCODE (optimización/reescalado).
Orquesta el proceso de post-procesamiento de GCODE.
"""
from pathlib import Path

class GcodeToGcodeWorkflow:
    def __init__(self, container, presenter, filename_service, config):
        self.container = container
        self.presenter = presenter
        self.filename_service = filename_service
        self.config = config

    def run(self, config):
        from adapters.input.gcode_file_selector_adapter import GcodeFileSelectorAdapter
        from application.use_cases.gcode_to_gcode_use_case import GcodeToGcodeUseCase
        from application.use_cases.gcode_rescale_use_case import GcodeRescaleUseCase
        gcode_selector = GcodeFileSelectorAdapter(self.config)
        gcode_file = gcode_selector.select_gcode_file()
        if not gcode_file:
            self.presenter.print(self.presenter.i18n.get("error_no_gcode"), color='red')
            return False
        gcode_file = Path(gcode_file)
        self.presenter.print(f"Archivo GCODE seleccionado: {gcode_file}", color='blue')
        self.presenter.print(self.presenter.i18n.get("operation_menu_title"), color='bold')
        self.presenter.print_option(self.presenter.i18n.get("operation_optimize"))
        self.presenter.print_option(self.presenter.i18n.get("operation_rescale"))
        self.presenter.print_option(self.presenter.i18n.get("exit"), color='yellow')
        operation_choice = -1
        while operation_choice not in [0, 1, 2]:
            try:
                operation_choice = int(self.presenter.input(self.presenter.i18n.get("enter_number") + ": "))
            except ValueError:
                self.presenter.print(self.presenter.i18n.get("invalid_number"), color='yellow')
        if operation_choice == 0:
            self.presenter.print(self.presenter.i18n.get("operation_cancelled"), color='yellow')
            return False
        if operation_choice == 1:
            refactor_use_case = GcodeToGcodeUseCase(
                filename_service=self.filename_service,
                logger=self.container.logger
            )
            result = refactor_use_case.execute(gcode_file)
            self.container.event_bus.publish('gcode_refactored', {
                'input_file': gcode_file,
                'output_file': result['output_file'],
                'changes': result['changes_made']
            })
            msg = self.presenter.i18n.get("success_refactor", output_file=result['output_file'])
            self.presenter.print(msg, color='green')
            msg2 = self.presenter.i18n.get("success_optimize", changes=result['changes_made'])
            self.presenter.print(msg2, color='green')
        elif operation_choice == 2:
            # Obtener altura objetivo (usar configuración o solicitar al usuario)
            target_height = None
            use_config = self.presenter.input("\n¿Usar altura máxima de configuración (250mm)? [S/n]: ").strip().lower()
            if use_config != 'n':
                target_height = self.config.max_height_mm
                msg = self.presenter.i18n.get("rescale_using_max", height=target_height)
                self.presenter.print(msg, color='blue')
            else:
                while True:
                    try:
                        target_height = float(self.presenter.input(self.presenter.i18n.get("enter_number") + " (mm): "))
                        if target_height <= 0:
                            self.presenter.print(self.presenter.i18n.get("height_gt_zero"), color='yellow')
                        else:
                            break
                    except ValueError:
                        self.presenter.print(self.presenter.i18n.get("invalid_number"), color='yellow')
            rescale_use_case = GcodeRescaleUseCase(
                filename_service=self.filename_service,
                logger=self.container.logger,
                config_provider=self.config
            )
            result = rescale_use_case.execute(gcode_file, target_height)
            self.container.event_bus.publish('gcode_rescaled', {
                'input_file': gcode_file,
                'output_file': result['output_file'],
                'scale_factor': result['scale_factor'],
                'original_dimensions': result['original_dimensions'],
                'new_dimensions': result['new_dimensions']
            })
            original_dim = result['original_dimensions']
            new_dim = result['new_dimensions']
            msg = self.presenter.i18n.get("success_rescale", output_file=result['output_file'])
            self.presenter.print(msg, color='green')
            msg2 = self.presenter.i18n.get("rescale_original", width=original_dim['width'], height=original_dim['height'])
            self.presenter.print(msg2)
            msg3 = self.presenter.i18n.get("rescale_new", width=new_dim['width'], height=new_dim['height'])
            self.presenter.print(msg3)
            msg4 = self.presenter.i18n.get("rescale_factor", factor=result['scale_factor'])
            self.presenter.print(msg4)
            msg5 = self.presenter.i18n.get("rescale_cmds", g0g1=result['commands_rescaled']['g0g1'], g2g3=result['commands_rescaled']['g2g3'])
            self.presenter.print(msg5)
        return True
