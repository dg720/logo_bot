from pptx import Presentation
from pptx.util import Inches
from PIL import Image
from src.reformat import remove_white_background, auto_crop
import os

output_file = "logos_presentation.pptx"


def configure_ppt_settings(logo_positions: tuple, slide_size: tuple):
    """
    Set up slide and logo layout parameters for PowerPoint generation.

    Args:
        logo_positions (tuple): (num_cols, num_rows) - Number of logos per row and column.
        slide_size (tuple): (width_in_inches, height_in_inches) - Slide dimensions.

    Returns:
        dict: A dictionary containing layout configuration values.
    """

    num_cols, num_rows = logo_positions
    user_width, user_height = slide_size
    slide_width, slide_height = Inches(user_width), Inches(user_height)

    # Derived Parameters
    logo_height = int(user_height * 96 / num_rows / 2)
    slide_pixel_width = user_width * 96
    max_logo_width = int(slide_pixel_width / num_cols)

    # Compute horizontal positions (centered columns)
    col_spacing = slide_width / (num_cols - 1)
    column_centers = []
    current_x = Inches(0.1)
    for _ in range(num_cols):
        column_center = current_x + col_spacing / 2
        column_centers.append(column_center)
        current_x += col_spacing

    # Compute vertical spacing
    row_spacing = slide_height / (num_rows - 1)

    return {
        "num_cols": num_cols,
        "num_rows": num_rows,
        "slide_width": slide_width,
        "slide_height": slide_height,
        "logo_height": logo_height,
        "max_logo_width": max_logo_width,
        "column_centers": column_centers,
        "row_spacing": row_spacing,
    }


def load_and_process_logos(
    folder,
    num_cols,
    num_rows,
    slide_width,
    slide_height,
    logo_height,
    max_logo_width,
    column_centers,
    row_spacing,
):
    """Load, clean, resize, and save logos."""
    logos = [
        f for f in os.listdir(folder) if f.lower().endswith((".png", ".jpg", ".jpeg"))
    ]
    processed_logos = []

    for logo in logos:
        logo_path = os.path.join(folder, logo)
        img = Image.open(logo_path)

        img = remove_white_background(img)
        img = auto_crop(img)

        aspect_ratio = img.width / img.height
        new_width = int(logo_height * aspect_ratio)
        new_height = logo_height

        if new_width > max_logo_width:
            new_width = max_logo_width
            new_height = int(new_width / aspect_ratio)

        img = img.resize((new_width, new_height))
        img.save(logo_path, format="PNG")

        processed_logos.append((logo_path, new_width, new_height))

    return processed_logos


def create_powerpoint(
    processed_logos,
    num_cols,
    num_rows,
    slide_width,
    slide_height,
    logo_height,
    max_logo_width,
    column_centers,
    row_spacing,
):
    """Create PowerPoint presentation with logos arranged in a grid."""
    prs = Presentation()
    slide = prs.slides.add_slide(prs.slide_layouts[5])  # Blank slide

    for idx, (logo_path, width_px, height_px) in enumerate(processed_logos):
        col = idx % num_cols
        row = idx // num_cols
        if row >= num_rows:
            break

        width_in = Inches(width_px / 96)
        height_in = Inches(height_px / 96)

        x = column_centers[col] - (width_in / 2)
        y = (row + 1) * row_spacing - height_in / 2

        slide.shapes.add_picture(logo_path, x, y, width=width_in, height=height_in)

    prs.save(output_file)
    return
