"""
Path: adapters/output/gcode_generator_adapter.py
Adapter for G-code generation, implementing the GcodeGeneratorPort domain port.
"""

from typing import List, Optional
from tqdm import tqdm

from domain.entities.point import Point
from domain.ports.path_transform_strategy_port import PathTransformStrategyPort
from domain.ports.path_sampler_port import PathSamplerPort
from domain.ports.transform_manager_port import TransformManagerPort
from domain.ports.gcode_generator_port import GcodeGeneratorPort
from domain.geometry.scale_manager import ScaleManager
from domain.gcode.gcode_border_rectangle_detector import GCodeBorderRectangleDetector
from domain.gcode.gcode_border_filter import GCodeBorderFilter
from domain.ports.gcode_optimization_chain_port import GcodeOptimizationChainPort
from domain.ports.config_port import ConfigPort
from domain.ports.logger_port import LoggerPort
from domain.ports.transform_manager_port import NullTransformManager
from domain.services.optimization.trajectory_optimizer import TrajectoryOptimizer
from domain.compression_config import CompressionConfig

from infrastructure.transform_manager import TransformManager
from infrastructure.adapters.reference_marks_generator import ReferenceMarksGenerator
from infrastructure.logger_helper import LoggerHelper

from adapters.output.feed_rate_strategy import FeedRateStrategy
from adapters.output.sample_transform_pipeline import SampleTransformPipeline
from adapters.output.gcode_builder_helper import GCodeBuilderHelper
from adapters.output.curvature_feed_calculator import CurvatureFeedCalculator
from adapters.output.gcode_generation_config_helper import GcodeGenerationConfigHelper
from adapters.output.gcode_compression_factory import GcodeCompressionFactory

