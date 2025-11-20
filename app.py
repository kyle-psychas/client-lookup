import streamlit as st
import pandas as pd
import os

# --- Page config ---
st.set_page_config(page_title="Client Lookup", layout="wide")

# --- PASSWORD PROTECTION ---
ACCESS_PASSWORD = st.secrets["app"]["ACCESS_PASSWORD"]  # Stored securely in Streamlit Secrets

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    password = st.text_input("Enter password to access the app:", type="password")
    if password == ACCESS_PASSWORD:
        st.session_state.authenticated = True
        st.success("Access granted")
        # First authenticated user becomes admin
        if "is_admin" not in st.session_state:
            st.session_state.is_admin = True
    else:
        st.warning("Enter the correct password to continue")
        st.stop()

# --- App title ---
st.title("Firmwide Client & Prospect Lookup")

DATA_FILE = "shared_crm_contacts.xlsx"

# --- Admin upload (only visible to admin) ---
if st.session_state.get("is_admin", False):
    st.sidebar.header("Admin Update")
    uploaded = st.sidebar.file_uploader("Upload latest CRM file", type=["xlsx", "xls"])
    if uploaded:
        pd.read_excel(uploaded, usecols="A:C",
                      names=["Name", "Client Category", "Servicing Advisor"]) \
          .to_excel(DATA_FILE, index=False)
        st.sidebar.success("Updated for everyone!")
        st.experimental_rerun()  # Reload app with new data

# --- Load data ---
if os.path.exists(DATA_FILE):
    df = pd.read_excel(DATA_FILE, usecols="A:C",
                       names=["Name", "Client Category", "Servicing Advisor"])
else:
    df = pd.read_excel("crm_contacts.xlsx", usecols="A:C",
                       names=["Name", "Client Category", "Servicing Advisor"])

# --- Search interface ---
st.write("#### Search by name, category, or advisor")
query = st.text_input("", placeholder="Start typing…", label_visibility="collapsed")

if query:
    results = df[df.apply(lambda row: row.astype(str).str.contains(query, case=False, na=False).any(), axis=1)]
    st.dataframe(results, use_container_width=True)
    st.write(f"**{len(results)}** result(s) found")
else:
    st.info("Type to search the client list")






