WHITE_THRESHOLD = 230


def remove_white_background(image):
    """Converts white background pixels to transparent."""
    image = image.convert("RGBA")  # Ensure image is in RGBA mode
    data = image.getdata()

    new_data = []
    for item in data:
        # Check if pixel is close to white
        if (
            item[0] > WHITE_THRESHOLD
            and item[1] > WHITE_THRESHOLD
            and item[2] > WHITE_THRESHOLD
        ):
            new_data.append((255, 255, 255, 0))  # Make transparent
        else:
            new_data.append(item)  # Keep original pixel

    image.putdata(new_data)
    return image


def auto_crop(image):
    """Auto-crops an image by removing fully transparent borders."""
    bbox = image.getbbox()
    if bbox:
        return image.crop(bbox)
    return image  # If no cropping needed, return original image
