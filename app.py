# app.py
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Client Lookup", layout="wide")

# ========================= SECRETS =========================
ACCESS_PASSWORD = st.secrets["app"]["ACCESS_PASSWORD"]
ADMIN_PASSWORD  = st.secrets["app"]["ADMIN_PASSWORD"]

# ========================= SESSION STATE =========================
defaults = {
    "authenticated": False,
    "is_admin": False,
    "df": None,
    "data_source": "Default file"
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

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
        uploaded = st.file_uploader("Upload new CRM Excel (3 columns)", type=["xlsx", "xls"])

        if uploaded and st.button("Confirm Upload & Update Data", type="primary"):
            with st.spinner("Processing file..."):
                try:
                    df_new = pd.read_excel(uploaded, usecols=[0,1,2], header=None)
                    df_new.columns = ["Name", "Client Category", "Servicing Advisor"]
                    df_new = df_new.astype(str).apply(lambda x: x.str.strip()).replace("nan", "")
                    
                    st.session_state.df = df_new
                    st.session_state.data_source = f"Uploaded: {uploaded.name} ({len(df_new)} rows)"
                    st.success("Data updated successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

# ========================= LOAD DATA =========================
if st.session_state.df is not None:
    df = st.session_state.df.copy()
else:
    df = pd.read_excel("crm_contacts.xlsx", usecols=[0,1,2], header=None)
    df.columns = ["Name", "Client Category", "Servicing Advisor"]
    df = df.astype(str).apply(lambda x: x.str.strip()).replace("nan", "")
    st.session_state.data_source = f"Default file ({len(df)} rows)"

# ========================= MAIN APP UI =========================
st.title("Firmwide Client & Prospect Lookup")
st.caption(f"Data source: {st.session_state.data_source}")

st.markdown("### Search by name, category, or advisor")
query = st.text_input(
    "",
    placeholder="Start typing to search…",
    label_visibility="collapsed",
    key="search_query"
)

# Convert everything to string once
df_str = df.astype(str)

if query:
    q = query.strip().lower()
    # Search in any column
    mask = df_str.apply(lambda col: col.str.lower().str.contains(q, na=False)).any(axis=1)
    results = df[mask].reset_index(drop=True)
    
    if len(results) > 0:
        st.dataframe(results, use_container_width=True)
        st.success(f"Found {len(results)} result(s)")
    else:
        st.warning("No matches found. Try a partial name.")
else:
    st.info("Start typing above to search the client database")
    # Optional: show small preview
    # st.dataframe(df.head(10), use_container_width=True)

# ========================= ADMIN TOOLS =========================
if st.session_state.is_admin:
    with st.sidebar:
        st.markdown("---")
        if st.button("Revert to default file"):
            st.session_state.df = None
            st.session_state.data_source = "Default file"
            st.rerun()
        st.write(f"**Total records:** {len(df)}")


















