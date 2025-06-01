import os
import requests
import streamlit as st
import random
import shutil
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from googlesearch import search
import retrying


# --- Utilities ---


def get_company_website(company_name):
    query = f"{company_name} official site"
    for result in search(query):
        if "wikipedia" not in result.lower() and "linkedin" not in result.lower():
            return result
    return None


def extract_domain(url):
    try:
        parsed_url = urlparse(url)
        return parsed_url.netloc.replace("www.", "")
    except Exception:
        return None


@retrying.retry(stop_max_attempt_number=5, wait_fixed=2000)
def download_logo(company_url, company_name, backup_path, session_cache_path):
    api_key = st.secrets["BRANDFETCH_API_KEY"]
    logo_url = f"https://cdn.brandfetch.io/{company_url}/w/512/h/94/logo?c={api_key}"

    headers = {
        "User-Agent": random.choice(
            [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X)",
                "Mozilla/5.0 (X11; Linux x86_64)",
            ]
        ),
        "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
        "Referer": "https://brandfetch.io/",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
    }

    response = requests.get(logo_url, headers=headers, stream=True)

    if response.status_code == 200 and "image" in response.headers.get(
        "Content-Type", ""
    ):
        extension = response.headers["Content-Type"].split("/")[-1]
        if extension == "webp":
            extension = "png"

        file_name = f"{company_name}.{extension}"
        file_path = os.path.join(backup_path, file_name)
        cache_path = os.path.join(session_cache_path, file_name)

        content = response.content
        with open(file_path, "wb") as f:
            f.write(content)
        with open(cache_path, "wb") as f:
            f.write(content)
    else:
        raise Exception("Logo download failed")


def process_single_logo(company, backup_path, session_cache_path):
    try:
        backup_file = next(
            (f for f in os.listdir(backup_path) if f.startswith(company)), None
        )

        if backup_file:
            source = os.path.join(backup_path, backup_file)
            destination = os.path.join(session_cache_path, backup_file)
            if not os.path.exists(destination):
                shutil.copy2(source, destination)
            return

        website = get_company_website(company)
        if website:
            domain = extract_domain(website)
            if domain:
                download_logo(domain, company, backup_path, session_cache_path)

    except Exception as e:
        st.warning(f"⚠️ {company}: {str(e)}")


# --- Main Parallel Pull Function ---


def pull_logos_parallel(companies, backup_path, session_cache_path, max_workers=8):
    st.write(f"Downloading logos for {len(companies)} companies...")

    bar = st.progress(0, text="Starting...")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(
                process_single_logo, company, backup_path, session_cache_path
            ): company
            for company in companies["Company"]
        }

        for i, future in enumerate(as_completed(futures), 1):
            company = futures[future]
            bar.progress(i / len(futures), text=f"Processed {company}")

    bar.empty()
    st.success("✅ All logos processed.")
