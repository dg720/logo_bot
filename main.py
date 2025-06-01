import streamlit as st
import pandas as pd
from src.chatbot import get_company_list_from_prompt
from src.logos import pull_logos
from src.output import (
    load_and_process_logos,
    create_powerpoint,
    configure_ppt_settings,
    clear_folder,
)
import os
import uuid

# ---------------- Configuration ----------------
cache_path = "logo_cache"
backup_path = "logo_backup"

# Generate unique ID for this user session
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# Create session-specific logo cache folder
session_cache_path = os.path.join("logo_cache", st.session_state.session_id)
os.makedirs(session_cache_path, exist_ok=True)


# ---------------- Utilities ----------------
def preview_images(folder):
    logo_files = [
        f
        for f in os.listdir(folder)
        if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))
    ]
    logo_files.sort()
    cols_per_row = 5
    rows = [
        logo_files[i : i + cols_per_row]
        for i in range(0, len(logo_files), cols_per_row)
    ]

    for row in rows:
        cols = st.columns(cols_per_row)
        for idx, logo_file in enumerate(row):
            with cols[idx]:
                st.image(
                    os.path.join(folder, logo_file),
                    use_container_width=True,
                    caption=logo_file.split(".")[0].title(),
                )


# ---------------- App Title ----------------
st.markdown("<h1 style='color:#4A90E2;'>🤖 LogoBot</h1>", unsafe_allow_html=True)
st.markdown(
    "<p style='font-size:16px;'>Automatically source, format, and arrange company logos into a downloadable PowerPoint grid. It is recommended to delete all saved logos upon starting the app </p>",
    unsafe_allow_html=True,
)
st.divider()

# ---------------- Step 1 ----------------
st.markdown(
    "<h3 style='color:#1f77b4;'>🏁 Step 1: Source Logos</h3>", unsafe_allow_html=True
)

# Initialize session state if not already
if "manual_input" not in st.session_state:
    st.session_state.manual_input = ""

# --- Option B: AI-based generation ---
st.markdown("**Option A: Generate companies using ChatGPT**")
ai_prompt = st.text_input(
    "💬 Describe the type of companies (e.g., 'Top automotive OEMs')",
    key="ai_prompt",
)

if st.button("🤖 Generate with ChatGPT"):
    if ai_prompt.strip():
        with st.spinner("Contacting ChatGPT..."):
            df_generated = get_company_list_from_prompt(ai_prompt.strip())
        if not df_generated.empty:
            generated_text = "\n".join(df_generated["Company"])
            st.session_state.manual_input = generated_text
            st.rerun()
        else:
            st.error("❌ No companies returned. Try a different prompt.")
    else:
        st.warning("⚠️ Please enter a description.")

# --- Option A: Manual entry (auto-filled from AI if used) ---
st.markdown("**Option B: Enter company names manually**")
company_input = st.text_area(
    "✍️ One company per line",
    height=200,
    value=st.session_state.manual_input,
    key="manual_text_input",
)

# Update session state with current text box content
st.session_state.manual_input = company_input

st.divider()

# Run and clear buttons
c1, c2 = st.columns(2)

with c1:
    if st.button("🚀 Run"):
        if st.session_state.manual_input.strip():
            company_list = [
                name.strip()
                for name in st.session_state.manual_input.strip().split("\n")
                if name.strip()
            ]
            df = pd.DataFrame(company_list, columns=["Company"])
            clear_folder(session_cache_path)
            pull_logos(df, backup_path, session_cache_path)
            st.success("✅ Logos downloaded successfully!")
        else:
            st.warning("⚠️ Please enter at least one company name.")

with c2:
    if st.button("🗑️ Delete all saved logos"):
        clear_folder(session_cache_path)
        st.success("🧹 Logo folder cleared.")

st.markdown("###### 👁️ Preview saved logos:")
if st.button("Preview logos"):
    preview_images(session_cache_path)

st.divider()

# ---------------- Step 2 ----------------
st.markdown(
    "<h3 style='color:#2ca02c;'>🖼️ Step 2: Generate PPT</h3>", unsafe_allow_html=True
)

st.info("💡 Tip: Make sure slide dimensions match your logo layout.")

col1, col2 = st.columns(2)
rows = col1.number_input("🔢 Rows", min_value=1, value=5, step=1)
columns = col1.number_input("🔢 Columns", min_value=1, value=5, step=1)
height = col2.number_input("📏 Height (inches)", min_value=0.5, value=5.0)
width = col2.number_input("📐 Width (inches)", min_value=0.5, value=5.0, step=1.0)

if st.button("📸 Generate PPT"):
    params = configure_ppt_settings((columns, rows), (width, height))
    processed = load_and_process_logos(session_cache_path, **params)
    create_powerpoint(processed, **params)
    st.success("🎉 PowerPoint created successfully!")

st.divider()

# ---------------- Step 3 ----------------
st.markdown(
    "<h3 style='color:#e67e22;'>📥 Step 3: Download PPT</h3>", unsafe_allow_html=True
)

file_name = "logos_presentation.pptx"
if os.path.exists(file_name):
    with open(file_name, "rb") as f:
        st.download_button(
            label="⬇️ Download PowerPoint",
            data=f,
            file_name="logo_array.pptx",
            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        )
else:
    st.warning("⚠️ Generate the presentation before downloading.")
