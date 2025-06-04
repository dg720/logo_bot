# Threshold above which a pixel is considered "white"
WHITE_THRESHOLD = 230


def remove_white_background(image):
    """
    Removes near-white backgrounds by making those pixels fully transparent.

    Args:
        image (PIL.Image): An input image in any mode (converted to RGBA).

    Returns:
        PIL.Image: The image with white or near-white pixels made transparent.
    """
    image = image.convert("RGBA")  # Convert image to include alpha channel
    data = image.getdata()  # Get pixel data as a list of RGBA tuples

    new_data = []
    for item in data:
        # Identify pixels that are close to white across all RGB channels
        if (
            item[0] > WHITE_THRESHOLD
            and item[1] > WHITE_THRESHOLD
            and item[2] > WHITE_THRESHOLD
        ):
            new_data.append((255, 255, 255, 0))  # Set to transparent
        else:
            new_data.append(item)  # Retain original pixel

    image.putdata(new_data)  # Update image with new pixel data
    return image


def auto_crop(image):
    """
    Automatically crops the image by removing transparent borders.

    Args:
        image (PIL.Image): An image, typically with transparent areas.

    Returns:
        PIL.Image: Cropped image, or the original if no cropping is needed.
    """
    bbox = image.getbbox()  # Get bounding box of non-transparent area
    if bbox:
        return image.crop(bbox)  # Crop to bounding box if found
    return image  # Return original if no non-transparent content found
