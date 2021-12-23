"""Creates a Spotify cover"""
import glob
import random
from PIL import Image
from utils import centered_resize, zoom_in, pick_large_img_locs


# TODO: 
# - Add 2x2 and 3x3 cell images
#       - Total number of possible nxn cell images: (NUM_COLS // n) * (NUM_ROWS // n)
#       - Range of valid start columns for nxn cell images: 0 to NUM_COLS-n
# - Add optional text


# Settings
IN_FOLDER = "../images"
OUT_FOLDER = ".."
FILE_FORMATS = ["jpg", "png"]
BG_COLOR = "#2f3030"
NUM_COLS = 5
NUM_ROWS = 5
GAP_SIZE = 20
OUT_HEIGHT = 2048
OUT_WIDTH = 2048
IMAGE_TILT = 20
CELL_WIDTH = (OUT_WIDTH - GAP_SIZE * (NUM_COLS - 1)) // NUM_COLS
CELL_HEIGHT = (OUT_HEIGHT - GAP_SIZE * (NUM_ROWS - 1)) // NUM_ROWS
NUM_LARGE_IMGS = 2
LARGE_IMG_WIDTH = CELL_WIDTH * 2 + GAP_SIZE
LARGE_IMG_HEIGHT = CELL_HEIGHT * 2 + GAP_SIZE
NUM_IMGS = NUM_COLS * NUM_ROWS + NUM_LARGE_IMGS


# Magic stuff. Basically, search for files with the given extensions and put them in a list.
all_files = [file for format in FILE_FORMATS for file in glob.glob(f"{IN_FOLDER}/*.{format}")] * 4
album_files = random.sample(all_files, NUM_IMGS)
album_imgs = [Image.open(file) for file in album_files]

# Paste small album covers into a grid, iteratively
playlist_cover = Image.new('RGB', (OUT_WIDTH, OUT_HEIGHT), color=BG_COLOR)
i = 0
for xcursor in range(0, OUT_WIDTH, GAP_SIZE + CELL_WIDTH):
    for ycursor in range(0, OUT_HEIGHT, GAP_SIZE + CELL_HEIGHT):
        img = album_imgs[i]
        img = centered_resize(img, (CELL_WIDTH, CELL_HEIGHT))
        playlist_cover.paste(img, box=(xcursor, ycursor))
        i += 1

# Paste large album covers, iteratively
large_img_locs = pick_large_img_locs(NUM_COLS, NUM_ROWS, NUM_LARGE_IMGS)
for col_index, row_index in large_img_locs:
    img = album_imgs[i]
    img = centered_resize(img, (LARGE_IMG_WIDTH, LARGE_IMG_HEIGHT))
    xcursor = col_index * (GAP_SIZE + CELL_WIDTH)
    ycursor = row_index * (GAP_SIZE + CELL_WIDTH)
    playlist_cover.paste(img, box=(xcursor, ycursor))
    i += 1

# Post-processing on the album grid
playlist_cover = playlist_cover.rotate(IMAGE_TILT, fillcolor=BG_COLOR)
playlist_cover = zoom_in(playlist_cover, 1.2)

# Save the final Spotify album cover.
playlist_cover.save(f"{OUT_FOLDER}/sample-cover.jpg")