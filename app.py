import streamlit as st
import pandas as pd
import plotly.express as px
import io
import openai

# Load OpenAI API key
openai.api_key = st.secrets["openai_api_key"]

st.title("Chat-Driven Data Cleaner & Visualizer")

# File uploader
uploaded_file = st.file_uploader("Upload CSV/XLSX file", type=['csv', 'xlsx'])

if uploaded_file:
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.write("### Uploaded Data", df)

    # User query
    query = st.text_input("Ask a question or request a graph (e.g., 'Clean data', 'Show sales by month')")

    if query:
        # Generate response from OpenAI
        prompt = f"""You are a data analyst. The user uploaded this dataset:\n\n{df.head(5)}\n\nUser asked: {query}\n\nRespond with Python Pandas code that solves their request."""
        
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        code = response['choices'][0]['message']['content']

        st.write("### Suggested Code", f"```python\n{code}\n```")

        # Execute code (safe eval for you later, but for demo we skip auto-execution)

        st.warning("Manual execution for safety. Copy code to test.")

        # Example: Graph visualization (hardcoded example for demo)
        if "sales" in query.lower():
            if "month" in df.columns:
                fig = px.bar(df, x="month", y=df.columns[1])
                st.plotly_chart(fig)

    # Download cleaned data
    cleaned_csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download Cleaned CSV", cleaned_csv, "cleaned_data.csv", "text/csv")
