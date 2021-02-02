"""Creates a Spotify cover"""
import glob
import random
import numpy as np
from PIL import Image
from pathlib import Path
from utils import squared, zoom_in

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
            # width = WIDTH_PER_COL
            # height = int(img.height * (width / img.width))  # TODO: Check if this accounts for Born to Run
            # img = img.resize((width, height))
            img = squared(img)  # Crops the images into a square.
            img = img.resize((WIDTH_PER_COL, WIDTH_PER_COL))  # Resize the square image into the desired dimensions.
            album_imgs.append(img)

            # Save Image
            # outfile = f"../processed-images/{file_path.name}"
            # im.save(outfile)
    except OSError as e:
        print(e)

# Arrange album covers into a grid
# width = sum(img.width for img in album_imgs) // 3
# height = sum(img.height for img in album_imgs)

# Create the image that the covers will be pasted into.
playlist_cover = Image.new('RGB', (OUT_WIDTH, OUT_HEIGHT), color=BG_COLOR)

# Add images to a column in the Spotify album cover until it is full. Then, progress to the next column. Repeat.
xcursor = 0
ycursor = 0
for i, img in enumerate(album_imgs):
    if i > 0 and i % ROW_COUNT == 0:  # The end of a colum.
        xcursor += XGAP + WIDTH_PER_COL
        ycursor = 0

    # centered_x = xcursor + (WIDTH_PER_COL - img.width) // 2  # Center the image within its column.
    playlist_cover.paste(img, box=(xcursor, ycursor))
    ycursor += img.height + YGAP
# Rotate the Spotify album cover.
playlist_cover = playlist_cover.rotate(IMAGE_TILT, fillcolor=BG_COLOR)
playlist_cover = zoom_in(playlist_cover, 1.2)
# Save the final Spotify album cover.
outfile = f"{OUT_FOLDER}/test.jpg"
playlist_cover.save(outfile)

ims = np.array([np.array(im.convert("L")) for im in album_imgs])
imave = np.average(ims,axis=0)
result = Image.fromarray(imave.astype("uint8"))
result.save(f"{OUT_FOLDER}/avg.jpg")