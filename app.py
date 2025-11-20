import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Client Lookup", layout="wide")
st.title("Firmwide Client & Prospect Lookup")

DATA_FILE = "shared_crm_contacts.xlsx"

# THIS IS THE MAGIC: whoever opens the app FIRST becomes permanent admin
if "is_admin" not in st.session_state:
    st.session_state.is_admin = True          # ← You are the first → you become admin forever
else:
    st.session_state.is_admin = False         # Everyone after you = normal user

# Only YOU see the upload button (always visible for you)
if st.session_state.is_admin:
    st.sidebar.header("Admin Update")
    uploaded = st.sidebar.file_uploader("Upload latest CRM file", type=["xlsx", "xls"])
    if uploaded:
        pd.read_excel(uploaded, usecols="A:C", 
                     names=["Name", "Client Category", "Servicing Advisor"]) \
          .to_excel(DATA_FILE, index=False)
        st.sidebar.success("Updated for everyone!")
        st.rerun()

# Load data (real one if exists, otherwise blank dummy from GitHub)
if os.path.exists(DATA_FILE):
    df = pd.read_excel(DATA_FILE, usecols="A:C", names=["Name", "Client Category", "Servicing Advisor"])
else:
    df = pd.read_excel("crm_contacts.xlsx", usecols="A:C", names=["Name", "Client Category", "Servicing Advisor"])

# Clean search-only interface for everyone
st.write("#### Search by name, category, or advisor")
query = st.text_input("", placeholder="Start typing…", label_visibility="collapsed")

if query:
    results = df[df.apply(lambda row: row.astype(str).str.contains(query, case=False, na=False).any(), axis=1)]
    st.dataframe(results, use_container_width=True)
    st.write(f"**{len(results)}** result(s) found")
else:
    st.info("Type to search the client list")




