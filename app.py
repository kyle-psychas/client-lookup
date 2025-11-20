import streamlit as st
import pandas as pd
import os

# ==========================
# Page Config & Title
# ==========================
st.set_page_config(page_title="Client Lookup", layout="wide")
st.title("Firmwide Client & Prospect Lookup")

# ==========================
# 1. File Uploader (takes priority)
# ==========================
uploaded_file = st.file_uploader(
    "Upload your updated CRM Excel file (optional)",
    type=["xlsx", "xls"],
    help="Drag & drop or browse. If no file is uploaded, the default crm_contacts.xlsx from the repo will be used."
)

# ==========================
# 2. Load Data Function (with caching)
# ==========================
@st.cache_data(ttl=600)  # refresh cache every 10 minutes
def load_data_from_bytes(file_bytes) -> pd.DataFrame:
    return pd.read_excel(file_bytes, usecols="A:C", names=["Name", "Client Category", "Servicing Advisor"])

@st.cache_data(ttl=3600)  # longer cache for the repo version
def load_data_from_disk() -> pd.DataFrame:
    file_path = "crm_contacts.xlsx"
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Default file not found: {file_path}")
    return pd.read_excel(file_path, usecols="A:C", names=["Name", "Client Category", "Servicing Advisor"])

# ==========================
# 3. Decide which data to use
# ==========================
if uploaded_file is not None:
    # User uploaded something → use it
    try:
        df = load_data_from_bytes(uploaded_file)
        st.success(f"Loaded uploaded file: **{uploaded_file.name}** ({uploaded_file.size:,} bytes)")
    except Exception as e:
        st.error(f"Could not read the uploaded file: {e}")
        st.stop()
else:
    # No upload → use the file from the repo / local folder
    try:
        df = load_data_from_disk()
        st.info("Using default file: `crm_contacts.xlsx` from the repository")
    except FileNotFoundError:
        st.error("Default file `crm_contacts.xlsx` not found in the repository.")
        st.info("Please either:")
        st.info("- Add the file to your GitHub repo root, or")
        st.info("- Upload it using the uploader above")
        st.stop()
    except Exception as e:
        st.error(f"Error loading default file: {e}")
        st.stop()

# ==========================
# 4. Search UI (unchanged – works perfectly)
# ==========================
st.write("Type a client's name, category, or advisor to search.")
query = st.text_input("Search here:", key="search")

if query:
    results = df[df.apply(
        lambda row: row.astype(str).str.contains(query, case=False, na=False).any(),
        axis=1
    )].copy()
    
    if len(results) > 0:
        st.dataframe(results, use_container_width=True)
        st.write(f"**{len(results)}** result(s) found")
    else:
        st.warning("No matches found.")
else:
    st.info("Start typing to see results.")
    # Optional: show full table when nothing is searched
    with st.expander("Show full client list", expanded=False):
        st.dataframe(df, use_container_width=True)

