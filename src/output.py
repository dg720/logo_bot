from pptx import Presentation
from pptx.util import Inches
from PIL import Image
from reformat import remove_white_background, auto_crop
import os

# ------------------ Configuration ------------------

LOGO_FOLDER = (
    "C:/Users/dhruv/Documents/logo_bot/src/logos_temp"  # Folder containing input logos
)
OUTPUT_FILE = "logos_presentation.pptx"  # Output PowerPoint file name
LOGO_POSITIONS = (5, 10)  # (columns, rows) in grid layout
USER_WIDTH, USER_HEIGHT = (4, 9)  # Slide dimensions in inches
SLIDE_WIDTH, SLIDE_HEIGHT = Inches(USER_WIDTH), Inches(USER_HEIGHT)
HORIZONTAL_PADDING = Inches(
    2
)  # Optional horizontal padding between columns (currently unused)

# ------------------ Derived Parameters ------------------

num_cols, num_rows = LOGO_POSITIONS
LOGO_HEIGHT = int(
    USER_HEIGHT * 96 / num_rows / 2
)  # Logo height in pixels (assuming 96 DPI)
slide_pixel_width = USER_WIDTH * 96  # Slide width in pixels
MAX_WIDTH = int(slide_pixel_width / num_cols)  # Max allowed logo width per column

# ------------------ Load and Process Logos ------------------

# Filter valid image files
logos = [
    f for f in os.listdir(LOGO_FOLDER) if f.lower().endswith((".png", ".jpg", ".jpeg"))
]
processed_logos = []

for logo in logos:
    logo_path = os.path.join(LOGO_FOLDER, logo)
    img = Image.open(logo_path)

    # Step 1: Remove white background
    img = remove_white_background(img)

    # Step 2: Auto-crop transparent borders
    img = auto_crop(img)

    # Step 3: Resize image while maintaining aspect ratio
    aspect_ratio = img.width / img.height
    new_width = int(LOGO_HEIGHT * aspect_ratio)
    new_height = LOGO_HEIGHT

    if new_width > MAX_WIDTH:
        new_width = MAX_WIDTH
        new_height = int(new_width / aspect_ratio)

    img = img.resize((new_width, new_height))
    img.save(logo_path, format="PNG")  # Overwrite image in PNG format for transparency

    processed_logos.append((logo_path, new_width, new_height))

# ------------------ Compute Column Centers ------------------

# Determine horizontal center position for each column
col_spacing = SLIDE_WIDTH / (num_cols - 1)  # Space between column centers
column_centers = []

current_x = Inches(0.1)  # Start slightly away from the left edge
for _ in range(num_cols):
    column_center = current_x + col_spacing / 2
    column_centers.append(column_center)
    current_x += col_spacing

# ------------------ Create PowerPoint Presentation ------------------

prs = Presentation()
slide = prs.slides.add_slide(prs.slide_layouts[5])  # Blank layout

# ------------------ Compute Row Spacing ------------------

row_spacing = SLIDE_HEIGHT / (num_rows - 1)  # Vertical spacing between rows

# ------------------ Place Logos in Grid ------------------

for idx, (logo_path, width_px, height_px) in enumerate(processed_logos):
    col = idx % num_cols
    row = idx // num_cols

    if row >= num_rows:
        break  # Don't place logos outside the grid

    # Convert size from pixels to inches (assuming 96 DPI)
    width_in = Inches(width_px / 96)
    height_in = Inches(height_px / 96)

    # Center horizontally within the column
    x = column_centers[col] - (width_in / 2)

    # Vertically center within the row
    y = (row + 1) * row_spacing - height_in / 2

    # Insert image onto slide
    slide.shapes.add_picture(logo_path, x, y, width=width_in, height=height_in)

# ------------------ Save Presentation ------------------

prs.save(OUTPUT_FILE)
print(f"PowerPoint saved as {OUTPUT_FILE}")
