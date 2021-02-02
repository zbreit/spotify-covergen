from PIL import Image

def squared(image: Image) -> Image:
    """Creates a cropped image that is square, without squishing the image"""
    if image.width > image.height:
        crop_left = (image.width - image.height) // 2
        crop_right = crop_left + image.height
        result = image.crop((crop_left, 0, crop_right, image.height))
    else:
        crop_top = (image.height - image.width) // 2
        crop_bot = crop_top + image.height
        result = image.crop((0, crop_top, image.width, crop_bot))

    return result

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
