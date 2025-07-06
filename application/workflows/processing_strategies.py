"""
Estrategias para el procesamiento de entrada en el workflow no interactivo.
"""
from abc import ABC, abstractmethod
from pathlib import Path

class ProcessingStrategy(ABC):
    " "
    @abstractmethod
    def process(self, workflow, args, input_data, temp_path, output_path, optimize, rescale):
        pass

class SvgProcessingStrategy(ProcessingStrategy):
    " "
    def process(self, workflow, args, input_data, temp_path, output_path, optimize, rescale):
        # --- Soporte para surface-preset en modo batch ---
        surface_preset = getattr(args, 'surface_preset', None)
        if surface_preset:
            presets = workflow.config.get("SURFACE_PRESETS", {})
            plotter_max_area = workflow.config.plotter_max_area_mm
            if surface_preset in presets:
                dims = presets[surface_preset]
                # Validar contra área máxima
                if dims[0] > plotter_max_area[0] or dims[1] > plotter_max_area[1]:
                    # Por defecto: escalar
                    scale_w = plotter_max_area[0] / dims[0]
                    scale_h = plotter_max_area[1] / dims[1]
                    scale = min(scale_w, scale_h)
                    dims = [round(dims[0]*scale, 2), round(dims[1]*scale, 2)]
                    workflow.presenter.print(f"[WARN] Área objetivo del preset '{surface_preset}' excedía el área máxima. Escalado automático a {dims[0]}x{dims[1]} mm.", color='yellow')
                # Set TARGET_WRITE_AREA_MM in config, compatible with both UserConfig and other config types
                if hasattr(workflow.config, 'set') and callable(getattr(workflow.config, 'set')):
                    workflow.config.set("TARGET_WRITE_AREA_MM", dims)
                else:
                    try:
                        # Try attribute assignment or dict-like assignment
                        if hasattr(workflow.config, '__setitem__'):
                            workflow.config["TARGET_WRITE_AREA_MM"] = dims
                        else:
                            setattr(workflow.config, "TARGET_WRITE_AREA_MM", dims)
                    except (AttributeError, TypeError) as e:
                        workflow.presenter.print(f"[ERROR] No se pudo asignar TARGET_WRITE_AREA_MM en config: {e}", color='red')
                workflow.presenter.print(f"[INFO] Área de escritura configurada por preset: {dims[0]}x{dims[1]} mm ({surface_preset})", color='green')
            else:
                available = ', '.join(presets.keys())
                workflow.presenter.print(f"[ERROR] El preset '{surface_preset}' no existe. Disponibles: {available}", color='red')
                return 2
        svg_loader_factory = workflow.container.get_svg_loader
        workflow.presenter.print("processing_start", color='blue')
        if input_data is not None:
            # SVG desde stdin
            from tempfile import NamedTemporaryFile
            with NamedTemporaryFile(delete=False, mode='w', encoding='utf-8', suffix='.svg') as tmp:
                tmp.write(input_data)
                tmp_path = tmp.name
            temp_path = tmp_path
        paths = svg_loader_factory(temp_path).get_paths()
        workflow.presenter.print("processing_complete", color='green')
        geometry_service = workflow.container.domain_factory.create_geometry_service()
        if hasattr(geometry_service, "calculate_bbox"):
            bbox = geometry_service.calculate_bbox(paths)
        else:
            raise AttributeError("geometry_service does not have a public 'calculate_bbox' method.")
        _xmin, _xmax, _ymin, _ymax = bbox
        geometry_service = workflow.container.domain_factory.create_geometry_service()
        if hasattr(geometry_service, "center"):
            _cx, cy = geometry_service.center(bbox)
        else:
            raise AttributeError("geometry_service does not have a public 'center' method.")
        transform_strategies = []
        if workflow.config.get_mirror_vertical():
            from domain.services.path_transform_strategies import MirrorVerticalStrategy
            transform_strategies.append(MirrorVerticalStrategy(cy))
        path_processor = workflow.container.path_processing_service or workflow.container.create_path_processing_service()
        generator = workflow.container.get_gcode_generator(transform_strategies=transform_strategies)
        gcode_service = workflow.container.gcode_generation_service or workflow.container.create_gcode_generation_service(generator)
        compression_service = workflow.container.gcode_compression_service or workflow.container.create_gcode_compression_service()
        config_reader = workflow.container.adapter_factory.create_config_adapter(workflow.config)
        compress_use_case = workflow.container.compress_gcode_use_case or workflow.container.create_compress_gcode_use_case(compression_service, config_reader)
        svg_to_gcode_use_case = workflow.container.create_svg_to_gcode_use_case(
            svg_loader_factory=svg_loader_factory,
            path_processing_service=path_processor,
            gcode_generation_service=gcode_service,
            gcode_compression_use_case=compress_use_case,
            logger=workflow.logger,
            filename_service=workflow.filename_service,
            i18n=workflow.presenter.i18n
        )
        tool_type = getattr(args, 'tool', 'pen')
        double_pass = getattr(args, 'double_pass', True)
        context = {
            "tool_type": tool_type,
            "double_pass": double_pass
        }
        result = svg_to_gcode_use_case.execute(temp_path, context=context)
        gcode_lines = result['compressed_gcode'] if optimize else result['gcode_lines']
        if output_path == '-' or output_path is None:
            import sys
            sys.stdout.write("\n".join(gcode_lines) + "\n")
            return 0
        else:
            # Asegura que output_path sea un string o Path, no una lista
            if isinstance(output_path, list):
                output_path = output_path[0]
            workflow.write_gcode_file(Path(output_path), gcode_lines)
            out_file = output_path
            workflow.presenter.print("processing_complete", color='green')
            msg = workflow.presenter.i18n.get("success_refactor", output_file=out_file)
            workflow.presenter.print(msg, color='green')
            return 0

