import pandas as pd
from openai import OpenAI
import re
import streamlit as st

# Initialize the OpenAI client using the API key stored securely in Streamlit secrets
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])


def clean_lines(text: str) -> list[str]:
    """
    Cleans a multiline string by removing leading bullets, numbers, or symbols
    from each line while preserving company names.

    Args:
        text (str): Multiline string containing company names (possibly numbered or bulleted).

    Returns:
        list[str]: Cleaned list of company names.
    """
    lines = text.strip().split("\n")
    cleaned = []
    for line in lines:
        # Remove common leading patterns like "1.", "2)", "-", "•"
        cleaned_line = re.sub(r"^\s*(?:\d+[\.\)\-]?|[\-\•])\s*", "", line)
        if cleaned_line:
            cleaned.append(cleaned_line.strip())
    return cleaned


def get_company_list_from_prompt(
    prompt: str, model: str = "gpt-3.5-turbo", max_tokens: int = 1000
) -> pd.DataFrame:
    """
    Queries the OpenAI API to generate a list of company names from a natural language prompt.

    Args:
        prompt (str): User-defined request, e.g., "the top 50 tech startups in Europe".
        model (str): OpenAI language model to use (default is "gpt-3.5-turbo").
        max_tokens (int): Maximum token length for the API response.

    Returns:
        pd.DataFrame: DataFrame with a single 'Company' column listing extracted company names.
    """
    full_prompt = (
        f"Please list the names of {prompt}. "
        "Only provide company names, each on a new line. Do not include numbers, bullet points, or explanations."
    )

    try:
        # Send request to OpenAI chat API
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that returns clean lists of companies.",
                },
                {"role": "user", "content": full_prompt},
            ],
            max_tokens=max_tokens,
            temperature=0.3,
        )

        # Extract and clean the response text
        raw_text = response.choices[0].message.content.strip()
        cleaned_companies = clean_lines(raw_text)

        return pd.DataFrame(cleaned_companies, columns=["Company"])

    except Exception as e:
        # Log the error and return an empty DataFrame
        print(f"OpenAI API error: {e}")
        return pd.DataFrame(columns=["Company"])
