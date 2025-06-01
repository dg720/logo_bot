# logo_bot

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://dg720-logo-bot-main-xvjsh8.streamlit.app/)
![Python Version](https://img.shields.io/badge/python-3.9+-blue)
![Last Commit](https://img.shields.io/github/last-commit/dg720/logo_bot)

! I'm Dhruv (@dg720) and this is **logo_bot**, a Streamlit-based web app that automatically finds and formats company logos into a downloadable PowerPoint file.

Whether you're building a client deck, showcasing a portfolio, or putting together a partnership slide, this tool saves you the tedious work of Googling logos, resizing them, and formatting them into PowerPoint.

Try it live: [logo_bot Streamlit App](https://dg720-logo-bot-main-xvjsh8.streamlit.app/)

---

## Overview

- **Search**: Input a list of company names manually or paste in bulk.
- **Source**: The app fetches the most relevant logos using a hybrid of Brandfetch and fallback scraping.
- **Preview**: View the logos in a clean, scrollable grid with quick quality checks.
- **Download**: Export the result as a PowerPoint file with logos neatly arranged in a grid and scaled to fit.
- **Clear/Restore**: Manage your session's logo cache with reset and recovery options.

---

## How to Use

1. Open the app at the link above.
2. Enter company names—either type them or paste a list (one per line).
3. Click **Run** to fetch and preview logos.
4. Configure layout options like slide dimensions and grid format.
5. Click **Export to PowerPoint** to download the presentation.

You can also use the **Clear Logos** button to reset the session and start fresh.

---

## Technical Overview

The app is structured with a modular backend and a Streamlit-based UI.

### Core Components

- `src/logos.py`:  
  Fetches logos via Brandfetch and fallback scraping. Saves logos in a standardized format (`.png`, `.webp`).

- `src/output.py`:  
  Uses `python-pptx` to:
  - Arrange logos into a grid layout
  - Scale logos based on slide and cell dimensions
  - Format the final presentation

- `app.py`:  
  Orchestrates the UI using Streamlit. Manages user input, display logic, and session state.

### Storage & Caching

- `logo_cache/`: Temporary session-specific logo storage.
- `logo_backup/`: Persistent storage for recovered or previously used logos.

### Image Processing

- Optional whitespace trimming and auto-cropping using Pillow
- Aspect-ratio preservation for clean logo scaling

---

## Module Structure

    logo_bot/
    ├── app.py                   # Streamlit frontend
    ├── requirements.txt
    ├── logo_cache/              # Session logo storage
    ├── logo_backup/             # Persistent fallback logo storage
    └── src/
        ├── logos.py             # Logo sourcing (Brandfetch + fallback scraping)
        ├── output.py            # PowerPoint layout and export logic
        └── reformat.py          # Logo cleanup (autocrop, background removal)

---

## Roadmap

Planned features:

- Manual logo override via drag-and-drop
- Advanced search filters (e.g., SVG only, transparent backgrounds)
- AI-based logo quality detection and replacement
- Support for multiple API fallback sources
- Branded PowerPoint template options
- CSV-based batch processing for enterprise users