class GcodeProcessingStrategy(ProcessingStrategy):
    def process(self, workflow, args, input_data, temp_path, output_path, optimize, rescale):
        if input_data is not None:
            # GCODE desde stdin
            from tempfile import NamedTemporaryFile
            with NamedTemporaryFile(delete=False, mode='w', encoding='utf-8', suffix='.gcode') as tmp:
                tmp.write(input_data)
                tmp_path = tmp.name
            temp_path = tmp_path
        if optimize:
            refactor_use_case = workflow.container.gcode_to_gcode_use_case or workflow.container.create_gcode_to_gcode_use_case(
                filename_service=workflow.filename_service,
                logger=workflow.logger
            )
            result = refactor_use_case.execute(temp_path)
            gcode_out = open(result['output_file'], encoding='utf-8').read().splitlines()
            if output_path == '-' or output_path is None:
                import sys
                sys.stdout.write("\n".join(gcode_out) + "\n")
                return 0
            else:
                workflow.write_gcode_file(Path(output_path), gcode_out)
                out_file = output_path
                msg = workflow.presenter.i18n.get("success_refactor", output_file=out_file)
                workflow.presenter.print(msg, color='green')
                workflow.presenter.print("success_optimize", color='green', changes=result['changes_made'])
                return 0
        elif rescale:
            rescale_use_case = workflow.container.gcode_rescale_use_case or workflow.container.create_gcode_rescale_use_case(
                filename_service=workflow.filename_service,
                logger=workflow.logger,
                config_provider=workflow.config
            )
            result = rescale_use_case.execute(temp_path, rescale)
            gcode_out = open(result['output_file'], encoding='utf-8').read().splitlines()
            if output_path == '-' or output_path is None:
                import sys
                sys.stdout.write("\n".join(gcode_out) + "\n")
                return 0
            else:
                workflow.write_gcode_file(Path(output_path), gcode_out)
                out_file = output_path
                original_dim = result.get('original_dimensions', {})
                new_dim = result.get('new_dimensions', {})
                msg = workflow.presenter.i18n.get("success_rescale", output_file=out_file)
                workflow.presenter.print(msg, color='green')
                workflow.presenter.print("rescale_original", width=original_dim.get('width', 0), height=original_dim.get('height', 0))
                workflow.presenter.print("rescale_new", width=new_dim.get('width', 0), height=new_dim.get('height', 0))
                workflow.presenter.print("rescale_factor", factor=result.get('scale_factor', 1.0))
                workflow.presenter.print("rescale_cmds", g0g1=result['commands_rescaled']['g0g1'], g2g3=result['commands_rescaled']['g2g3'])
                return 0
        workflow.presenter.print("error_occurred", color='red')
        return 3
