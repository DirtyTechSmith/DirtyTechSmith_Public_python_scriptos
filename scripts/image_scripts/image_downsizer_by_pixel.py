"""
Resize an image to a maximum dimension of matching the MAX_DIMENSION variable.
"""
from pathlib import Path

import PIL
from PIL import Image

from lazy_log import logger

file_path = Path('C:\\image_file_path.jpg')
small_file_path = Path('C:\\small_image_file_path.jpg')

MAX_DIMENSION = 700

the_image = PIL.Image.open(file_path.as_posix())
width, height = the_image.size
sizing_dimension = width
if height > width:
    sizing_dimension = height

reduction = MAX_DIMENSION / sizing_dimension
width = int(width * reduction)
height = int(height * reduction)
logger.info(f'multiplier: {reduction}')
logger.info(f'width:  {width},  height : {height}')

small_image = the_image.resize((width, height))
small_image.save(small_file_path.as_posix())
