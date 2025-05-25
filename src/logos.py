import os
import requests
import time
import streamlit as st
from googlesearch import search
from urllib.parse import urlparse
import random
import retrying


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
def download_logo(company_url, company_name, save_path="logo_backup"):
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
        os.makedirs(save_path, exist_ok=True)

        content_type = response.headers["Content-Type"]
        extension = content_type.split("/")[-1]
        if extension == "webp":
            extension = "png"

        file_path = os.path.join(save_path, f"{company_name}.{extension}")

        # Save image to disk
        with open(file_path, "wb") as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
    else:
        raise Exception("Failed request")


def pull_logos(companies):
    """
    Main function that reads a CSV of companies and attempts to download their logos.

    Args:
        csv_path (str): Path to a CSV file with a 'Company' column.
    """
    os.makedirs("logo_backup", exist_ok=True)
    num_companies = len(companies)
    n = 0
    bar = st.progress(0, text="Initialising...")

    for company in companies["Company"]:
        n += 1
        existing_files = os.listdir("logo_backup")
        bar.progress(n / num_companies, text=f"Searching for {company}")

        # Skip if logo already exists for this company
        if any(company in file for file in existing_files):
            continue

        # Find website and domain
        website = get_company_website(company)
        if website:
            domain = extract_domain(website)
            if domain:
                download_logo(domain, company)

        # Sleep to avoid being flagged for automated requests
        time.sleep(random.uniform(1, 3))

    bar.empty()
