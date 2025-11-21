# app.py
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Client Lookup", layout="wide")

# ====================== SECRETS ======================
ACCESS_PASSWORD = st.secrets["app"]["ACCESS_PASSWORD"]
ADMIN_PASSWORD  = st.secrets["app"]["ADMIN_PASSWORD"]

# ====================== SESSION STATE ======================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.is_admin = False
    st.session_state.df = None          # Will hold the uploaded/default data

# ====================== AUTHENTICATION ======================
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

# ====================== ADMIN UPLOAD (SIDEBAR) ======================
if st.session_state.is_admin:
    with st.sidebar:
        st.header("Admin: Upload New Data")
        uploaded = st.file_uploader(
            "Upload updated Excel file (3 columns only)",
            type=["xlsx", "xls"]
        )

        if uploaded is not None:
            if st.button("Confirm upload & refresh data"):
                with st.spinner("Loading file..."):
                    # This line works with ANY normal CRM export
                    df_new = pd.read_excel(uploaded, usecols=[0,1,2], header=None)
                    df_new.columns = ["Name", "Client Category", "Servicing Advisor"]
                    df_new = df_new.astype(str).apply(lambda x: x.str.strip()).fillna("")

                    # Save to session state
                    st.session_state.df = df_new

                    # SUCCESS MESSAGE — now placed AFTER st.rerun() is safe
                    st.success(f"Successfully loaded {uploaded.name} → {len(df_new)} rows")
                    st.rerun()

# ====================== LOAD DATA ======================
if st.session_state.df is not None:
    df = st.session_state.df.copy()
    source = f"Uploaded file ({len(df)} rows)"
else:
    # Default file that MUST exist in your repo
    df = pd.read_excel("crm_contacts.xlsx", usecols=[0,1,2], header=None)
    df.columns = ["Name", "Client Category", "Servicing Advisor"]
    df = df.astype(str).apply(lambda x: x.str.strip()).fillna("")
    source = f"Default file (crm_contacts.xlsx) – {len(df)} rows"

st.caption(f"Data source: {source}")

# ====================== SEARCH (PERFECTLY WORKING) ======================
st.markdown("### Search by name, category or advisor")
query = st.text_input("", placeholder="Start typing…", label_visibility="collapsed", key="q")

if query:
    q = query.strip()
    # This search line is bullet-proof
    mask = df.astype(str).apply(
        lambda row: row.str.contains(q, case=False, na=False).any(),
        axis=1
    )
    results = df[mask].reset_index(drop=True)

    if len(results) > 0:
        st.dataframe(results, use_container_width=True)
        st.success(f"Found {len(results)} match(es)")
    else:
        st.warning("No results – try a partial name")
else:
    st.info("Type above to begin searching")
    st.dataframe(df.head(20), use_container_width=True)

# ====================== ADMIN TOOLS ======================
if st.session_state.is_admin:
    with st.sidebar:
        st.markdown("---")
        if st.button("Revert to default file"):
            st.session_state.df = None
            st.rerun()
        st.write(f"**Total rows:** {len(df)}")

















