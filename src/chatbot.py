import pandas as pd
from openai import OpenAI
import re
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def clean_lines(text):
    """
    Remove bullets/numbers from beginning of lines only. Preserve valid names.
    """
    lines = text.strip().split("\n")
    cleaned = []
    for line in lines:
        # Remove patterns like "1.", "2)", "-", "•"
        cleaned_line = re.sub(r"^\s*(?:\d+[\.\)\-]?|[\-\•])\s*", "", line)
        if cleaned_line:
            cleaned.append(cleaned_line.strip())
    return cleaned


def get_company_list_from_prompt(
    prompt: str, model: str = "gpt-3.5-turbo", max_tokens: int = 300
) -> pd.DataFrame:
    full_prompt = (
        f"Please list the names of {prompt}. "
        "Only provide company names, each on a new line. Do not include numbers, bullet points, or explanations."
    )

    try:
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

        raw_text = response.choices[0].message.content.strip()
        cleaned_companies = clean_lines(raw_text)
        return pd.DataFrame(cleaned_companies, columns=["Company"])

    except Exception as e:
        print(f"OpenAI API error: {e}")
        return pd.DataFrame(columns=["Company"])
