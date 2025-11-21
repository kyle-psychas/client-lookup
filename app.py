import streamlit as st
import pandas as pd
import os

# --- Page config ---
st.set_page_config(page_title="Client Lookup", layout="wide")

# --- Load passwords from Streamlit Secrets ---
ACCESS_PASSWORD = st.secrets["app"]["ACCESS_PASSWORD"]
ADMIN_PASSWORD = st.secrets["app"]["ADMIN_PASSWORD"]

# --- Initialize session state ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.is_admin = False
    st.session_state.df = None  # Will hold the current data

# --- PASSWORD CHECK ---
if not st.session_state.authenticated:
    st.title("Firmwide Client & Prospect Lookup")
    st.write("#### Please enter the password to continue")
    
    password = st.text_input("Password", type="password", key="password_input")
    
    if password:
        if password == ADMIN_PASSWORD:
            st.session_state.authenticated = True
            st.session_state.is_admin = True
            st.success("Admin access granted")
            st.rerun()
        elif password == ACCESS_PASSWORD:
            st.session_state.authenticated = True
            st.session_state.is_admin = False
            st.success("Access granted")
            st.rerun()
        else:
            st.error("Incorrect password. Try again.")
            st.stop()
    else:
        st.stop()

# --- Main App (User is authenticated) ---
st.title("Firmwide Client & Prospect Lookup")

# --- Admin Upload Section (Sidebar) ---
if st.session_state.is_admin:
    st.sidebar.header("Admin: Update CRM Data")
    uploaded = st.sidebar.file_uploader(
        "Upload latest CRM file (Excel)", 
        type=["xlsx", "xls"],
        help="Only columns A–C will be used: Name, Client Category, Servicing Advisor"
    )
    
    if uploaded:
        try:
            new_df = pd.read_excel(
                uploaded,
                usecols="A:C",
                names=["Name", "Client Category", "Servicing Advisor"],
                engine="openpyxl"
            )
            st.session_state.df = new_df
            st.sidebar.success("File uploaded and updated successfully!")
            st.sidebar.dataframe(new_df.head(), use_container_width=True)
            st.rerun()  # Refresh the app to show new data immediately
        except Exception as e:
            st.sidebar.error(f"Error reading file: {e}")

# --- Load Data ---
def load_data():
    # Priority: 1. Session state (latest upload), 2. Local fallback, 3. GitHub default
    if st.session_state.df is not None:
        return st.session_state.df.copy()
    
    fallback_local = "crm_contacts.xlsx"
    if os.path.exists(fallback_local):
        return pd.read_excel(
            fallback_local,
            usecols="A:C",
            names=["Name", "Client Category", "Servicing Advisor"]
        )
    
    # Final fallback: bundled default file (should be in your repo)
    default_file = "crm_contacts.xlsx"
    return pd.read_excel(
        default_file,
        usecols="A:C",
        names=["Name", "Client Category", "Servicing Advisor"]
    )

df = load_data()

# --- Search Interface ---
st.write("#### Search by name, category, or advisor")
query = st.text_input(
    "",
    placeholder="Start typing to search…",
    label_visibility="collapsed",
    key="search_query"
)

if query.strip():
    mask = df.apply(
        lambda row: row.astype(str).str.contains(query, case=False, na=False).any(),
        axis=1
    )
    results = df[mask].reset_index(drop=True)
    st.dataframe(results, use_container_width=True)
    st.write(f"**{len(results)}** result(s) found")
else:
    st.info("Start typing above to search the client list")
    st.dataframe(df.head(10), use_container_width=True)  # Optional preview
    if len(df) > 10:
        st.write(f"... and {len(df) - 10} more rows")

# --- Footer ---
if st.session_state.is_admin:
    st.sidebar.markdown("---")
    st.sidebar.write(f"**Total records:** {len(df)}")
    st.sidebar.caption("You are logged in as **Admin**")
else:
    st.caption(f"Total records: {len(df)} | Last updated: see admin for details")













