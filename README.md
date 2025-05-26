# 🖼️ logo_bot

Hi! I'm Dhruv (@dg720) and this is **logo_bot**, a Streamlit-based web app that automatically finds and formats company logos into a downloadable PowerPoint file.

Whether you're building a client deck, showcasing a portfolio, or putting together a partnership slide, this tool saves you the tedious work of Googling logos, resizing them, and formatting them into PowerPoint.

👉 Try it live here: [logo_bot Streamlit App](https://dg720-logo-bot-main-xvjsh8.streamlit.app/)

---

## 🔧 What it does

- **Search**: Input a list of company names manually or paste in bulk.
- **Source**: The app fetches the most relevant logos using a hybrid of Brandfetch and fallback scraping.
- **Preview**: View the logos in a clean, scrollable grid with quick quality checks.
- **Download**: Export the result as a PowerPoint file with the logos neatly laid out in a grid, auto-scaled to fit your slide format.
- **Clear/Restore**: Manage your session's logo cache with one-click buttons to clear or reload.

---

## ⚙️ How to use it

1. **Open the app** at the link above.
2. **Enter company names** – either type them one-by-one or paste a full list (one per line).
3. Click **Run** to fetch and preview the logos.
4. Adjust layout options like **slide dimensions** and **logo grid (columns x rows)**.
5. Click **Export to PowerPoint** to download a fully formatted `.pptx` file.

Optional: use the **Clear Logos** button to reset the session or try a new list.

---

## 🧠 Technical Overview

The app is structured with a modular backend and an interactive Streamlit front-end.

### 📁 Core Components

- `src/logos.py`:  
  Handles company name input, sources logos via the Brandfetch API and fallback scraping, and saves them in a standardized format (`.png` or `.webp`).

- `src/output.py`:  
  Formats the downloaded logos into a PowerPoint file using `python-pptx`. Handles:
  - Dynamic grid layout
  - Logo height/width scaling
  - Custom slide sizing and spacing
  - Centered alignment for aesthetic consistency

- `app.py`:  
  The Streamlit front-end. Captures user input, previews images, and controls layout/output settings using `st.session_state`.

### 📦 Storage & Caching

- **`logo_cache/`**: Temporarily stores the logos retrieved during a session.
- **`logo_backup/`**: Acts as a persistent fallback if the logo fetch fails in future runs.

### 🧼 Image Processing

Before inserting into the presentation:
- Logos are optionally auto-cropped and whitespace removed using `Pillow`
- Image dimensions are adjusted to maintain aspect ratio within a cell

---

## 🗂️ Module Structure

![Module Structure](docs/module_structure.png)

*Place this image in a `docs/` folder and name it `module_structure.png`.*

---

## 🛣️ Roadmap / Features to Develop

Planned enhancements include:

- 🔍 **Manual logo overrides** – allow users to upload or drag-drop their own logo if the automatic one isn’t right  
- 🎯 **Advanced search controls** – refine logo results with filters (e.g. SVG only, transparent background preferred)  
- 🧠 **AI logo validation** – flag or replace logos that are blurry, outdated, or incorrectly matched  
- 🌐 **Multi-source fallback** – integrate more robust APIs (e.g. Clearbit, Bing Image Search) to reduce miss rates  
- 🧩 **PowerPoint themes** – allow users to choose from predefined or custom branded slide templates  
- 📦 **Batch processing** – support uploading a CSV of companies + metadata and auto-generate multiple slides  

Feel free to suggest features or contribute your own!

---

## 📫 Contact & Contributions

If you find this useful, feel free to ⭐️ the repo or reach out with feedback.  
You can also fork and improve it — PRs are welcome!

— Dhruv (@dg720)
