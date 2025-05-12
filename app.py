import streamlit as st
import pandas as pd
import plotly.express as px
from openai import OpenAI
import io
import contextlib

# Streamlit page settings
st.set_page_config(page_title="Chat Data Cleaner", layout="wide")
st.title("📊 Chat-Driven Data Cleaner & Visualizer")

# Initialize OpenAI client (correct way for v1.x)
client = OpenAI(api_key=st.secrets["openai_api_key"])

# File uploader
uploaded_file = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx"])

# Function to safely execute generated code
def safe_exec(code_string, local_vars):
    with contextlib.redirect_stdout(io.StringIO()) as f:
        try:
            exec(code_string, {}, local_vars)
            result = f.getvalue()
        except Exception as e:
            result = f"❗ Error during execution: {e}"
    return result

if uploaded_file:
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.subheader("📄 Uploaded Data")
    st.dataframe(df)

    # Chat query input
    query = st.text_input("Ask a question about your data (e.g., 'Show sales by category', 'Clean missing values')")

    if query:
        with st.spinner("Processing your request..."):
            prompt = f"""You are a helpful data analyst.
The user uploaded this dataset:
{df.head(5).to_markdown()}

User request: {query}

Write Python Pandas and Plotly code to fulfill the request.
- The dataframe is named 'df'.
- If you create a Plotly figure, assign it to 'fig'.
- Do not print explanations, only give code.
- Always clean data safely.
"""

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0
            )

            code = response.choices[0].message.content
            st.subheader("📝 Generated Code")
            st.code(code, language='python')

            # Execute generated code safely
            locals_dict = {'df': df, 'st': st, 'px': px, 'pd': pd}
            output = safe_exec(code, locals_dict)

            # Show console output if any
            if output.strip():
                st.text(output)

            # Show updated DataFrame if modified
            if 'df' in locals_dict:
                df = locals_dict['df']
                st.subheader("🔄 Updated Data")
                st.dataframe(df)

            # Show generated plot if available
            if 'fig' in locals_dict:
                st.subheader("📊 Visualization")
                st.plotly_chart(locals_dict['fig'])

    # Download button for cleaned data
    cleaned_csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download Cleaned CSV", cleaned_csv, "cleaned_data.csv", "text/csv")

else:
    st.info("Please upload a CSV or Excel file to get started.")
