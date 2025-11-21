import streamlit as st
import pandas as pd

# --- Page Config ---
st.set_page_config(page_title="Client Lookup", layout="wide")

# --- Secrets ---
ACCESS_PASSWORD = st.secrets["app"]["ACCESS_PASSWORD"]
ADMIN_PASSWORD = st.secrets["app"]["ADMIN_PASSWORD"]

# --- Session State Initialization ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.is_admin = False
    st.session_state.df = None          # Holds the current dataframe
    st.session_state.data_source = ""   # For display info

# ===================== AUTHENTICATION =====================
if not st.session_state.authenticated:
    st.title("Firmwide Client & Prospect Lookup")
    st.markdown("### Enter password to access the app")
    
    pwd = st.text_input("Password", type="password", key="pwd_input")
    
    if pwd:
        if pwd == ADMIN_PASSWORD:
            st.session_state.authenticated = True
            st.session_state.is_admin = True
            st.success("Admin access granted!")
            st.rerun()
        elif pwd == ACCESS_PASSWORD:
            st.session_state.authenticated = True
            st.session_state.is_admin = False
            st.success("Access granted!")
            st.rerun()
        else:
            st.error("Incorrect password")
    st.stop()

# ===================== AUTHENTICATED APP =====================
st.title("Firmwide Client & Prospect Lookup")

# --- Admin Upload (Sidebar) ---
if st.session_state.is_admin:
    st.sidebar.header("Admin: Upload New CRM Data")
    uploaded_file = st.sidebar.file_uploader(
        "Upload updated Excel file",
        type=["xlsx", "xls"],
        help="Only first 3 columns are used: Name, Client Category, Servicing Advisor"
    )
    
    if uploaded_file is not None:
        try:
            # Read the uploaded file correctly
            df_new = pd.read_excel(
                uploaded_file,
                usecols=range(3),  # Columns A, B, C (0-indexed)
                header=None,
                names=["Name", "Client Category", "Servicing Advisor"],
                engine="openpyxl"
            )
            # Clean any NaN or weird values
            df_new = df_new.fillna("")
            
            # Save to session state so it survives reruns
            st.session_state.df = df_new
            st.session_state.data_source = f"Uploaded file: {uploaded_file.name} ({len(df_new)} records)"
            
            st.sidebar.success("New data loaded successfully!")
            st.sidebar.write(f"**Rows:** {len(df_new)}")
            st.rerun()
            
        except Exception as e:
            st.sidebar.error(f"Error reading file: {e}")

# --- Load Data (with correct priority) ---
@st.cache_data(ttl=3600)  # Cache fallback files only
def load_default_data():
    return pd.read_excel(
        "crm_contacts.xlsx",
        usecols=range(3),
        header=None,
        names=["Name", "Client Category", "Servicing Advisor"]
    ).fillna("")

# Priority: 1. Uploaded (session), 2. Default file in repo
if st.session_state.df is not None:
    df = st.session_state.df.copy()
    source_info = st.session_state.data_source
else:
    df = load_default_data()
    source_info = f"Default file (crm_contacts.xlsx) – {len(df)} records"

# Show data source info
st.caption(f"Data source: {source_info}")

# ===================== SEARCH INTERFACE =====================
st.markdown("#### Search by name, category, or advisor")
query = st.text_input(
    "",
    placeholder="Type to search instantly…",
    label_visibility="collapsed",
    key="main_search"
)

# Make search case-insensitive and robust
if query.strip():
    query = query.strip()
    mask = df.astype(str).apply(
        lambda col: col.str.contains(query, case=False, na=False, regex=False)
    ).any(axis=1)
    results = df[mask].reset_index(drop=True)
    
    if len(results) > 0:
        st.dataframe(results, use_container_width=True)
        st.success(f"**{len(results)}** result(s) found")
    else:
        st.warning("No matches found. Try different keywords.")
else:
    # Show a preview when no search
    st.info("Start typing above to search")
    preview = df.head(20)
    st.dataframe(preview, use_container_width=True)
    if len(df) > 20:
        st.caption(f"Showing first 20 of {len(df)} total records")

# --- Admin Footer ---
if st.session_state.is_admin:
    with st.sidebar:
        st.markdown("---")
        st.write("**Admin Tools**")
        if st.button("Clear uploaded data → revert to default"):
            st.session_state.df = None
            st.session_state.data_source = ""
            st.rerun()
        st.write(f"Total records loaded: **{len(df)}**")














