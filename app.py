import streamlit as st
import pandas as pd
import io

# -------------------------
# CONFIG
# -------------------------

st.set_page_config(page_title="Client Lookup", layout="wide")

SHARED_FILE = "crm_contacts.xlsx"   # Your shared Excel filename

# -------------------------
# SESSION STATE SETUP
# -------------------------

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if "is_admin" not in st.session_state:
    st.session_state["is_admin"] = False

# Handle safe rerun after admin upload
if st.session_state.get("force_reload", False):
    st.session_state["force_reload"] = False
    st.experimental_rerun()

# -------------------------
# AUTHENTICATION
# -------------------------

def login_screen():
    st.sidebar.header("🔒 Login Required")

    user_password = st.sidebar.text_input("Enter Password", type="password")

    if st.sidebar.button("Login"):
        shared_pw = st.secrets["general_password"]
        admin_pw = st.secrets["admin_password"]

        if user_password == shared_pw:
            st.session_state["authenticated"] = True
            st.session_state["is_admin"] = False
            st.sidebar.success("Logged in!")
        elif user_password == admin_pw:
            st.session_state["authenticated"] = True
            st.session_state["is_admin"] = True
            st.sidebar.success("Logged in as Admin!")
        else:
            st.sidebar.error("Incorrect password")

    st.stop()


# If not authenticated → show login
if not st.session_state["authenticated"]:
    login_screen()

# -------------------------
# LOAD EXCEL DATA
# -------------------------

def load_data():
    try:
        return pd.read_excel(SHARED_FILE)
    except Exception as e:
        st.error("Unable to load Excel file.")
        st.stop()

df = load_data()

# -------------------------
# ADMIN UPLOAD SECTION
# -------------------------

if st.session_state["is_admin"]:
    st.sidebar.markdown("---")
    st.sidebar.header("🛠 Admin Controls")

    uploaded_file = st.sidebar.file_uploader(
        "Upload Updated Excel File",
        type=["xlsx"],
        key="admin_upload"
    )

    if uploaded_file is not None:
        with open(SHARED_FILE, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.sidebar.success("File updated for all users!")

        if st.sidebar.button("Reload App"):
            st.session_state["force_reload"] = True
            st.experimental_rerun()

# -------------------------
# MAIN SEARCH UI
# -------------------------

st.title("🔍 Client Lookup Tool")

search_query = st.text_input("Search by Client Name")

if search_query:
    results = df[df.apply(lambda row: search_query.lower() in row.astype(str).str.lower().to_string(), axis=1)]
    st.write(f"### Results ({len(results)})")
    st.dataframe(results, use_container_width=True)
else:
    st.write("Type a name above to search the client directory.")










