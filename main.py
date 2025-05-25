import streamlit as st
import pandas as pd
from src.logos import pull_logos
from src.output import load_and_process_logos, create_powerpoint, configure_ppt_settings
import os

logo_path = "logo_backup"


def preview_images():
    logo_files = [
        f
        for f in os.listdir(logo_path)
        if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))
    ]

    # Sort alphabetically for consistency
    logo_files.sort()

    # Choose number of columns
    cols_per_row = 5
    rows = [
        logo_files[i : i + cols_per_row]
        for i in range(0, len(logo_files), cols_per_row)
    ]
    # Display grid
    for row in rows:
        cols = st.columns(cols_per_row)
        for idx, logo_file in enumerate(row):
            with cols[idx]:
                st.image(
                    os.path.join(logo_path, logo_file),
                    use_container_width=True,
                    caption=logo_file.split(".")[0].title(),
                )


st.title("LogoBot")
st.markdown("Upload your data and get predictions.")

st.write("### Step 1: Source Logos")

company_input = st.text_area(
    "Company Names", height=200, placeholder="e.g. Apple\nGoogle\nAmazon"
)

if st.button("Download Logos"):
    if company_input.strip():
        # Clean and split the input into a list
        company_list = [
            name.strip() for name in company_input.strip().split("\n") if name.strip()
        ]
        df = pd.DataFrame(company_list, columns=["Company"])
        st.success(f"Created a DataFrame with {len(df)} companies.")
        st.dataframe(df)
        pull_logos(df)
        preview_images()

    else:
        st.warning("Please enter at least one company name.")

st.write("### Step 2: Generate PPT")

col1, col2 = st.columns(2)
rows = col1.number_input("Rows", min_value=1, value=5, step=1)
columns = col1.number_input("Columns", min_value=1, value=5, step=1)
height = col2.number_input("Height", min_value=0.5, value=5.0)
width = col2.number_input("Width", min_value=0.5, value=5.0, step=1.0)

if st.button("Generate PPT"):
    params = configure_ppt_settings((columns, rows), (width, height))
    processed = load_and_process_logos(logo_path, **params)
    create_powerpoint(processed, **params)
    st.success("PPT output")

st.write("### Step 3: Download PPT")

file_name = "logos_presentation.pptx"
with open(file_name, "rb") as f:
    st.download_button(
        label="Download PPT",
        data=f,
        file_name="logo_array.pptx",
        mime="application/pptx",
    )
