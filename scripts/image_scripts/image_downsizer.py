# Purpose: reduce the size of an image to a target size
# used to get images under 100kb for a website(passport photos)

import os
from pathlib import Path

import PIL
from PIL import Image

from lazy_log import logger

file_path = Path('C:\\image_file_path.jpg')
small_file_path = Path('C:\\small_image_file_path.jpg')

TARGET_SIZE = 100  # kb
MULTIPLIER = .999 # The amount to reduce the image size by in each iteration
STEP_SIZE = .001  # The decrement value for the MULTIPLIER in each iteration

current_size_on_disk = os.path.getsize(file_path.as_posix()) / 1000.0
reduction = TARGET_SIZE / current_size_on_disk
logger.info(f'size:{current_size_on_disk}')
logger.info(f'reduction: {reduction}')
while current_size_on_disk > TARGET_SIZE:
    the_image = PIL.Image.open(file_path.as_posix())
    width, height = the_image.size
    width = int(width * MULTIPLIER)
    height = int(height * MULTIPLIER)
    logger.info(f'multiplier: {MULTIPLIER}')
    logger.info(f'width:  {width},  height : {height}')

    small_image = the_image.resize((width, height))
    small_image.save(small_file_path.as_posix())
    # reduce the multiplier by the step size, this way we downsize from the original image to avoid artifacts
    MULTIPLIER -= STEP_SIZE
    current_size_on_disk = small_file_path.stat().st_size / 1000.0
    logger.info(f'size:{current_size_on_disk}')
