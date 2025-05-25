from pptx import Presentation
from pptx.util import Inches
from PIL import Image
from src.reformat import remove_white_background, auto_crop
import os

# ------------------ Configuration ------------------

LOGO_FOLDER = "C:/Users/dhruv/Documents/logo_bot/src/logo_backup"
OUTPUT_FILE = "logos_presentation.pptx"
LOGO_POSITIONS = (5, 10)  # (columns, rows)
USER_WIDTH, USER_HEIGHT = (4, 9)  # in inches
SLIDE_WIDTH, SLIDE_HEIGHT = Inches(USER_WIDTH), Inches(USER_HEIGHT)

# ------------------ Derived Parameters ------------------

num_cols, num_rows = LOGO_POSITIONS
LOGO_HEIGHT = int(USER_HEIGHT * 96 / num_rows / 2)
slide_pixel_width = USER_WIDTH * 96
MAX_WIDTH = int(slide_pixel_width / num_cols)

# Compute horizontal positions
col_spacing = SLIDE_WIDTH / (num_cols - 1)
column_centers = []
current_x = Inches(0.1)
for _ in range(num_cols):
    column_center = current_x + col_spacing / 2
    column_centers.append(column_center)
    current_x += col_spacing

# Compute vertical spacing
row_spacing = SLIDE_HEIGHT / (num_rows - 1)


def load_and_process_logos(folder):
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
        new_width = int(LOGO_HEIGHT * aspect_ratio)
        new_height = LOGO_HEIGHT

        if new_width > MAX_WIDTH:
            new_width = MAX_WIDTH
            new_height = int(new_width / aspect_ratio)

        img = img.resize((new_width, new_height))
        img.save(logo_path, format="PNG")

        processed_logos.append((logo_path, new_width, new_height))

    return processed_logos


def create_powerpoint(processed_logos):
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

    prs.save(OUTPUT_FILE)
    print(f"PowerPoint saved as {OUTPUT_FILE}")