class GCodeGeneratorAdapter(GcodeGeneratorPort, LoggerHelper):
    " Generador de G-code adaptado a los puertos del dominio. "
    def __init__(
        self,
        *,
        path_sampler: PathSamplerPort,
        feed: float,
        cmd_down: str,
        cmd_up: str,
        step_mm: float,
        dwell_ms: int,
        max_height_mm: float,
        max_width_mm: float = 180.0,
        config: ConfigPort,  # Inject config port
        logger: LoggerPort = None,
        transform_strategies: Optional[List[PathTransformStrategyPort]] = None,
        optimizer: Optional[GcodeOptimizationChainPort] = None,
        _transform_manager: Optional[TransformManagerPort] = None,
        i18n=None
    ):
        LoggerHelper.__init__(self, config=config, logger=logger)
        self.feed = feed
        self.cmd_down = cmd_down
        self.cmd_up = cmd_up
        self.step_mm = step_mm
        self.dwell_ms = dwell_ms
        self.max_height_mm = max_height_mm
        self.max_width_mm = max_width_mm
        self.logger: LoggerPort = logger
        self.transform_strategies = transform_strategies or []
        if self.transform_strategies:
            for s in self.transform_strategies:
                if not isinstance(s, PathTransformStrategyPort):
                    raise TypeError("Todas las estrategias deben implementar PathTransformStrategy")
        self.path_sampler = path_sampler
        # Usar TransformManager real si hay estrategias, si no NullTransformManager
        if self.transform_strategies:
            self.transform_manager = TransformManager(self.transform_strategies, logger=self.logger)
        else:
            self.transform_manager = NullTransformManager()
        self.optimizer = optimizer
        self.config = config
        self.feed_rate_strategy = FeedRateStrategy(
            base_feed=feed,
            curvature_factor=getattr(config, 'curvature_adjustment_factor', 0.35),
            min_feed_factor=getattr(config, 'minimum_feed_factor', 0.4)
        )
        self.curvature_feed_calculator = CurvatureFeedCalculator(self.feed_rate_strategy)
        self.i18n = i18n
        # Asegura que config tenga i18n para la compresión
        if self.i18n and not hasattr(self.config, 'i18n'):
            setattr(self.config, 'i18n', self.i18n)


    def generate_gcode_commands(self, all_points: List[List[Point]], use_relative_moves: bool = False):
        " Genera los comandos G-code a partir de los puntos muestreados y transformados"
        def feed_fn(prev_pt, curr_pt, next_pt, future_pt):
            " Calcula el feed rate basado en la curvatura entre puntos"
            feed = self.curvature_feed_calculator.adjust_feed(prev_pt, curr_pt, next_pt)
            if future_pt is not None:
                future_feed = self.curvature_feed_calculator.adjust_feed(curr_pt, next_pt, future_pt)
                feed = min(feed, future_feed)
            return feed
        builder_helper = GCodeBuilderHelper(self.cmd_down, self.cmd_up, self.dwell_ms)
        return builder_helper.build(all_points, feed_fn, use_relative_moves=use_relative_moves)

    def generate(self, paths, svg_attr: dict, context=None) -> list:  # pylint: disable=unused-argument
        """
        Genera las líneas de G-code a partir de los paths y atributos SVG.
        El parámetro context permite pasar información adicional (por ejemplo, tool_diameter).
        """
        # Usar TARGET_WRITE_AREA_MM para todos los cálculos y logs
        # Compatibilidad con ConfigAdapter y Config
        if hasattr(self.config, 'get_target_write_area_mm'):
            target_write_area_mm = self.config.get_target_write_area_mm()
        else:
            target_write_area_mm = self.config.get("TARGET_WRITE_AREA_MM", [297.0, 210.0])
        if hasattr(self.config, 'get_plotter_max_area_mm'):
            plotter_max_area_mm = self.config.get_plotter_max_area_mm()
        else:
            plotter_max_area_mm = self.config.get("PLOTTER_MAX_AREA_MM", [300.0, 260.0])
        self.logger.info(f"Máximos configurados: ancho={target_write_area_mm[0]:.4g}mm, alto={target_write_area_mm[1]:.4g}mm")
        if (target_write_area_mm[0] > plotter_max_area_mm[0] or target_write_area_mm[1] > plotter_max_area_mm[1]):
            self.logger.warning(
                f"TARGET_WRITE_AREA_MM ({target_write_area_mm[0]}x{target_write_area_mm[1]}mm) "
                f"excede PLOTTER_MAX_AREA_MM ({plotter_max_area_mm[0]}x{plotter_max_area_mm[1]}mm)"
            )
        # Usar estos valores para escalado
        self.max_width_mm = target_write_area_mm[0]
        self.max_height_mm = target_write_area_mm[1]
        # Validaciones de configuración|
        if self.step_mm <= 0:
            self.logger.warning(self.i18n.get("WARN_STEP_MM_INVALID", value=self.step_mm))
        if not self.path_sampler:
            self.logger.error(self.i18n.get("ERR_MISSING_PATH_SAMPLER"))
            raise ValueError("PathSamplerPort is required")
        gcode = []  # Valor por defecto para evitar UnboundLocalError
        # --- INICIO: Incorporar marcas de referencia ---
        ref_marks_generator = ReferenceMarksGenerator(logger=self.logger, i18n=self.i18n)
        ref_marks_gcode = ref_marks_generator.generate(
            width=self.max_width_mm,
            height=self.max_height_mm
        )
        # --- FIN: Incorporar marcas de referencia ---
        # Log orden y distancia antes de optimizar
        optimizer = TrajectoryOptimizer()
        # Loguear inicio de optimización
        self._debug(self.i18n.get("INFO_OPTIMIZING_PATHS"))
        # Barra de progreso con tqdm para optimización
        use_tqdm = True
        pbar = None
        def progress_callback(current, total):
            nonlocal pbar
            if use_tqdm:
                if pbar is None and total > 0:
                    pbar = tqdm(total=total, desc=self.i18n.get('OPTIMIZING_PATHS'), ncols=60)
                if pbar is not None:
                    pbar.n = current
                    pbar.refresh()
                    if current == total:
                        pbar.n = total
                        pbar.refresh()
                        pbar.close()
                        pbar = None
            else:
                percent = int((current / float(total)) * 100) if total else 100
                print(f"Progreso: {percent}%")
        # Usar barra de progreso con tqdm
        optimized_paths = optimizer.optimize_order(paths, progress_callback=progress_callback)
        if pbar is not None and not pbar.disable:
            pbar.close()
        # Loguear si la optimización no tuvo efecto
        if not optimized_paths or optimized_paths == paths:
            self.logger.warning(self.i18n.get("WARN_NO_OPTIMIZATION"))

        # Usar instancia de ScaleManager para debug configurable
        # --- INICIO: Re-escalado iterativo ---
        MAX_ITER = 3
        TOLERANCIA = 0.5  # mm
        FACTOR_MINIMO = 0.05
        factor_historial = []
        # Factor inicial desde viewbox_scale
        scale_manager = ScaleManager(config_provider=self.config, logger=self.logger)
        factor = scale_manager.viewbox_scale(svg_attr)
        scale = factor
        for intento in range(1, MAX_ITER + 1):
            scale = factor
            # Aplicar escalado para alto y ancho
            scale = scale_manager.adjust_scale_for_max_height(optimized_paths, scale, self.max_height_mm)
            scale = scale_manager.adjust_scale_for_max_width(optimized_paths, scale, self.max_width_mm)
            all_points = self.sample_transform_pipeline(optimized_paths, scale)
            flat_points = [pt for sublist in all_points for pt in sublist]
            if flat_points:
                xs = [pt.x for pt in flat_points]
                ys = [pt.y for pt in flat_points]
                real_width = max(xs) - min(xs)
                real_height = max(ys) - min(ys)
                self.logger.info(f"[Iteración {intento}] Escala aplicada: {scale:.4g}, ancho={real_width:.4g}mm, alto={real_height:.4g}mm")
                factor_historial.append(scale)
                excedente = False
                if real_width > self.max_width_mm + TOLERANCIA:
                    nuevo_factor = scale * (self.max_width_mm / real_width)
                    self.logger.warning(f"Excedente de ancho: {real_width:.4g}mm > {self.max_width_mm:.4g}mm. Nuevo factor: {nuevo_factor:.4g}")
                    factor = nuevo_factor
                    excedente = True
                if real_height > self.max_height_mm + TOLERANCIA:
                    nuevo_factor = scale * (self.max_height_mm / real_height)
                    self.logger.warning(f"Excedente de alto: {real_height:.4g}mm > {self.max_height_mm:.4g}mm. Nuevo factor: {nuevo_factor:.4g}")
                    factor = min(factor, nuevo_factor)
                    excedente = True
                if factor < FACTOR_MINIMO:
                    self.logger.error(f"Factor de escala demasiado pequeño: {factor:.4g}. Abortando.")
                    raise ValueError("No es posible ajustar el escalado sin perder calidad.")
                if not excedente:
                    break
            else:
                real_width = real_height = 0
                factor_historial.append(scale)
        if excedente:
            self.logger.error("No se pudo ajustar el escalado tras el máximo de intentos.")
            raise ValueError("No se pudo ajustar el escalado tras el máximo de intentos.")
        # --- FIN: Re-escalado iterativo ---
        self._debug(self.i18n.get("DEBUG_SCALE_APPLIED", scale=f"{scale:.3f}"))
        remove_border = GcodeGenerationConfigHelper.get_remove_border(self.config)
        use_relative_moves = GcodeGenerationConfigHelper.get_use_relative_moves(self.config)
        from adapters.output.gcode_analyzer import GCodeAnalyzer
        MAX_ITER_GCODE = 3
        TOLERANCIA = 0.5  # mm
        FACTOR_MINIMO = 0.05
        gcode_factor_historial = []
        gcode_excedente = False
        for intento_gcode in range(1, MAX_ITER_GCODE + 1):
            try:
                gcode, _metrics = self.generate_gcode_commands(all_points, use_relative_moves=use_relative_moves)
            except Exception:
                self.logger.exception(self.i18n.get("ERR_GCODE_BUILD_FAILED"))
                raise
            # Only calculate width if gcode is not empty
            gcode_width = 0
            if gcode:
                gcode_width = GCodeAnalyzer.get_width_from_gcode_lines(gcode)
            self.logger.info(f"[Iteración G-code {intento_gcode}] G-code final: ancho={gcode_width:.4g}mm")
            gcode_factor_historial.append(scale)
            gcode_excedente = False
            if gcode_width > self.max_width_mm + TOLERANCIA:
                nuevo_factor = scale * (self.max_width_mm / gcode_width)
                self.logger.warning(f"Excedente de ancho en G-code: {gcode_width:.4g}mm > {self.max_width_mm:.4g}mm. Nuevo factor: {nuevo_factor:.4g}")
                scale = nuevo_factor
                # Recalcular all_points con el nuevo factor
                all_points = self.sample_transform_pipeline(optimized_paths, scale)
                gcode_excedente = True
            # Si quieres controlar el alto del G-code, agrega aquí lógica similar
            if scale < FACTOR_MINIMO:
                self.logger.error(f"Factor de escala demasiado pequeño en G-code: {scale:.4g}. Abortando.")
                raise ValueError("No es posible ajustar el escalado del G-code sin perder calidad.")
            if not gcode_excedente:
                break
        if gcode_excedente:
            self.logger.error("No se pudo ajustar el escalado del G-code tras el máximo de intentos.")
            raise ValueError("No se pudo ajustar el escalado del G-code tras el máximo de intentos.")
        compression_service = GcodeCompressionFactory.get_compression_service(
            self.config,
            logger=self.logger
        )
        if compression_service:
            compression_config = CompressionConfig()
            gcode, _ = compression_service.compress(gcode, compression_config)
        if remove_border:
            detector = GCodeBorderRectangleDetector()
            border_filter = GCodeBorderFilter(detector)
            # Detectar borde antes de filtrar

            gcode = border_filter.filter(gcode if isinstance(gcode, str) else '\n'.join(gcode))
            if isinstance(gcode, str):
                gcode = gcode.split('\n')
        # --- INICIO: Incorporar marcas de referencia ---
        ref_marks_generator = ReferenceMarksGenerator(logger=self.logger, i18n=self.i18n)
        ref_marks_gcode = ref_marks_generator.generate(
            width=self.max_width_mm,
            height=self.max_height_mm
        )
        # Evitar duplicación de encabezados (G21, G90, cmd_up)
        encabezados = {"G21", "G90", self.cmd_up}
        # Ensure gcode is a list of strings
        if isinstance(gcode, str):
            gcode_lines = gcode.split('\n')
        elif isinstance(gcode, list):
            # Flatten if nested lists
            gcode_lines = []
            for item in gcode:
                if isinstance(item, str):
                    gcode_lines.append(item)
                elif isinstance(item, list):
                    gcode_lines.extend(str(x) for x in item)
                else:
                    gcode_lines.append(str(item))
        else:
            gcode_lines = [str(gcode)]
        # Remove duplicate headers at the start
        while gcode_lines and gcode_lines[0].strip() in encabezados:
            gcode_lines.pop(0)
        # ref_marks_gcode may be string or list
        if isinstance(ref_marks_gcode, str):
            ref_marks_lines = ref_marks_gcode.split('\n')
        elif isinstance(ref_marks_gcode, list):
            ref_marks_lines = [str(x) for x in ref_marks_gcode]
        else:
            ref_marks_lines = [str(ref_marks_gcode)]
        # Concatenate reference marks and gcode
        final_gcode = ref_marks_lines + gcode_lines
        # --- FIN: Incorporar marcas de referencia ---
        return final_gcode

    def sample_transform_pipeline(self, paths, scale) -> List[List[Point]]:
        " Aplica el pipeline de muestreo y transformación a los paths"
        pipeline = SampleTransformPipeline(self.path_sampler, self.transform_manager, scale)
        return pipeline.process(paths)
