import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Client Lookup", layout="wide")
st.title("Firmwide Client & Prospect Lookup")

DATA_FILE = "shared_crm_contacts.xlsx"

# Admin only: upload the real file once (only appears if not already saved)
if not os.path.exists(DATA_FILE):
    st.warning("No data file found yet – admin needs to upload the real CRM file.")
    uploaded = st.file_uploader(
        "Admin: Upload the latest CRM Excel file (saved forever for everyone)",
        type=["xlsx", "xls"]
    )
    if uploaded:
        pd.read_excel(uploaded, usecols="A:C", 
                     names=["Name", "Client Category", "Servicing Advisor"]) \
          .to_excel(DATA_FILE, index=False)
        st.success("Real data saved! Refreshing…")
        st.rerun()

# Load the real data (or blank dummy if admin hasn't uploaded yet)
if os.path.exists(DATA_FILE):
    df = pd.read_excel(DATA_FILE, usecols="A:C",
                       names=["Name", "Client Category", "Servicing Advisor"])
    st.success("Showing latest firmwide data")
else:
    df = pd.read_excel("crm_contacts.xlsx", usecols="A:C",
                       names=["Name", "Client Category", "Servicing Advisor"])
    st.info("Blank template – waiting for admin upload")

# Just the search bar – nothing else on screen until they type
st.write("#### Search by name, category, or advisor")
query = st.text_input("", placeholder="Start typing…", label_visibility="collapsed")

if query:
    results = df[df.apply(
        lambda row: row.astype(str).str.contains(query, case=False, na=False).any(),
        axis=1
    )]
    st.dataframe(results, use_container_width=True)
    st.write(f"**{len(results)}** result(s) found")
else:
    st.info("Type above to search the client list")



