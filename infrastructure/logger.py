"""
Logger setup for the application.
"""
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(levelname)-5s- %(filename)s:%(lineno)s] %(message)s'
)
logger = logging.getLogger("svg2gcode")
