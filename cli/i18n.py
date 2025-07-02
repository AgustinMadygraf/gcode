"""
Diccionario de mensajes para internacionalización CLI.
Organizado por etiqueta → idioma → valor para mejor mantenibilidad.
"""

MESSAGES = {
    'DEBUG_DEV_MODE_ON': {
        'es': "[DEV] Modo desarrollador activo: logging DEBUG y stacktrace extendido.",
        'en': "[DEV] Developer mode active: DEBUG logging and extended stacktrace.",
        'zh': "[DEV] 开发者模式已激活：DEBUG 日志和扩展堆栈跟踪",
    },
    'MENU_MAIN_TITLE': {
        'es': "Menú Principal",
        'en': "Main Menu",
        'zh': "主菜单",
    },
    'MENU_OPTION_CONVERT': {
        'es': "1. Convertir SVG a G-code",
        'en': "1. Convert SVG to G-code",
        'zh': "1. 转换 SVG 到 G代码",
    },
    'MENU_OPTION_OPTIMIZE': {
        'es': "2. Optimizar archivo G-code existente",
        'en': "2. Optimize existing G-code file",
        'zh': "2. 优化现有 G代码文件",
    },
    'INFO_SVG_FILES_FOUND': {
        'es': "Archivos SVG encontrados:",
        'en': "SVG files found:",
        'zh': "找到的 SVG 文件：",
    },
    'OPTION_CANCEL': {
        'es': "  [0] Cancelar",
        'en': "[0] Cancel",
        'zh': "[0] 取消",
    },
    'PROMPT_SELECT_OPTION': {
        'es': "Seleccione una opción:",
        'en': "Enter option number:",
        'zh': "请输入选项编号：",
    },
    'OPTION_SVG_FILE': {
        'es': "[{num}] {filename}",
        'en': "[{num}] {filename}",
        'zh': "[{num}] {filename}",
    },
    'PROMPT_SELECT_SVG_FILE': {
        'es': "Seleccione un archivo SVG por número:",
        'en': "Select an SVG file by number:",
        'zh': "请选择 SVG 文件编号：",
    },
    'INFO_SVG_SELECTED': {
        'es': "Archivo SVG seleccionado: {filename}",
        'en': "SVG file selected: {filename}",
        'zh': "已选择 SVG 文件：{filename}",
    },
    'INFO_GCODE_OUTPUT': {
        'es': "Archivo G-code de salida: {filename}",
        'en': "Output G-code file: {filename}",
        'zh': "输出 G代码文件：{filename}",
    },
    'INFO_PROCESSING_FILE': {
        'es': "Procesando archivo… esto puede tardar unos segundos.",
        'en': "Processing file… this may take a few seconds.",
        'zh': "正在处理文件... 可能需要几秒钟",
    },
    'INFO_PROCESSING_DONE': {
        'es': "Procesamiento completado",
        'en': "Processing completed",
        'zh': "处理完成",
    },
    'OPTION_TOOL_PEN': {
        'es': "[1] Lapicera (sólo contornos)",
        'en': "[1] Pen (contours only)",
        'zh': "[1] 钢笔 (仅轮廓)",
    },
    'OPTION_TOOL_MARKER': {
        'es': "[2] Fibrón grueso (plenos/contornos)",
        'en': "[2] Marker (fills/contours)",
        'zh': "[2] 粗记号笔 (填充/轮廓)",
    },
    'PROMPT_SELECT_TOOL': {
        'es': "Seleccione una opción:",
        'en': "Select an option:",
        'zh': "请选择工具类型：",
    },
    'OPTION_YES': {
        'es': "[s] Sí",
        'en': "[y] Yes",
        'zh': "[S] 是",
    },
    'OPTION_NO': {
        'es': "[n] No",
        'en': "[n] No",
        'zh': "[N] 否",
    },
    'PROMPT_DOUBLE_PASS': {
        'es': "¿Desea realizar doble pasada en contornos? [S/n]:",
        'en': "Double pass on contours? [Y/n]:",
        'zh': "轮廓是否进行双遍绘制? [S/n]:",
    },
    'INFO_SVG_LOAD': {
        'es': "Carga de SVG: {filename}",
        'en': "SVG loaded: {filename}",
        'zh': "已加载 SVG: {filename}",
    },
    'INFO_PATHS_EXTRACTED': {
        'es': "Paths extraídos: {count}",
        'en': "Paths extracted: {count}",
        'zh': "提取路径数: {count}",
    },
    'INFO_PATHS_PROCESSED': {
        'es': "Paths útiles tras procesamiento: {count}",
        'en': "Useful paths after processing: {count}",
        'zh': "有效路径数: {count}",
    },
    'DEBUG_PATHS_ORDER_ORIG': {
        'es': "Orden original de paths: {list}",
        'en': "Original path order: {list}",
        'zh': "原始路径顺序: {list}",
    },
    'DEBUG_TOTAL_DIST_ORIG': {
        'es': "Distancia total original: {dist} mm",
        'en': "Original total distance: {dist} mm",
        'zh': "原始总距离: {dist} mm",
    },
    'DEBUG_PATHS_ORDER_OPT': {
        'es': "Orden optimizado de paths: {list}",
        'en': "Optimized path order: {list}",
        'zh': "优化后路径顺序: {list}",
    },
    'DEBUG_TOTAL_DIST_OPT': {
        'es': "Distancia total optimizada: {dist} mm",
        'en': "Optimized total distance: {dist} mm",
        'zh': "优化后总距离: {dist} mm",
    },
    'DEBUG_BOUNDING_BOX': {
        'es': "Bounding box: xmin={xmin}, xmax={xmax}, ymin={ymin}, ymax={ymax}",
        'en': "Bounding box: xmin={xmin}, xmax={xmax}, ymin={ymin}, ymax={ymax}",
        'zh': "边界框: xmin={xmin}, xmax={xmax}, ymin={ymin}, ymax={ymax}",
    },
    'DEBUG_SCALE_APPLIED': {
        'es': "Escala aplicada: {scale}",
        'en': "Scale applied: {scale}",
        'zh': "应用缩放: {scale}",
    },
    'DEBUG_RELATIVE_MOVES': {
        'es': "Movimientos relativos activados: {enabled}",
        'en': "Relative moves enabled: {enabled}",
        'zh': "相对移动已启用: {enabled}",
    },
    'DEBUG_ARC_COMPRESS': {
        'es': "Compresión ArcCompressor: {percent}%",
        'en': "ArcCompressor compression: {percent}%",
        'zh': "圆弧压缩率: {percent}%",
    },
    'DEBUG_LINE_COMPRESS': {
        'es': "Compresión LineCompressor: {percent}%",
        'en': "LineCompressor compression: {percent}%",
        'zh': "直线压缩率: {percent}%",
    },
    'DEBUG_GCODE_LINES': {
        'es': "Líneas de G-code generadas: {count}",
        'en': "G-code lines generated: {count}",
        'zh': "生成的 G代码行数: {count}",
    },
    'DEBUG_OPTIMIZATION_METRICS': {
        'es': "Métricas de optimización: {metrics}",
        'en': "Optimization metrics: {metrics}",
        'zh': "优化指标: {metrics}",
    },
    'INFO_GCODE_GENERATED': {
        'es': "G-code generado con {count} líneas",
        'en': "G-code generated with {count} lines",
        'zh': "已生成 G代码，共 {count} 行",
    },
    'DEBUG_COMPRESSION_SUMMARY': {
        'es': "Compresión: original={orig}, comprimido={comp}, ratio={ratio}%",
        'en': "Compression: original={orig}, compressed={comp}, ratio={ratio}%",
        'zh': "压缩率: 原始={orig}, 压缩后={comp}, 比率={ratio}%",
    },
    'INFO_GCODE_WRITTEN': {
        'es': "Archivo G-code escrito: {filename}",
        'en': "G-code file written: {filename}",
        'zh': "G代码文件已保存: {filename}",
    },
    'INFO_GCODE_SUCCESS': {
        'es': "✔ G-code generado exitosamente: {filename}",
        'en': "✔ G-code successfully generated: {filename}",
        'zh': "✔ G代码生成成功: {filename}",
    },
    'ARGPARSE_DESCRIPTION': {
        'es': (
            "Convierte archivos SVG en recorridos G-code para plotters o CNC sencillos.\n\n"
            "Ejemplos de uso:\n"
            "  python run.py --input ejemplo.svg --output salida.gcode\n"
            "  python run.py --no-interactive -i ejemplo.svg -o - > resultado.gcode\n"
            "  cat ejemplo.svg | python run.py --no-interactive -i - -o salida.gcode\n"
            "  python run.py --no-interactive --optimize -i entrada.gcode -o optimizado.gcode\n\n"
            "Use -h o --help para ver todas las opciones."
        ),
        'en': (
            "Convert SVG files to G-code toolpaths for simple plotters or CNC.\n\n"
            "Usage examples:\n"
            "  python run.py --input example.svg --output result.gcode\n"
            "  python run.py --no-interactive -i example.svg -o - > result.gcode\n"
            "  cat example.svg | python run.py --no-interactive -i - -o result.gcode\n"
            "  python run.py --no-interactive --optimize -i input.gcode -o optimized.gcode\n\n"
            "Use -h or --help to see all options."
        ),
        'zh': (
            "将 SVG 文件转换为绘图仪或简易 CNC 的 G代码路径\n\n"
            "使用示例:\n"
            "  python run.py --input 示例.svg --output 输出.gcode\n"
            "  python run.py --no-interactive -i 示例.svg -o - > 输出.gcode\n"
            "  cat 示例.svg | python run.py --no-interactive -i - -o 输出.gcode\n"
            "  python run.py --no-interactive --optimize -i 输入.gcode -o 优化后.gcode\n\n"
            "使用 -h 或 --help 查看所有选项"
        ),
    },
    'ARG_NO_INTERACTIVE': {
        'es': "Ejecutar en modo no interactivo",
        'en': "Run in non-interactive mode",
        'zh': "非交互模式运行",
    },
    'ARG_NO_COLOR': {
        'es': "Desactivar colores en la salida",
        'en': "Disable colored output",
        'zh': "禁用彩色输出",
    },
    'ARG_LANG': {
        'es': "Idioma de la interfaz (es, en)",
        'en': "Interface language (es, en)",
        'zh': "界面语言 (es, en, zh)",
    },
    'ARG_INPUT': {
        'es': "Archivo SVG o G-code de entrada (usa '-' para stdin)",
        'en': "Input SVG or G-code file (use '-' for stdin)",
        'zh': "输入的 SVG 或 G-code 文件 (使用 '-' 表示标准输入)",
    },
    'ARG_OUTPUT': {
        'es': "Archivo G-code de salida (usa '-' para stdout)",
        'en': "Output G-code file (use '-' for stdout)",
        'zh': "输出 G-code 文件 (使用 '-' 表示标准输出)",
    },
    'ARG_OPTIMIZE': {
        'es': "Aplicar optimización de movimientos",
        'en': "Apply movement optimization",
        'zh': "应用运动优化",
    },
    'ARG_RESCALE': {
        'es': "Factor de reescalado para el archivo G-code",
        'en': "Rescale factor for the G-code file",
        'zh': "G-code 文件的重缩放因子",
    },
    'ARG_SAVE_CONFIG': {
        'es': "Guardar los argumentos actuales como configuración de usuario",
        'en': "Save current arguments as user config",
        'zh': "将当前参数保存为用户配置",
    },
    'ARG_CONFIG': {
        'es': "Ruta a archivo de configuración personalizado (JSON)",
        'en': "Path to custom config file (JSON)",
        'zh': "自定义配置文件的路径 (JSON)",
    },
    'ARG_TOOL': {
        'es': "Tipo de herramienta: lapicera (pen) o fibrón (marker)",
        'en': "Tool type: pen or marker",
        'zh': "工具类型：钢笔或记号笔",
    },
    'ARG_DOUBLE_PASS': {
        'es': "Usar doble pasada para contornos con lapicera",
        'en': "Use double pass for pen contours",
        'zh': "对钢笔轮廓使用双遍绘制",
    },
    'ARG_NO_DOUBLE_PASS': {
        'es': "Deshabilitar doble pasada para contornos",
        'en': "Disable double pass for contours",
        'zh': "禁用轮廓的双遍绘制",
    },
    'ARG_DEV': {
        'es': "Activar modo desarrollador (logging DEBUG, stacktrace extendido)",
        'en': "Enable developer mode (DEBUG logging, extended stacktrace)",
        'zh': "启用开发者模式 (DEBUG 日志，扩展堆栈跟踪)",
    },
    'ERROR_INVALID_SELECTION': {
        'es': "Selección inválida. Por favor, elija una opción válida.",
        'en': "Invalid selection. Please choose a valid option.",
        'zh': "✖ 无效选择，请选择有效选项",
    },
    'ERROR_GENERIC': {
        'es': "Ocurrió un error inesperado.",
        'en': "An unexpected error occurred.",
        'zh': "✖ 发生意外错误",
    },
    'WARN_INVALID_SELECTION': {
        'es': "Selección inválida. Intente nuevamente.",
        'en': "Invalid selection. Try again.",
        'zh': "⚠ 无效选择，请重试",
    },
    'WARN_INVALID_NUMBER': {
        'es': "Por favor, ingrese un número válido.",
        'en': "Please enter a valid number.",
        'zh': "⚠ 请输入有效数字",
    },
    'WARN_YES_NO': {
        'es': "Por favor, responda 's' (sí) o 'n' (no).",
        'en': "Please answer 'y' (yes) or 'n' (no).",
        'zh': "⚠ 请回答 'S' (是) 或 'N' (否)",
    },
    'INFO_EXIT': {
        'es': "\nSaliendo del programa. ¡Hasta luego!",
        'en': "\nExiting program. Goodbye!",
        'zh': "\n程序退出，再见！",
    },
    'INFO_EXIT_INTERRUPT': {
        'es': "\nSaliendo del programa por interrupción (Ctrl+C).",
        'en': "\nExiting program due to interruption (Ctrl+C).",
        'zh': "\n因中断（Ctrl+C）退出程序。",
    },
    'ERROR_NO_GCODE': {
        'es': "No se seleccionó ningún archivo GCODE.",
        'en': "No GCODE file selected.",
        'zh': "未选择 GCODE 文件。",
    },
    'OPERATION_MENU_TITLE': {
        'es': "Seleccione una operación:",
        'en': "Select an operation:",
        'zh': "请选择操作：",
    },
    'OPERATION_OPTIMIZE': {
        'es': "1. Optimizar archivo G-code",
        'en': "1. Optimize G-code file",
        'zh': "1. 优化 G-code 文件",
    },
    'OPERATION_RESCALE': {
        'es': "2. Reescalar archivo G-code",
        'en': "2. Rescale G-code file",
        'zh': "2. 重缩放 G-code 文件",
    },
    'EXIT': {
        'es': "0. Cancelar",
        'en': "0. Cancel",
        'zh': "0. 取消",
    },
    'ENTER_NUMBER': {
        'es': "Ingrese el número de opción",
        'en': "Enter option number",
        'zh': "请输入选项编号",
    },
    'INVALID_NUMBER': {
        'es': "Por favor, ingrese un número válido.",
        'en': "Please enter a valid number.",
        'zh': "请输入有效数字。",
    },
    'OPERATION_CANCELLED': {
        'es': "Operación cancelada.",
        'en': "Operation cancelled.",
        'zh': "操作已取消。",
    },
    'SUCCESS_REFACTOR': {
        'es': "Archivo G-code optimizado guardado en: {output_file}",
        'en': "Optimized G-code file saved to: {output_file}",
        'zh': "优化后的 G-code 文件已保存至：{output_file}",
    },
    'SUCCESS_OPTIMIZE': {
        'es': "Cambios realizados: {changes}",
        'en': "Changes made: {changes}",
        'zh': "已做更改：{changes}",
    },
    'RESCALE_USING_MAX': {
        'es': "Reescalando usando área máxima de la plotter: {height} mm de alto",
        'en': "Rescaling using max config height: {height} mm",
        'zh': "使用最大配置高度重缩放：{height} 毫米",
    },
    'HEIGHT_GT_ZERO': {
        'es': "La altura debe ser mayor a cero.",
        'en': "Height must be greater than zero.",
        'zh': "高度必须大于零。",
    },
    'SUCCESS_RESCALE': {
        'es': "Archivo G-code reescalado guardado en: {output_file}",
        'en': "Rescaled G-code file saved to: {output_file}",
        'zh': "重缩放后的 G-code 文件已保存至：{output_file}",
    },
    'RESCALE_ORIGINAL': {
        'es': "Dimensiones originales: ancho={width} mm, alto={height} mm",
        'en': "Original dimensions: width={width} mm, height={height} mm",
        'zh': "原始尺寸：宽={width} 毫米，高={height} 毫米",
    },
    'RESCALE_NEW': {
        'es': "Nuevas dimensiones: ancho={width} mm, alto={height} mm",
        'en': "New dimensions: width={width} mm, height={height} mm",
        'zh': "新尺寸：宽={width} 毫米，高={height} 毫米",
    },
    'RESCALE_FACTOR': {
        'es': "Factor de escala aplicado: {factor}",
        'en': "Scale factor applied: {factor}",
        'zh': "应用的缩放因子：{factor}",
    },
    'RESCALE_CMDS': {
        'es': "Comandos reescalados: G0/G1={g0g1}, G2/G3={g2g3}",
        'en': "Commands rescaled: G0/G1={g0g1}, G2/G3={g2g3}",
        'zh': "已重缩放命令：G0/G1={g0g1}，G2/G3={g2g3}",
    },
    'PROMPT_SELECT_SVG_FILE_RANGE': {
        'es': "Seleccione un archivo SVG ({range}):",
        'en': "Select an SVG file ({range}):",
        'zh': "选择一个 SVG 文件 ({range}):",
    },
    'PROMPT_USE_MAX_HEIGHT': {
        'es': "¿Usar área máxima de la plotter ({max_height}mm de alto)? [S/n]:",
        'en': "Use max config height ({max_height}mm)? [Y/n]:",
        'zh': "使用最大配置高度 ({max_height}mm)？ [S/n]:",
    },
    'ERROR_FILE_NOT_FOUND': {
        'es': "Archivo no encontrado.",
        'en': "File not found.",
        'zh': "文件未找到。",
    },
    'WARN_NOT_IMPLEMENTED': {
        'es': "Funcionalidad aún no implementada.",
        'en': "Feature not implemented yet.",
        'zh': "功能尚未实现。",
    },
    'INFO_OPTIONS': {
        'es': "Opciones:",
        'en': "Options:",
        'zh': "选项：",
    },
    'INFO_DIRECT_EXECUTION': {
        'es': "Ejecución directa: usando archivos especificados por argumentos.",
        'en': "Direct execution: using files specified by arguments.",
        'zh': "直接执行：使用参数指定的文件。",
    },
    'WARN_NO_FILES_FOUND': {
        'es': "No se encontraron archivos SVG ni GCODE disponibles.",
        'en': "No SVG or GCODE files available.",
        'zh': "没有可用的 SVG 或 GCODE 文件。",
    },
    'OPTIMIZING_PATHS': {
        'es': "Optimizando trayectorias...",
        'en': "Optimizing paths...",
        'zh': "正在优化路径...",
    },
    'DEBUG_REMOVE_BORDER': {
        'es': "Eliminación de borde activada: {enabled}",
        'en': "Eliminación de borde activada: {enabled}",
        'zh': "边框移除已激活：{enabled}",
    },
    'WARN_SCALE_REDUCED': {
        'es': "La escala fue reducida a {scale:.3f} para respetar límites físicos.",
        'en': "Scale was reduced to {scale:.3f} to fit physical limits.",
        'zh': "为适应物理限制，缩放比例已降至 {scale:.3f}。",
    },
    'WARN_BORDER_NOT_FOUND': {
        'es': "Se solicitó eliminar borde pero no se detectó ninguno.",
        'en': "Border removal requested but no border was detected.",
        'zh': "请求去除边框，但未检测到任何边框。",
    },
    'INFO_GCODE_FILES_FOUND': {
        'es': "Archivos G-code encontrados:",
        'en': "G-code files found:",
        'zh': "找到的 G-code 文件：",
    },
    'PROMPT_SELECT_GCODE_FILE': {
        'es': "Seleccione un archivo G-code por número:",
        'en': "Select a G-code file by number:",
        'zh': "请选择 G-code 文件编号：",
    },
    'INFO_GCODE_SELECTED': {
        'es': "Archivo G-code seleccionado: {filename}",
        'en': "G-code file selected: {filename}",
        'zh': "已选择 G-code 文件：{filename}",
    },
    'WARN_INVALID_OPTION': {
        'es': "Opción inválida. Intente nuevamente.",
        'en': "Invalid option. Try again.",
        'zh': "⚠ 无效选项，请重试",
    },
}

def get_message(key, lang='es', **kwargs):
    """Obtiene el mensaje localizado y formatea con kwargs si aplica."""
    # Si la clave no existe, devolver la propia clave como fallback
    if key not in MESSAGES:
        return key
    
    # Si el idioma no existe para esa clave, intentar con el idioma por defecto (es)
    message_template = MESSAGES[key].get(lang, MESSAGES[key].get('es', key))
    
    # Aplicar formato si hay argumentos
    if kwargs:
        try:
            return message_template.format(**kwargs)
        except Exception:
            return message_template
    
    return message_template
