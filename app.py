import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Client Lookup", layout="wide")
st.title("Firmwide Client & Prospect Lookup")

DATA_FILE = "shared_crm_contacts.xlsx"   # This lives inside the app, not on GitHub

# 1. Admin upload (you) can upload the real file once
if not os.path.exists(DATA_FILE):
    st.warning("No shared data file found yet.")
    uploaded = st.file_uploader(
        "Admin only: Upload the real CRM file (it will be saved for everyone)",
        type=["xlsx", "xls"],
        key="admin"
    )
    if uploaded:
        df_temp = pd.read_excel(uploaded, usecols="A:C", names=["Name", "Client Category", "Servicing Advisor"])
        df_temp.to_excel(DATA_FILE, index=False)
        st.success("Real data saved! Everyone will now see the updated data forever.")
        st.rerun()

# 2. Load the shared file (real one if it exists, otherwise dummy from GitHub)
if os.path.exists(DATA_FILE):
    df = pd.read_excel(DATA_FILE, usecols="A:C", names=["Name", "Client Category", "Servicing Advisor"])
    st.success("Showing latest shared data (updated by admin)")
else:
    # Fallback to the blank dummy that lives safely on GitHub
    df = pd.read_excel("crm_contacts.xlsx", usecols="A:C", names=["Name", "Client Category", "Servicing Advisor"])
    st.info("Showing blank template — waiting for admin to upload real data")

# 3. Normal search (same as always)
st.write("Type a client's name, category, or advisor to search.")
query = st.text_input("Search here:", key="search")

if query:
    results = df[df.apply(lambda row: row.astype(str).str.contains(query, case=False, na=False).any(), axis=1)]
    st.dataframe(results, use_container_width=True)
    st.write(f"**{len(results)}** result(s) found")
else:
    with st.expander("Show full list", expanded=True):
        st.dataframe(df, use_container_width=True)


