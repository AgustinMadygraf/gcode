"""
Diccionario de mensajes para internacionalización CLI.
"""

MESSAGES = {
    'es': {
        'DEBUG_DEV_MODE_ON': "[DEV] Modo desarrollador activo: logging DEBUG y stacktrace extendido.",
        'MENU_MAIN_TITLE': "Menú Principal",
        'MENU_OPTION_CONVERT': "1. Convertir SVG a G-code",
        'MENU_OPTION_OPTIMIZE': "2. Optimizar archivo G-code existente",
        'INFO_SVG_FILES_FOUND': "Archivos SVG encontrados:",
        'OPTION_CANCEL': "  [0] Cancelar",
        'PROMPT_SELECT_OPTION': "Seleccione una opción:",
        'INFO_SVG_FILES_FOUND': "Archivos SVG disponibles:",
        'OPTION_SVG_FILE': "[{num}] {filename}",
        'OPTION_CANCEL': "[0] Cancelar",
        'PROMPT_SELECT_SVG_FILE': "Seleccione un archivo SVG por número:",
        'INFO_SVG_SELECTED': "Archivo SVG seleccionado: {filename}",
        'INFO_GCODE_OUTPUT': "Archivo G-code de salida: {filename}",
        'INFO_PROCESSING_FILE': "Procesando archivo… esto puede tardar unos segundos.",
        'INFO_PROCESSING_DONE': "Procesamiento completado",
        'OPTION_TOOL_PEN': "[1] Lapicera (sólo contornos)",
        'OPTION_TOOL_MARKER': "[2] Fibrón grueso (plenos/contornos)",
        'PROMPT_SELECT_TOOL': "Seleccione una opción:",
        'OPTION_YES': "[s] Sí",
        'OPTION_NO': "[n] No",
        'PROMPT_DOUBLE_PASS': "¿Desea realizar doble pasada en contornos? [S/n]:",
        'INFO_SVG_LOAD': "Carga de SVG: {filename}",
        'INFO_PATHS_EXTRACTED': "Paths extraídos: {count}",
        'INFO_PATHS_PROCESSED': "Paths útiles tras procesamiento: {count}",
        'DEBUG_PATHS_ORDER_ORIG': "Orden original de paths: {list}",
        'DEBUG_TOTAL_DIST_ORIG': "Distancia total original: {dist} mm",
        'DEBUG_PATHS_ORDER_OPT': "Orden optimizado de paths: {list}",
        'DEBUG_TOTAL_DIST_OPT': "Distancia total optimizada: {dist} mm",
        'DEBUG_BOUNDING_BOX': "Bounding box: xmin={xmin}, xmax={xmax}, ymin={ymin}, ymax={ymax}",
        'DEBUG_SCALE_APPLIED': "Escala aplicada: {scale}",
        'DEBUG_RELATIVE_MOVES': "Movimientos relativos activados: {enabled}",
        'DEBUG_ARC_COMPRESS': "Compresión ArcCompressor: {percent}%",
        'DEBUG_LINE_COMPRESS': "Compresión LineCompressor: {percent}%",
        'DEBUG_GCODE_LINES': "Líneas de G-code generadas: {count}",
        'DEBUG_OPTIMIZATION_METRICS': "Métricas de optimización: {metrics}",
        'INFO_GCODE_GENERATED': "G-code generado con {count} líneas",
        'DEBUG_COMPRESSION_SUMMARY': "Compresión: original={orig}, comprimido={comp}, ratio={ratio}%",
        'INFO_GCODE_WRITTEN': "Archivo G-code escrito: {filename}",
        'INFO_GCODE_SUCCESS': "✔ G-code generado exitosamente: {filename}",
        'ARGPARSE_DESCRIPTION': (
            "Convierte archivos SVG en recorridos G-code para plotters o CNC sencillos.\n\n"
            "Ejemplos de uso:\n"
            "  python run.py --input ejemplo.svg --output salida.gcode\n"
            "  python run.py --no-interactive -i ejemplo.svg -o - > resultado.gcode\n"
            "  cat ejemplo.svg | python run.py --no-interactive -i - -o salida.gcode\n"
            "  python run.py --no-interactive --optimize -i entrada.gcode -o optimizado.gcode\n\n"
            "Use -h o --help para ver todas las opciones."
        ),
        'ARG_NO_INTERACTIVE': "Ejecutar en modo no interactivo",
        'ARG_NO_COLOR': "Desactivar colores en la salida",
        'ARG_LANG': "Idioma de la interfaz (es, en)",
        'ARG_INPUT': "Archivo SVG o G-code de entrada (usa '-' para stdin)",
        'ARG_OUTPUT': "Archivo G-code de salida (usa '-' para stdout)",
        'ARG_OPTIMIZE': "Aplicar optimización de movimientos",
        'ARG_RESCALE': "Factor de reescalado para el archivo G-code",
        'ARG_SAVE_CONFIG': "Guardar los argumentos actuales como configuración de usuario",
        'ARG_CONFIG': "Ruta a archivo de configuración personalizado (JSON)",
        'ARG_TOOL': "Tipo de herramienta: lapicera (pen) o fibrón (marker)",
        'ARG_DOUBLE_PASS': "Usar doble pasada para contornos con lapicera",
        'ARG_NO_DOUBLE_PASS': "Deshabilitar doble pasada para contornos",
        'ARG_DEV': "Activar modo desarrollador (logging DEBUG, stacktrace extendido)",
        'ERROR_INVALID_SELECTION': "Selección inválida. Por favor, elija una opción válida.",
        'ERROR_GENERIC': "Ocurrió un error inesperado.",
        'WARN_INVALID_SELECTION': "Selección inválida. Intente nuevamente.",
        'WARN_INVALID_NUMBER': "Por favor, ingrese un número válido.",
        'WARN_YES_NO': "Por favor, responda 's' (sí) o 'n' (no).",
        'INFO_EXIT': "\nSaliendo del programa. ¡Hasta luego!",
        'INFO_EXIT_INTERRUPT': "\nSaliendo del programa por interrupción (Ctrl+C).",
        'WARN_INVALID_OPTION': "Opción inválida.",
        'INFO_OPERATION_CANCELLED': "Operación cancelada por el usuario.",
        'WARN_OUT_OF_RANGE': "Selección fuera de rango.",
        'WARN_NO_SVG_FOUND': "No se encontraron archivos SVG en '{svg_input_dir}'.",
        'INFO_ASSIGN_NEW_DIR': "1) Asignar nueva carpeta de entrada",
        'INFO_RETRY': "2) Reintentar (debe colocar un archivo SVG en la carpeta actual)",
        'PROMPT_NEW_SVG_DIR': "Ingrese la nueva ruta de carpeta para SVGs:",
        'INFO_SVG_INPUT_UPDATED': "SVG_INPUT_DIR actualizado a: {new_dir}",
        'WARN_INVALID_DIR': "Carpeta no válida.",
        'INFO_PLACE_SVG_AND_RETRY': "Por favor, coloque al menos un archivo SVG en la carpeta y presione Enter para reintentar.",
        'INFO_GCODE_FILES_FOUND': "\nArchivos GCODE encontrados:",
        'PROMPT_SELECT_GCODE_FILE': "Seleccione un archivo GCODE por número:",
        'WARN_NO_GCODE_FOUND': "No se encontraron archivos GCODE en {gcode_dir}",
        'PROMPT_NEW_GCODE_DIR': "[INPUT] Ingrese otra carpeta (o 'q' para cancelar): ",
        'INFO_OPERATION_CANCELLED_CTRL_C': "\nOperación cancelada por el usuario (Ctrl+C).",
        'ERROR_NO_GCODE': "No se seleccionó ningún archivo GCODE.",
        'OPERATION_MENU_TITLE': "Seleccione una operación:",
        'OPERATION_OPTIMIZE': "1. Optimizar archivo G-code",
        'OPERATION_RESCALE': "2. Reescalar archivo G-code",
        'EXIT': "0. Cancelar",
        'ENTER_NUMBER': "Ingrese el número de opción",
        'INVALID_NUMBER': "Por favor, ingrese un número válido.",
        'OPERATION_CANCELLED': "Operación cancelada.",
        'SUCCESS_REFACTOR': "Archivo G-code optimizado guardado en: {output_file}",
        'SUCCESS_OPTIMIZE': "Cambios realizados: {changes}",
        'RESCALE_USING_MAX': "Reescalando usando altura máxima de configuración: {height} mm",
        'HEIGHT_GT_ZERO': "La altura debe ser mayor a cero.",
        'SUCCESS_RESCALE': "Archivo G-code reescalado guardado en: {output_file}",
        'RESCALE_ORIGINAL': "Dimensiones originales: ancho={width} mm, alto={height} mm",
        'RESCALE_NEW': "Nuevas dimensiones: ancho={width} mm, alto={height} mm",
        'RESCALE_FACTOR': "Factor de escala aplicado: {factor}",
        'RESCALE_CMDS': "Comandos reescalados: G0/G1={g0g1}, G2/G3={g2g3}",
        'PROMPT_SELECT_SVG_FILE_RANGE': "Seleccione un archivo SVG ({range}):",
        'PROMPT_USE_MAX_HEIGHT': "¿Usar altura máxima de configuración ({max_height}mm)? [S/n]:",
        'ERROR_FILE_NOT_FOUND': "Archivo no encontrado.",
        'WARN_NOT_IMPLEMENTED': "Funcionalidad aún no implementada.",
        'INFO_OPTIONS': "Opciones:",
        'INFO_DIRECT_EXECUTION': "Ejecución directa: usando archivos especificados por argumentos.",
        'WARN_NO_FILES_FOUND': "No se encontraron archivos SVG ni GCODE disponibles.",
        'INFO_TECHNICAL_LOGS_HEADER': "--- [LOGS TÉCNICOS] ---",
        'OPTIMIZING_PATHS': "Optimizando trayectorias...",
        # ...agregar más mensajes según se centralicen...
    },
    'en': {
        'DEBUG_DEV_MODE_ON': "[DEV] Developer mode active: DEBUG logging and extended stacktrace.",
        'MENU_MAIN_TITLE': "Main Menu",
        'MENU_OPTION_CONVERT': "1. Convert SVG to G-code",
        'MENU_OPTION_OPTIMIZE': "2. Optimize existing G-code file",
        'PROMPT_SELECT_OPTION': "Enter option number:",
        'INFO_SVG_FILES_FOUND': "SVG files found:",
        'OPTION_SVG_FILE': "[{num}] {filename}",
        'OPTION_CANCEL': "[0] Cancel",
        'PROMPT_SELECT_SVG_FILE': "Select an SVG file by number:",
        'INFO_SVG_SELECTED': "SVG file selected: {filename}",
        'INFO_GCODE_OUTPUT': "Output G-code file: {filename}",
        'INFO_PROCESSING_FILE': "Processing file… this may take a few seconds.",
        'INFO_PROCESSING_DONE': "Processing completed",
        'OPTION_TOOL_PEN': "[1] Pen (contours only)",
        'OPTION_TOOL_MARKER': "[2] Marker (fills/contours)",
        'PROMPT_SELECT_TOOL': "Select an option:",
        'OPTION_YES': "[y] Yes",
        'OPTION_NO': "[n] No",
        'PROMPT_DOUBLE_PASS': "Double pass on contours? [Y/n]:",
        'INFO_SVG_LOAD': "SVG loaded: {filename}",
        'INFO_PATHS_EXTRACTED': "Paths extracted: {count}",
        'INFO_PATHS_PROCESSED': "Useful paths after processing: {count}",
        'DEBUG_PATHS_ORDER_ORIG': "Original path order: {list}",
        'DEBUG_TOTAL_DIST_ORIG': "Original total distance: {dist} mm",
        'DEBUG_PATHS_ORDER_OPT': "Optimized path order: {list}",
        'DEBUG_TOTAL_DIST_OPT': "Optimized total distance: {dist} mm",
        'DEBUG_BOUNDING_BOX': "Bounding box: xmin={xmin}, xmax={xmax}, ymin={ymin}, ymax={ymax}",
        'DEBUG_SCALE_APPLIED': "Scale applied: {scale}",
        'DEBUG_RELATIVE_MOVES': "Relative moves enabled: {enabled}",
        'DEBUG_ARC_COMPRESS': "ArcCompressor compression: {percent}%",
        'DEBUG_LINE_COMPRESS': "LineCompressor compression: {percent}%",
        'DEBUG_GCODE_LINES': "G-code lines generated: {count}",
        'DEBUG_OPTIMIZATION_METRICS': "Optimization metrics: {metrics}",
        'INFO_GCODE_GENERATED': "G-code generated with {count} lines",
        'DEBUG_COMPRESSION_SUMMARY': "Compression: original={orig}, compressed={comp}, ratio={ratio}%",
        'INFO_GCODE_WRITTEN': "G-code file written: {filename}",
        'INFO_GCODE_SUCCESS': "✔ G-code successfully generated: {filename}",
        'ERROR_INVALID_SELECTION': "Invalid selection. Please choose a valid option.",
        'ERROR_GENERIC': "An unexpected error occurred.",
        'WARN_INVALID_SELECTION': "Invalid selection. Try again.",
        'WARN_INVALID_NUMBER': "Please enter a valid number.",
        'WARN_YES_NO': "Please answer 'y' (yes) or 'n' (no).",
        'INFO_EXIT': "\nExiting program. Goodbye!",
        'INFO_EXIT_INTERRUPT': "\nExiting program due to interruption (Ctrl+C).",
        'ERROR_NO_GCODE': "No GCODE file selected.",
        'OPERATION_MENU_TITLE': "Select an operation:",
        'OPERATION_OPTIMIZE': "1. Optimize G-code file",
        'OPERATION_RESCALE': "2. Rescale G-code file",
        'EXIT': "0. Cancel",
        'ENTER_NUMBER': "Enter option number",
        'INVALID_NUMBER': "Please enter a valid number.",
        'OPERATION_CANCELLED': "Operation cancelled.",
        'SUCCESS_REFACTOR': "Optimized G-code file saved to: {output_file}",
        'SUCCESS_OPTIMIZE': "Changes made: {changes}",
        'RESCALE_USING_MAX': "Rescaling using max config height: {height} mm",
        'HEIGHT_GT_ZERO': "Height must be greater than zero.",
        'SUCCESS_RESCALE': "Rescaled G-code file saved to: {output_file}",
        'RESCALE_ORIGINAL': "Original dimensions: width={width} mm, height={height} mm",
        'RESCALE_NEW': "New dimensions: width={width} mm, height={height} mm",
        'RESCALE_FACTOR': "Scale factor applied: {factor}",
        'RESCALE_CMDS': "Commands rescaled: G0/G1={g0g1}, G2/G3={g2g3}",
        'INFO_SVG_INPUT_UPDATED': "SVG_INPUT_DIR updated to: {new_dir}",
        'WARN_INVALID_DIR': "Invalid folder.",
        'INFO_PLACE_SVG_AND_RETRY': "Please place at least one SVG file in the folder and press Enter to retry.",
        'INFO_ASSIGN_NEW_DIR': "1) Set new input folder",
        'INFO_RETRY': "2) Retry (place an SVG file in the current folder)",
        'WARN_NO_SVG_FOUND': "No SVG files found in '{svg_input_dir}'.",
        'WARN_OUT_OF_RANGE': "Selection out of range.",
        'WARN_INVALID_OPTION': "Invalid option.",
        'INFO_OPERATION_CANCELLED': "Operation cancelled by user.",
        'INFO_OPERATION_CANCELLED_CTRL_C': "\nOperation cancelled by user (Ctrl+C).",
        'INFO_GCODE_FILES_FOUND': "\nGCODE files found:",
        'PROMPT_SELECT_GCODE_FILE': "Select a GCODE file by number:",
        'WARN_NO_GCODE_FOUND': "No GCODE files found in {gcode_dir}",
        'PROMPT_NEW_GCODE_DIR': "[INPUT] Enter another folder (or 'q' to cancel): ",
        'ARGPARSE_DESCRIPTION': (
            "Convert SVG files to G-code toolpaths for simple plotters or CNC.\n\n"
            "Usage examples:\n"
            "  python run.py --input example.svg --output result.gcode\n"
            "  python run.py --no-interactive -i example.svg -o - > result.gcode\n"
            "  cat example.svg | python run.py --no-interactive -i - -o result.gcode\n"
            "  python run.py --no-interactive --optimize -i input.gcode -o optimized.gcode\n\n"
            "Use -h or --help to see all options."
        ),
        'ARG_NO_INTERACTIVE': "Run in non-interactive mode",
        'ARG_NO_COLOR': "Disable colored output",
        'ARG_LANG': "Interface language (es, en)",
        'ARG_INPUT': "Input SVG or G-code file (use '-' for stdin)",
        'ARG_OUTPUT': "Output G-code file (use '-' for stdout)",
        'ARG_OPTIMIZE': "Apply movement optimization",
        'ARG_RESCALE': "Rescale factor for the G-code file",
        'ARG_SAVE_CONFIG': "Save current arguments as user config",
        'ARG_CONFIG': "Path to custom config file (JSON)",
        'ARG_TOOL': "Tool type: pen or marker",
        'ARG_DOUBLE_PASS': "Use double pass for pen contours",
        'ARG_NO_DOUBLE_PASS': "Disable double pass for contours",
        'ARG_DEV': "Enable developer mode (DEBUG logging, extended stacktrace)",
        'PROMPT_SELECT_SVG_FILE_RANGE': "Select an SVG file ({range}):",
        'PROMPT_USE_MAX_HEIGHT': "Use max config height ({max_height}mm)? [Y/n]:",
        'ERROR_FILE_NOT_FOUND': "File not found.",
        'WARN_NOT_IMPLEMENTED': "Feature not implemented yet.",
        'INFO_OPTIONS': "Options:",
        'INFO_DIRECT_EXECUTION': "Direct execution: using files specified by arguments.",
        'WARN_NO_FILES_FOUND': "No SVG or GCODE files available.",
        'INFO_TECHNICAL_LOGS_HEADER': "--- [TECHNICAL LOGS] ---",
        'OPTIMIZING_PATHS': "Optimizing paths...",
    },
    'zh': {
        'DEBUG_DEV_MODE_ON': "[DEV] 开发者模式已激活：DEBUG 日志和扩展堆栈跟踪",
        'MENU_MAIN_TITLE': "主菜单",
        'MENU_OPTION_CONVERT': "1. 转换 SVG 到 G代码",
        'MENU_OPTION_OPTIMIZE': "2. 优化现有 G代码文件",
        'PROMPT_SELECT_OPTION': "请输入选项编号：",
        'INFO_SVG_FILES_FOUND': "找到的 SVG 文件：",
        'OPTION_SVG_FILE': "[{num}] {filename}",
        'OPTION_CANCEL': "[0] 取消",
        'PROMPT_SELECT_SVG_FILE': "请选择 SVG 文件编号：",
        'INFO_SVG_SELECTED': "已选择 SVG 文件：{filename}",
        'INFO_GCODE_OUTPUT': "输出 G代码文件：{filename}",
        'INFO_PROCESSING_FILE': "正在处理文件... 可能需要几秒钟",
        'INFO_PROCESSING_DONE': "处理完成",
        'OPTION_TOOL_PEN': "[1] 钢笔 (仅轮廓)",
        'OPTION_TOOL_MARKER': "[2] 粗记号笔 (填充/轮廓)",
        'PROMPT_SELECT_TOOL': "请选择工具类型：",
        'OPTION_YES': "[S] 是",
        'OPTION_NO': "[N] 否",
        'PROMPT_DOUBLE_PASS': "轮廓是否进行双遍绘制? [S/n]:",
        'INFO_SVG_LOAD': "已加载 SVG: {filename}",
        'INFO_PATHS_EXTRACTED': "提取路径数: {count}",
        'INFO_PATHS_PROCESSED': "有效路径数: {count}",
        'DEBUG_PATHS_ORDER_ORIG': "原始路径顺序: {list}",
        'DEBUG_TOTAL_DIST_ORIG': "原始总距离: {dist} mm",
        'DEBUG_PATHS_ORDER_OPT': "优化后路径顺序: {list}",
        'DEBUG_TOTAL_DIST_OPT': "优化后总距离: {dist} mm",
        'DEBUG_BOUNDING_BOX': "边界框: xmin={xmin}, xmax={xmax}, ymin={ymin}, ymax={ymax}",
        'DEBUG_SCALE_APPLIED': "应用缩放: {scale}",
        'DEBUG_RELATIVE_MOVES': "相对移动已启用: {enabled}",
        'DEBUG_ARC_COMPRESS': "圆弧压缩率: {percent}%",
        'DEBUG_LINE_COMPRESS': "直线压缩率: {percent}%",
        'DEBUG_GCODE_LINES': "生成的 G代码行数: {count}",
        'DEBUG_OPTIMIZATION_METRICS': "优化指标: {metrics}",
        'INFO_GCODE_GENERATED': "已生成 G代码，共 {count} 行",
        'DEBUG_COMPRESSION_SUMMARY': "压缩率: 原始={orig}, 压缩后={comp}, 比率={ratio}%",
        'INFO_GCODE_WRITTEN': "G代码文件已保存: {filename}",
        'INFO_GCODE_SUCCESS': "✔ G代码生成成功: {filename}",
        'ERROR_INVALID_SELECTION': "✖ 无效选择，请选择有效选项",
        'ERROR_GENERIC': "✖ 发生意外错误",
        'WARN_INVALID_SELECTION': "⚠ 无效选择，请重试",
        'WARN_INVALID_NUMBER': "⚠ 请输入有效数字",
        'WARN_YES_NO': "⚠ 请回答 'S' (是) 或 'N' (否)",
        'INFO_EXIT': "\n程序退出，再见！",
        'INFO_EXIT_INTERRUPT': "\n因中断（Ctrl+C）退出程序。",
        'ERROR_NO_GCODE': "未选择 GCODE 文件。",
        'OPERATION_MENU_TITLE': "请选择操作：",
        'OPERATION_OPTIMIZE': "1. 优化 G-code 文件",
        'OPERATION_RESCALE': "2. 重缩放 G-code 文件",
        'EXIT': "0. 取消",
        'ENTER_NUMBER': "请输入选项编号",
        'INVALID_NUMBER': "请输入有效数字。",
        'OPERATION_CANCELLED': "操作已取消。",
        'SUCCESS_REFACTOR': "优化后的 G-code 文件已保存至：{output_file}",
        'SUCCESS_OPTIMIZE': "已做更改：{changes}",
        'RESCALE_USING_MAX': "使用最大配置高度重缩放：{height} 毫米",
        'HEIGHT_GT_ZERO': "高度必须大于零。",
        'SUCCESS_RESCALE': "重缩放后的 G-code 文件已保存至：{output_file}",
        'RESCALE_ORIGINAL': "原始尺寸：宽={width} 毫米，高={height} 毫米",
        'RESCALE_NEW': "新尺寸：宽={width} 毫米，高={height} 毫米",
        'RESCALE_FACTOR': "应用的缩放因子：{factor}",
        'RESCALE_CMDS': "已重缩放命令：G0/G1={g0g1}，G2/G3={g2g3}",
        'INFO_SVG_INPUT_UPDATED': "SVG_INPUT_DIR 已更新为：{new_dir}",
        'WARN_INVALID_DIR': "无效文件夹。",
        'INFO_PLACE_SVG_AND_RETRY': "请在文件夹中放入至少一个 SVG 文件，然后按回车重试。",
        'INFO_ASSIGN_NEW_DIR': "1) 设置新的输入文件夹",
        'INFO_RETRY': "2) 重试（请在当前文件夹放入 SVG 文件）",
        'WARN_NO_SVG_FOUND': "在 '{svg_input_dir}' 中未找到 SVG 文件。",
        'WARN_OUT_OF_RANGE': "选择超出范围。",
        'WARN_INVALID_OPTION': "无效选项。",
        'INFO_OPERATION_CANCELLED': "用户已取消操作。",
        'INFO_OPERATION_CANCELLED_CTRL_C': "\n用户通过 Ctrl+C 取消操作。",
        'INFO_GCODE_FILES_FOUND': "\n找到的 GCODE 文件：",
        'PROMPT_SELECT_GCODE_FILE': "请输入 GCODE 文件编号：",
        'WARN_NO_GCODE_FOUND': "在 {gcode_dir} 中未找到 GCODE 文件",
        'PROMPT_NEW_GCODE_DIR': "[输入] 请输入其他文件夹（或输入 'q' 取消）：",
        'ARGPARSE_DESCRIPTION': (
            "将 SVG 文件转换为绘图仪或简易 CNC 的 G代码路径\n\n"
            "使用示例:\n"
            "  python run.py --input 示例.svg --output 输出.gcode\n"
            "  python run.py --no-interactive -i 示例.svg -o - > 输出.gcode\n"
            "  cat 示例.svg | python run.py --no-interactive -i - -o 输出.gcode\n"
            "  python run.py --no-interactive --optimize -i 输入.gcode -o 优化后.gcode\n\n"
            "使用 -h 或 --help 查看所有选项"
        ),
        'ARG_NO_INTERACTIVE': "非交互模式运行",
        'ARG_NO_COLOR': "禁用彩色输出",
        'ARG_LANG': "界面语言 (es, en, zh)",
    }
}

def get_message(key, lang='es', **kwargs):
    """Obtiene el mensaje localizado y formatea con kwargs si aplica."""
    template = MESSAGES.get(lang, MESSAGES['es']).get(key, key)
    return template.format(**kwargs)