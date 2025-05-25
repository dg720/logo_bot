import streamlit as st
import pandas as pd
from src.logos import pull_logos

st.title("LogoBot")
st.markdown("Upload your data and get predictions.")

# st.write("### Input Data")
# col1, col2 = st.columns(2)
# home_value = col1.number_input("Home Value", min_value=0, value=500000)
# deposit = col1.number_input("Deposit", min_value=0, value=100000)
# interest_rate = col2.number_input("Interest Rate (in %)", min_value=0.0, value=5.5)
# loan_term = col2.number_input("Loan Term (in years)", min_value=1, value=30)

company_input = st.text_area(
    "Company Names", height=200, placeholder="e.g. Apple\nGoogle\nAmazon"
)

if st.button("Create DataFrame"):
    if company_input.strip():
        # Clean and split the input into a list
        company_list = [
            name.strip() for name in company_input.strip().split("\n") if name.strip()
        ]
        df = pd.DataFrame(company_list, columns=["Company"])
        st.success(f"Created a DataFrame with {len(df)} companies.")
        st.dataframe(df)
        pull_logos(df)
        st.success("function run")

        logo_files = [
            f for f in logos if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))
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
                logo_path = os.path.join(logos, logo_file)
                with cols[idx]:
                    st.image(
                        logo_path,
                        use_column_width=True,
                        caption=logo_file.split(".")[0].title(),
                    )
    else:
        st.warning("Please enter at least one company name.")
