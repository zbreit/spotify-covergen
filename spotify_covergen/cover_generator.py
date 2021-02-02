"""Creates a Spotify cover"""
import glob
import random
import numpy as np
from PIL import Image
from pathlib import Path
from utils import squared, zoom_in


# TODO: 
# - Add 2x2 and 3x3 cell images
# - Add optional text


# Settings
IN_FOLDER = "../images"
OUT_FOLDER = "../processed-images"
FILE_FORMATS = ["jpg", "png"]
BG_COLOR = "#2f3030"
COL_COUNT = 5
ROW_COUNT = 5
XGAP = 20
YGAP = XGAP
OUT_HEIGHT = 900
OUT_WIDTH = 900
IMAGE_TILT = 20
WIDTH_PER_COL = (OUT_WIDTH - XGAP * (COL_COUNT - 1)) // COL_COUNT
HEIGHT_PER_COL = OUT_HEIGHT // ROW_COUNT

# Magic stuff. Basically, search for files with the given extensions and put them in a list.
all_files = [Path(file) for format in FILE_FORMATS for file in glob.glob(f"{IN_FOLDER}/*.{format}")] * 4
album_files = random.sample(all_files, COL_COUNT * ROW_COUNT)
album_count = len(album_files)

# Open and put all album cover images into a list.
album_imgs = []
for file_path in album_files:
    try:
        with Image.open(file_path) as img:
            img = squared(img)  # Crops the images into a square.
            img = img.resize((WIDTH_PER_COL, WIDTH_PER_COL))  # Resize the square image into the desired dimensions.
            album_imgs.append(img)
    except OSError as e:
        print(e)

# Create a grid of album covers, pasting images into the final cover iteratively
playlist_cover = Image.new('RGB', (OUT_WIDTH, OUT_HEIGHT), color=BG_COLOR)
xcursor = 0
ycursor = 0
for i, img in enumerate(album_imgs):
    if i > 0 and i % ROW_COUNT == 0:  # The end of a colum.
        xcursor += XGAP + WIDTH_PER_COL
        ycursor = 0
    playlist_cover.paste(img, box=(xcursor, ycursor))
    ycursor += img.height + YGAP

# Post-processing on the album grid
playlist_cover = playlist_cover.rotate(IMAGE_TILT, fillcolor=BG_COLOR)
playlist_cover = zoom_in(playlist_cover, 1.2)

# Save the final Spotify album cover.
playlist_cover.save(f"{OUT_FOLDER}/test.jpg")