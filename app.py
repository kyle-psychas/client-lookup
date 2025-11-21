# app.py
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Client Lookup", layout="wide")

# ========================= SECRETS =========================
ACCESS_PASSWORD = st.secrets["app"]["ACCESS_PASSWORD"]
ADMIN_PASSWORD  = st.secrets["app"]["ADMIN_PASSWORD"]

# ========================= SESSION STATE =========================
for key in ["authenticated", "is_admin", "df"]:
    if key not in st.session_state:
        st.session_state[key] = False if key != "df" else None

# ========================= AUTH =========================
if not st.session_state.authenticated:
    st.title("Firmwide Client & Prospect Lookup")
    pwd = st.text_input("Enter password", type="password")
    if pwd:
        if pwd == ADMIN_PASSWORD:
            st.session_state.authenticated = True
            st.session_state.is_admin = True
            st.rerun()
        elif pwd == ACCESS_PASSWORD:
            st.session_state.authenticated = True
            st.session_state.is_admin = False
            st.rerun()
        else:
            st.error("Incorrect password")
    st.stop()

# ========================= ADMIN UPLOAD =========================
if st.session_state.is_admin:
    with st.sidebar:
        st.header("Admin Upload")
        uploaded = st.file_uploader("Upload new 3-column Excel file", type=["xlsx", "xls"])

        if uploaded:
            # This ONE line reads ANY normal CRM export perfectly
            df_new = pd.read_excel(uploaded, usecols=[0,1,2], header=None)
            df_new.columns = ["Name", "Client Category", "Servicing Advisor"]
            df_new = df_new.astype(str).apply(lambda x: x.str.strip())
            
            st.session_state.df = df_new
            st.success(f"Loaded {uploaded.name} → {len(df_new)} rows")
            st.rerun()

# ========================= LOAD DATA =========================
if st.session_state.df is not None:
    df = st.session_state.df.copy()
else:
    # Default file that MUST be in your repo
    df = pd.read_excel("crm_contacts.xlsx", usecols=[0,1,2], header=None)
    df.columns = ["Name", "Client Category", "Servicing Advisor"]
    df = df.astype(str).apply(lambda x: x.str.strip())

st.caption(f"Total records: {len(df)}  •  {'Uploaded file' if st.session_state.df is not None else 'Default file'}")

# ========================= SEARCH (GUARANTEED TO WORK) =========================
st.markdown("### Search clients")
query = st.text_input("", placeholder="Type any name, category or advisor…", label_visibility="collapsed")

if query:
    q = query.strip()
    # This search line works every single time
    results = df[df.astype(str).apply(lambda row: row.str.contains(q, case=False, na=False).any(), axis=1)]
    
    if len(results):
        st.dataframe(results.reset_index(drop=True), use_container_width=True)
        st.success(f"Found {len(results)} match(es)")
    else:
        st.warning("No matches – try partial name")
else:
    st.info("Start typing to search")
    st.dataframe(df.head(20), use_container_width=True)

# ========================= ADMIN TOOLS =========================
if st.session_state.is_admin:
    with st.sidebar:
        st.markdown("---")
        if st.button("← Revert to default file"):
            st.session_state.df = None
            st.rerun()

















