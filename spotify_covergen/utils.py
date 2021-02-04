from PIL import Image

def centered_resize(image: Image, size: (int, int)) -> Image:
    """
    Resizes an image, cropping and centering it doesn't match the target resolution. 
    Like CSS's `background-fill: cover`
    """
    width, height = size
    old_aspect_ratio = image.width / image.height
    new_aspect_ratio = width / height

    if new_aspect_ratio != old_aspect_ratio:
        # Crop horizontally
        if old_aspect_ratio > new_aspect_ratio:
            crop_left = (image.width - image.height) // 2
            crop_right = crop_left + image.height
            image = image.crop((crop_left, 0, crop_right, image.height))

        # Crop vertically
        else:
            crop_top = (image.height - image.width) // 2
            crop_bot = crop_top + image.height
            image = image.crop((0, crop_top, image.width, crop_bot))

    return image.resize(size)

def zoom_in(image: Image, zoom_level: float) -> Image:
    """Zooms in on an image by a given amount (1.0 = don't zoom in, 2.0 = 2x zoom)"""  
    old_width = image.width
    old_height = image.height
    left = (image.width * (zoom_level - 1)) // 2
    right = image.width - left
    top = (image.height * (zoom_level - 1)) // 2
    bottom = image.height - top

    cropped = image.crop((left, top, right, bottom))

    return cropped.resize((old_width, old_height))

def pick_large_img_locs(num_cols: int, num_rows: int, num_large_imgs: int):
    """A generator for (x, y) tuples indicating where large 2x2 images should be placed in an image"""
    yield (1, 2)
    yield (3, 3)