import os
import requests
import time
import streamlit as st
from googlesearch import search
from urllib.parse import urlparse
import random
import retrying
import shutil


def get_company_website(company_name):
    """
    Performs a Google search to find the official website of a company.

    Args:
        company_name (str): Name of the company to search.

    Returns:
        str or None: First search result URL that is not a Wikipedia or LinkedIn link.
    """
    query = f"{company_name} official site"
    for result in search(query):
        if "wikipedia" not in result.lower() and "linkedin" not in result.lower():
            return result
    return None


def extract_domain(url):
    """
    Extracts the domain from a given URL.

    Args:
        url (str): A full website URL.

    Returns:
        str or None: The domain name, excluding "www.", or None if parsing fails.
    """
    try:
        parsed_url = urlparse(url)
        return parsed_url.netloc.replace("www.", "")
    except Exception:
        return None


@retrying.retry(stop_max_attempt_number=5, wait_fixed=2000)
def download_logo(company_url, company_name, backup_path, session_cache_path):
    """
    Downloads a company logo using Brandfetch and saves it locally.
    Retries up to 5 times in case of failure.

    Args:
        company_url (str): The company domain (e.g., "example.com").
        company_name (str): The display name to save the file as.
        save_path (str): Folder path to save the logos.
    """
    api_key = st.secrets["BRANDFETCH_API_KEY"]
    logo_url = f"https://cdn.brandfetch.io/{company_url}/w/512/h/94/logo?c={api_key}"

    # Random user-agent header to avoid basic scraping blocks
    headers = {
        "User-Agent": random.choice(
            [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
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
        # os.makedirs(backup_path, exist_ok=True)

        content_type = response.headers["Content-Type"]
        extension = content_type.split("/")[-1]
        if extension == "webp":
            extension = "png"

        file_path = os.path.join(backup_path, f"{company_name}.{extension}")
        cache_path = os.path.join(session_cache_path, f"{company_name}.{extension}")

        # Read all content once
        content = response.content

        # Save to backup path
        with open(file_path, "wb") as f:
            f.write(content)

        # Save to cache path
        with open(cache_path, "wb") as f:
            f.write(content)

    else:
        raise Exception("Failed request")


def pull_logos(companies, backup_path, session_cache_path):
    """
    Reads a list of companies and downloads their logos, using cache and backup folders.
    """
    # os.makedirs(backup_path, exist_ok=True)
    # os.makedirs(session_cache_path, exist_ok=True)

    num_companies = len(companies)
    bar = st.progress(0, text="Initialising...")

    for n, company in enumerate(companies["Company"], start=1):
        bar.progress(n / num_companies, text=f"Processing {company}...")

        # Check for existing logo in backup
        backup_file = next(
            (f for f in os.listdir(backup_path) if f.startswith(company)), None
        )

        if backup_file:
            # Copy to session cache if not already there
            source = os.path.join(backup_path, backup_file)
            destination = os.path.join(session_cache_path, backup_file)
            if not os.path.exists(destination):
                shutil.copy2(source, destination)
            continue  # Skip download if already exists

        # If not in backup, try to find and download
        website = get_company_website(company)
        if website:
            domain = extract_domain(website)
            if domain:
                try:
                    download_logo(domain, company, backup_path, session_cache_path)
                except Exception as e:
                    st.warning(f"Failed to download logo for {company}: {e}")

        time.sleep(random.uniform(1, 3))  # polite delay

    bar.empty()
