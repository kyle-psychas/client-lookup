import streamlit as st
import pandas as pd
import os

# --- Page config ---
st.set_page_config(page_title="Client Lookup", layout="wide")

# --- Load passwords from Streamlit Secrets ---
ACCESS_PASSWORD = st.secrets["app"]["ACCESS_PASSWORD"]
ADMIN_PASSWORD = st.secrets["app"]["ADMIN_PASSWORD"]

# --- Constants ---
DATA_FILE = "shared_crm_contacts.xlsx"
FALLBACK_FILE = "crm_contacts.xlsx"

# --- Initialize session state ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.is_admin = False

if "df_data" not in st.session_state:
    st.session_state.df_data = None

# --- PASSWORD CHECK ---
if not st.session_state.authenticated:
    password = st.text_input("Enter password to access the app:", type="password")
    
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
    elif password:
        st.error("Incorrect password")
    else:
        st.warning("Enter the correct password to continue")
    st.stop()

# --- Load data function ---
def load_data():
    """Load data from file or fallback"""
    try:
        if os.path.exists(DATA_FILE):
            return pd.read_excel(
                DATA_FILE, 
                usecols="A:C", 
                names=["Name", "Client Category", "Servicing Advisor"]
            )
        elif os.path.exists(FALLBACK_FILE):
            return pd.read_excel(
                FALLBACK_FILE, 
                usecols="A:C", 
                names=["Name", "Client Category", "Servicing Advisor"]
            )
        else:
            st.error("No data file found. Please upload a file.")
            return pd.DataFrame(columns=["Name", "Client Category", "Servicing Advisor"])
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame(columns=["Name", "Client Category", "Servicing Advisor"])

# --- Load data once ---
if st.session_state.df_data is None:
    st.session_state.df_data = load_data()

# --- App title ---
st.title("Firmwide Client & Prospect Lookup")

# --- Admin upload sidebar ---
if st.session_state.is_admin:
    st.sidebar.header("📤 Admin Update")
    st.sidebar.write("Upload a new Excel file to update the client list for all users.")
    
    uploaded = st.sidebar.file_uploader(
        "Upload latest CRM file", 
        type=["xlsx", "xls"],
        help="File should have 3 columns: Name, Client Category, Servicing Advisor"
    )
    
    if uploaded:
        try:
            # Read the uploaded file
            new_df = pd.read_excel(
                uploaded, 
                usecols="A:C", 
                names=["Name", "Client Category", "Servicing Advisor"]
            )
            
            # Validate the data
            if new_df.empty:
                st.sidebar.error("Uploaded file is empty!")
            elif len(new_df.columns) != 3:
                st.sidebar.error("File must have exactly 3 columns")
            else:
                # Save to disk
                new_df.to_excel(DATA_FILE, index=False)
                
                # Update session state
                st.session_state.df_data = new_df
                
                st.sidebar.success(f"✅ Updated! {len(new_df)} records loaded.")
                st.sidebar.info("All users now have access to the updated list.")
                
        except Exception as e:
            st.sidebar.error(f"Error processing file: {str(e)}")
            st.sidebar.info("Make sure the file has 3 columns in order: Name, Client Category, Servicing Advisor")

# --- Get current data ---
df = st.session_state.df_data

# --- Search interface ---
st.write("#### Search by name, category, or advisor")
query = st.text_input(
    "search_input",
    placeholder="Start typing…", 
    label_visibility="collapsed"
)

if query:
    # Filter data based on query
    results = df[
        df.apply(
            lambda row: row.astype(str).str.contains(query, case=False, na=False).any(), 
            axis=1
        )
    ]
    
    if len(results) > 0:
        st.dataframe(results, use_container_width=True)
        st.write(f"**{len(results)}** result(s) found")
    else:
        st.warning(f"No results found for '{query}'")
else:
    st.info("💡 Type to search the client list")
    
    # Show data stats
    if not df.empty:
        st.write(f"**Total records:** {len(df)}")





















