"""
Logger setup for the application.
"""
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(levelname)s] %(message)s'
)
logger = logging.getLogger("svg2gcode")
