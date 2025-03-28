import streamlit as st
import pandas as pd
import os
import sqlite3

# ---- App configuration ----
st.set_page_config(page_title="File Analysis and SQL Demo", page_icon="📊", layout="wide")

# ---- Sidebar with instructions ----
st.sidebar.title("📚 Instructions")
st.sidebar.markdown("""
1. **Upload a file:** Select a CSV, Excel, Parquet, or JSON file.
2. **Analyze Data:** Automatically detect column types.
3. **Run SQL Query:** Write SQL commands to manipulate or query the data.
4. **Export Results:** Download the query result as a CSV file.
""")
st.sidebar.info("💡 Tip: Click on 'Run Query' after writing your SQL query.")

# ---- Folder for available files ----
DATA_FOLDER = './data'

# Create folder if it doesn't exist
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

# ---- Function to list available files ----
def list_available_files():
    files = os.listdir(DATA_FOLDER)
    return [f for f in files if f.endswith(('csv', 'xlsx', 'parquet', 'json'))]

# ---- File upload or selection ----
st.title('📊 File Analysis and SQL Demo')

# Sidebar file uploader
uploaded_file = st.sidebar.file_uploader("📂 Upload a file", type=["csv", "xlsx", "parquet", "json"])

# List available files in sidebar
available_files = list_available_files()
selected_file = st.sidebar.selectbox("📚 Select a file from the repository", available_files) if not uploaded_file else None

# ---- Load the selected file ----
def load_file(file):
    ext = file.name.split('.')[-1]
    try:
        if ext == 'csv':
            return pd.read_csv(file, low_memory=False)
        elif ext == 'xlsx':
            return pd.read_excel(file)
        elif ext == 'parquet':
            return pd.read_parquet(file)
        elif ext == 'json':
            return pd.read_json(file)
        else:
            st.error("❌ Unsupported file format. Please upload a valid file.")
            return None
    except Exception as e:
        st.error(f"⚠️ Error loading file: {e}")
        return None

# ---- Analyze the data ----
def analyze_data(df):
    st.subheader("🔎 Table Description")
    description = pd.DataFrame({
        'Column Name': df.columns,
        'Data Type': [str(df[col].dtype) for col in df.columns]
    })
    st.dataframe(description, use_container_width=True)

# ---- Load and analyze data ----
if uploaded_file:
    df = load_file(uploaded_file)
elif selected_file:
    file_path = os.path.join(DATA_FOLDER, selected_file)
    df = load_file(open(file_path, 'rb'))
else:
    st.warning("⚠️ No file uploaded or selected. Please upload a file to proceed.")
    df = None

if df is not None:
    st.success("✅ File loaded successfully!")
    analyze_data(df)

    # Save data in SQLite
    conn = sqlite3.connect(':memory:')
    df.to_sql('data', conn, if_exists='replace', index=False)

    # ---- SQL query box ----
    st.subheader("📝 Run SQL Query")
    query = st.text_area("Write your SQL query (e.g., SELECT * FROM data)", "SELECT * FROM data LIMIT 5")

    if st.button("🚀 Run Query"):
        try:
            result = pd.read_sql_query(query, conn)
            st.write("📊 **Query Results:**")
            st.dataframe(result, use_container_width=True)

            # ---- Export results ----
            st.download_button(
                label="💾 Export results as CSV",
                data=result.to_csv(index=False),
                file_name="query_results.csv",
                mime="text/csv"
            )
        except Exception as e:
            st.error(f"❌ Error in query: {e}")
else:
    st.info("📂 Please upload a file to get started.")
