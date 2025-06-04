import os
import requests
import streamlit as st
import random
import shutil
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from googlesearch import search
import retrying
import threading

# ---------------------- #
#      Utilities         #
# ---------------------- #


def get_company_website(company_name):
    """
    Perform a Google search to retrieve the official website of the given company.

    Args:
        company_name (str): Name of the company.

    Returns:
        str or None: First non-Wikipedia/LinkedIn URL found, or None if not found.
    """
    query = f"{company_name} official site"
    for result in search(query):
        if "wikipedia" not in result.lower() and "linkedin" not in result.lower():
            return result
    return None


def extract_domain(url):
    """
    Extracts the domain from a URL (e.g., 'example.com' from 'https://www.example.com').

    Args:
        url (str): A full website URL.

    Returns:
        str or None: Clean domain name, or None if extraction fails.
    """
    try:
        parsed_url = urlparse(url)
        return parsed_url.netloc.replace("www.", "")
    except Exception:
        return None


@retrying.retry(stop_max_attempt_number=5, wait_fixed=2000)
def download_logo(company_url, company_name, backup_path, session_cache_path):
    """
    Downloads the company logo using Brandfetch API and saves it to both backup and session folders.

    Args:
        company_url (str): Company domain (e.g., 'example.com').
        company_name (str): Clean name used for saving the logo.
        backup_path (str): Path to store persistent logo backup.
        session_cache_path (str): Path to store session-specific logo.

    Raises:
        Exception: If the logo request fails or no image is returned.
    """
    api_key = st.secrets["BRANDFETCH_API_KEY"]
    logo_url = f"https://cdn.brandfetch.io/{company_url}/w/512/h/94/logo?c={api_key}"

    # Rotate user-agents to avoid bot detection
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
            extension = "png"  # Normalize to PNG for compatibility

        file_name = f"{company_name}.{extension}"
        file_path = os.path.join(backup_path, file_name)
        cache_path = os.path.join(session_cache_path, file_name)

        # Save logo to both backup and session-specific folders
        content = response.content
        with open(file_path, "wb") as f:
            f.write(content)
        with open(cache_path, "wb") as f:
            f.write(content)
    else:
        raise Exception("Logo download failed")


def process_single_logo(company, backup_path, session_cache_path, failed_logos, lock):
    """
    Attempts to fetch a logo from cache or download it; logs failures in a thread-safe manner.

    Args:
        company (str): Company name to process.
        backup_path (str): Folder to check for cached logo.
        session_cache_path (str): Session-specific folder for logo copies.
        failed_logos (list): Shared list for tracking failures.
        lock (threading.Lock): Lock for thread-safe access to `failed_logos`.
    """
    try:
        # Reuse backup logo if available
        backup_file = next(
            (f for f in os.listdir(backup_path) if f.startswith(company)), None
        )
        if backup_file:
            source = os.path.join(backup_path, backup_file)
            destination = os.path.join(session_cache_path, backup_file)
            if not os.path.exists(destination):
                shutil.copy2(source, destination)
            return

        # Attempt fresh download if not in backup
        website = get_company_website(company)
        if website:
            domain = extract_domain(website)
            if domain:
                download_logo(domain, company, backup_path, session_cache_path)
            else:
                raise Exception("Could not extract domain")
        else:
            raise Exception("Could not find website")

    except Exception:
        with lock:
            failed_logos.append(company)


# ------------------------------- #
#   Main Parallel Pull Function   #
# ------------------------------- #


def pull_logos_parallel(companies, backup_path, session_cache_path, max_workers=8):
    """
    Downloads company logos in parallel using thread pool execution.

    Args:
        companies (pd.DataFrame): DataFrame containing a 'Company' column.
        backup_path (str): Directory for persistent logo storage.
        session_cache_path (str): Directory for session-specific logo use.
        max_workers (int): Number of parallel threads to use.
    """
    st.write(f"Downloading logos for {len(companies)} companies...")
    bar = st.progress(0, text="Starting...")

    failed_logos = []
    lock = threading.Lock()

    # Dispatch threads for each logo fetch
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(
                process_single_logo,
                company,
                backup_path,
                session_cache_path,
                failed_logos,
                lock,
            ): company
            for company in companies["Company"]
        }

        # Update progress bar as threads complete
        for i, future in enumerate(as_completed(futures), 1):
            company = futures[future]
            bar.progress(i / len(futures), text=f"Processed {company}")

    bar.empty()
    st.success("✅ Logos processed")

    # Display list of companies whose logos couldn't be found
    if failed_logos:
        error_message = "⚠️ Logos could not be found for the following companies:\n\n"
        error_message += "\n".join(f"- {name}" for name in failed_logos)
        st.error(error_message)
