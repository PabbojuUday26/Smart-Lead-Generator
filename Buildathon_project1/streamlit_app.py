import streamlit as st
import pandas as pd
import os
import time
import concurrent.futures
from dotenv import load_dotenv

load_dotenv()

# Import backend modules
import sys
sys.path.append(os.getcwd())

from github import github_email_finder
from core import csv_manager
from email_engine.llm_client import LLMClient
from email_engine.email_writer import EmailWriter
from mailer import send_email

# --- CONFIGURATION & STYLES ---
st.set_page_config(page_title="Buildathon Outreach AI", layout="wide", initial_sidebar_state="expanded")

# --- CLEANUP ON RELOAD ---
if "app_initialized" not in st.session_state:
    st.session_state.app_initialized = True
    if os.path.exists("data/emails.csv"):
        os.remove("data/emails.csv")

st.markdown("""
<style>
/* ===== VIBRANT PINK-VIOLET THEME ===== */
:root {
    --primary: #c026d3;        /* Vibrant violet */
    --primary-dark: #a21caf;
    --primary-light: #e879f9;
    --accent: #f472b6;         /* Pink accent */
    --accent-dark: #db2777;
    --bg-main: #fdf4ff;        /* Very light pink */
    --bg-card: #ffffff;
    --bg-gradient: linear-gradient(135deg, #fdf4ff 0%, #fce7f3 50%, #f5f3ff 100%);
    --border: #f0abfc;
    --border-light: #fae8ff;
    --text-main: #3f3f46;
    --text-dark: #1f2937;
    --text-muted: #a855f7;
    --shadow: 0 8px 32px rgba(192, 38, 211, 0.15);
    --shadow-hover: 0 16px 48px rgba(192, 38, 211, 0.25);
}
 .stApp {
     background-color: #EFE6FA;
    -primary: #c026d3;        /* Vibrant violet */
    --primary-dark: #a21caf;
    --primary-light: #e879f9;
    --accent: #f472b6;         /* Pink accent */
    --accent-dark: #db2777;
    --bg-main: #fdf4ff;        /* Very light pink */
    --bg-card: #ffffff;
}

/* ===== GLOBAL STYLES ===== */
html, body, [class*="css"] {
    font-family: "Inter", "SF Pro Display", -apple-system, BlinkMacSystemFont, sans-serif;
    color: var(--text-main);
    background: var(--bg-gradient);
}

.main {
    background: var(--bg-gradient);
    padding: 1.5rem;
    
}

/* ===== TYPOGRAPHY ENHANCEMENT ===== */
h1 {
    font-size: 2.8rem;
    font-weight: 800;
    background: linear-gradient(90deg, var(--primary) 0%, var(--accent) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 1.5rem;
    letter-spacing: -0.5px;
}

h2 {
    font-size: 2rem;
    font-weight: 700;
    color: var(--primary-dark);
    border-left: 4px solid var(--accent);
    padding-left: 1rem;
    margin-top: 2rem;
}

h3 {
    font-size: 1.5rem;
    font-weight: 600;
    color: var(--text-muted);
}

p, li {
    line-height: 1.7;
    font-size: 1.05rem;
}

/* ===== SIDEBAR - PINK DREAM ===== */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #4c1d95 0%, #7c3aed 50%, #a855f7 100%);
    border-right: none;
    box-shadow: 8px 0 32px rgba(124, 58, 237, 0.3);
}

section[data-testid="stSidebar"] * {
    color: #faf5ff !important;
    font-weight: 500;
}

section[data-testid="stSidebar"] .st-emotion-cache-16txtl3 h1,
section[data-testid="stSidebar"] .st-emotion-cache-16txtl3 h2,
section[data-testid="stSidebar"] .st-emotion-cache-16txtl3 h3 {
    color: #ffffff !important;
    font-weight: 700;
}

/* ===== INPUT FIELDS - GLASS MORPHISM ===== */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stNumberInput > div > div > input {
    background: rgba(255, 255, 255, 0.9) !important;
    backdrop-filter: blur(10px);
    border-radius: 16px !important;
    border: 2px solid var(--border-light) !important;
    padding: 14px 18px !important;
    font-size: 1rem;
    color: var(--text-dark) !important;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: var(--shadow);
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus,
.stNumberInput > div > div > input:focus {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 4px rgba(192, 38, 211, 0.2), var(--shadow-hover) !important;
    transform: translateY(-2px);
    background: white !important;
}

/* ===== BUTTONS - GRADIENT MAGIC ===== */
.stButton > button {
    background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%);
    color: white;
    border-radius: 16px;
    padding: 0.85rem 2rem;
    font-weight: 700;
    font-size: 1rem;
    border: none;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: var(--shadow);
    position: relative;
    overflow: hidden;
    letter-spacing: 0.5px;
}

.stButton > button:hover {
    transform: translateY(-4px) scale(1.05);
    box-shadow: var(--shadow-hover);
    background: linear-gradient(135deg, var(--primary-dark) 0%, var(--accent-dark) 100%);
}

.stButton > button::after {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
    transition: 0.5s;
}

.stButton > button:hover::after {
    left: 100%;
}

/* ===== METRIC/CARDS - GLASS EFFECT ===== */
div[data-testid="stMetric"] {
    background: rgba(255, 255, 255, 0.85);
    backdrop-filter: blur(12px);
    border-radius: 20px;
    border: 1px solid rgba(244, 114, 182, 0.2);
    padding: 1.5rem;
    box-shadow: var(--shadow);
    transition: all 0.3s ease;
}

div[data-testid="stMetric"]:hover {
    transform: translateY(-5px);
    box-shadow: var(--shadow-hover);
    border-color: var(--accent);
}

/* ===== DATAFRAME - ELEGANT TABLE ===== */
[data-testid="stDataFrame"] {
    border-radius: 20px;
    overflow: hidden;
    border: 1px solid var(--border);
    box-shadow: var(--shadow);
    transition: all 0.4s ease;
}

[data-testid="stDataFrame"]:hover {
    transform: scale(1.02);
    box-shadow: var(--shadow-hover);
}

/* ===== FILE UPLOADER - DASHED GLAM ===== */
section[data-testid="stFileUploader"] {
    border-radius: 20px;
    border: 3px dashed var(--primary-light);
    background: rgba(248, 250, 252, 0.6);
    padding: 2.5rem;
    transition: all 0.4s ease;
    backdrop-filter: blur(8px);
}

section[data-testid="stFileUploader"]:hover {
    background: rgba(232, 121, 249, 0.1);
    border-color: var(--primary);
    transform: scale(1.02);
    box-shadow: var(--shadow);
}

/* ===== EXPANDER - ACCORDION STYLE ===== */
details {
    border-radius: 18px;
    border: 1px solid var(--border);
    background: white;
    padding: 1.5rem;
    transition: all 0.4s ease;
    margin: 1rem 0;
}

details:hover {
    box-shadow: var(--shadow);
    border-color: var(--primary);
}

summary {
    color: var(--primary-dark);
    font-weight: 700;
    font-size: 1.1rem;
    cursor: pointer;
}

/* ===== ALERTS - COLORFUL ===== */
.stAlert {
    border-radius: 16px;
    border: none;
    font-weight: 500;
}

.stAlert[data-baseweb="notification"] {
    border-left: 6px solid var(--primary);
}

/* ===== DIVIDER - GRADIENT ===== */
hr {
    border: none;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--primary), transparent);
    margin: 2.5rem 0;
}

/* ===== SELECTBOX/SLIDER ===== */
.stSelectbox > div > div,
.stSlider > div > div {
    border-radius: 16px;
    border: 2px solid var(--border-light);
}

/* ===== PROGRESS BAR ===== */
.stProgress > div > div > div {
    background: linear-gradient(90deg, var(--primary), var(--accent));
    border-radius: 10px;
}

/* ===== ANIMATIONS ===== */
@keyframes fadeUp {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes shimmer {
    0% { background-position: -1000px 0; }
    100% { background-position: 1000px 0; }
}

.fade-up {
    animation: fadeUp 0.6s ease-out;
}

/* ===== CUSTOM SCROLLBAR ===== */
::-webkit-scrollbar {
    width: 10px;
}

::-webkit-scrollbar-track {
    background: #f5f3ff;
    border-radius: 10px;
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(var(--primary), var(--accent));
    border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(var(--primary-dark), var(--accent-dark));
}

/* ===== TOOLTIPS ===== */
[data-baseweb="tooltip"] {
    border-radius: 12px !important;
    background: var(--primary-dark) !important;
    color: white !important;
    font-weight: 500 !important;
}
</style>
""", unsafe_allow_html=True)

st.title("🚀 Smart Lead")
st.markdown("Find the leads and automate your outreach")

# --- SIDEBAR CONFIG ---
with st.sidebar:
    st.header("⚙️Configuration")
    
    st.subheader("GitHub Settings")
    github_token_input = st.text_input("GitHub Token (Optional)", type="password", help="Leave empty to use default token")
    if github_token_input:
        github_email_finder.GITHUB_TOKEN = github_token_input
        github_email_finder.headers["Authorization"] = f"token {github_token_input}"
        st.success("GitHub Token updated!")

    st.subheader("Email Settings")
    sender_email_input = st.text_input("Your Gmail Address")
    sender_password_input = st.text_input("App Password", type="password")
    
    st.info("Make sure you have an App Password generated from Google Account settings.")

# --- SESSION STATE ---
if "leads" not in st.session_state:
    st.session_state.leads = []
if "generated_emails" not in st.session_state:
    st.session_state.generated_emails = {}

# --- MAIN INTERFACE ---

# 1. INPUTS
st.subheader("1. Campaign Details")

product_name = st.text_input("Product Name", placeholder="e.g. CodeFlow AI")
product_desc = st.text_area("Product Description", placeholder="Briefly describe what your product does...", height=100)
target_audience = st.text_input("Target Audience (GitHub Search Query)", placeholder="e.g. Python Developer, Machine Learning Engineer")
max_results = st.number_input("Max Leads to Find", min_value=1, max_value=200, value=10)

if "search_page_start" not in st.session_state:
    st.session_state.search_page_start = 1
if "last_query" not in st.session_state:
    st.session_state.last_query = ""

import random

# ... (imports are fine, just ensuring random is available if not already)

# 2. SEARCH FUNCTIONALITY
if st.button("Search", type="primary"):
    if not target_audience:
        st.error("Please enter a Target Audience to search for.")
    else:
        # Check if query changed
        if target_audience != st.session_state.last_query:
            st.session_state.search_page_start = 1
            st.session_state.last_query = target_audience
            
        # Parse queries
        queries = [q.strip() for q in target_audience.split(",") if q.strip()]
        
        # Distribute quotas
        quotas = []
        if len(queries) == 1:
            quotas = [max_results]
        else:
            # Random distribution logic
            # Generate random weights
            weights = [random.random() for _ in range(len(queries))]
            total_weight = sum(weights)
            # Normalize to max_results (ints)
            current_sum = 0
            for w in weights[:-1]:
                count = int((w / total_weight) * max_results)
                quotas.append(max(1, count)) # Ensure at least 1 if possible
                current_sum += max(1, count)
            # Assign remainder to last one
            quotas.append(max(1, max_results - current_sum))
        
        # Load history
        if os.path.exists("data/history.csv"):
            try:
                history_df = pd.read_csv("data/history.csv")
                if not history_df.empty:
                    existing_emails = set(history_df["email"].tolist())
                    existing_usernames = set(history_df["username"].tolist())
                else:
                     existing_emails = set()
                     existing_usernames = set()
            except Exception:
                existing_emails = set()
                existing_usernames = set()
        else:
            existing_emails = set()
            existing_usernames = set()
            
        with st.status(f"Searching GitHub...", expanded=True) as status:
            try:
                found_leads = []
                
                # Iterate over each query with its assigned quota
                for q_idx, query in enumerate(queries):
                    quota = quotas[q_idx]
                    status.write(f"Searching for '{query}' (Target: {quota} leads)...")
                    
                    page = st.session_state.search_page_start
                    leads_for_this_query = 0
                    max_pages_limit = page + 50 
                    
                    while leads_for_this_query < quota and page <= max_pages_limit:
                        status.write(f"Scanning '{query}' page {page}...")
                        users = github_email_finder.search_users(query=query, max_results=30, page=page)
                        
                        if not users:
                            break 
                        
                        users_to_check = []
                        for user in users:
                            username = user["login"]
                            if username not in existing_usernames:
                                users_to_check.append(username)
                        
                        if not users_to_check:
                             page += 1
                             time.sleep(0.5)
                             continue
                             
                        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                            future_to_user = {executor.submit(github_email_finder.get_public_email, u): u for u in users_to_check}
                            
                            for future in concurrent.futures.as_completed(future_to_user):
                                if leads_for_this_query >= quota:
                                    break
                                    
                                username = future_to_user[future]
                                try:
                                    email = future.result()
                                    if email:
                                        if email not in existing_emails:
                                            lead_obj = {"username": username, "email": email, "query": query}
                                            found_leads.append(lead_obj)
                                            leads_for_this_query += 1
                                            
                                            result_msg = f"Found: {username} ({email}) [{query}]"
                                            status.write(result_msg)
            
                                            existing_emails.add(email) 
                                            existing_usernames.add(username)
                                except Exception:
                                    pass
                        
                        page += 1
                        time.sleep(0.5)

                status.update(label=f"Search complete! Found {len(found_leads)} total leads.", state="complete", expanded=False)
                
                # Advance pagination for next time (simple global increment)
                st.session_state.search_page_start += 6
                
                st.session_state.leads = found_leads
                
                if found_leads:
                    # Save to CSV
                    df = pd.DataFrame(found_leads) # Now includes 'query' column which is nice
                    if not os.path.exists("data"):
                        os.makedirs("data")
                    df.to_csv("data/emails.csv", index=False)
                    
                    # Append to History (map columns safely if history structure is fixed)
                    # History expects username, email. We can just save filtered cols or expand history ? 
                    # Previous history just had username,email. Let's keep it compatible.
                    history_entry = df[["username", "email"]]
                    
                    if os.path.exists("data/history.csv"):
                         history_entry.to_csv("data/history.csv", mode='a', header=False, index=False)
                    else:
                         history_entry.to_csv("data/history.csv", index=False) # this will write header
                        
                else:
                     st.warning("No new unique emails found.")
                     
            except Exception as e:
                status.update(label="Search failed!", state="error")
                st.error(f"Search failed: {e}")
                
                if found_leads:
                    # Save to CSV (Current Batch)
                    df = pd.DataFrame(found_leads)
                    if not os.path.exists("data"):
                        os.makedirs("data")
                    df.to_csv("data/emails.csv", index=False)
                    
                    # Append to History
                    if os.path.exists("data/history.csv"):
                        df.to_csv("data/history.csv", mode='a', header=False, index=False)
                    else:
                        df.to_csv("data/history.csv", index=False)
                        
                else:
                    st.warning("No new unique emails found. Try a different query or wait a while.")
                    
            except Exception as e:
                status.update(label="Search failed!", state="error")
                st.error(f"Search failed: {e}")

# 3. DISPLAY RESULTS & SEND EMAILS
st.divider()

if os.path.exists("data/emails.csv"):
    try:
        df = pd.read_csv("data/emails.csv")
        st.session_state.leads = df.to_dict('records')
    except:
        df = pd.DataFrame()

if st.session_state.leads and not df.empty:
    st.subheader("2. Leads & Outreach")
    
    col_res, col_btn = st.columns([3, 1])
    
    with col_res:
         # Add selection column for deletion
         if "Select" not in df.columns:
             df.insert(0, "Select", False)
         
         edited_df = st.data_editor(
             df,
             column_config={
                 "Select": st.column_config.CheckboxColumn("Select", help="Select to delete", default=False)
             },
             disabled=df.columns.drop("Select"),
             hide_index=True,
             use_container_width=True,
             key="leads_editor"
         )
         
         if st.button("Delete Selected", type="secondary"):
             # Filter out selected rows
             selected_rows = edited_df[edited_df["Select"]]
             if not selected_rows.empty:
                 new_df = edited_df[~edited_df["Select"]].drop(columns=["Select"])
                 
                 # Save updates
                 new_df.to_csv("data/emails.csv", index=False)
                 st.session_state.leads = new_df.to_dict('records')
                 st.success(f"Deleted {len(selected_rows)} leads.")
                 st.rerun()
             else:
                 st.warning("Select rows to delete first.")
    
    with col_btn:
        pdf_attachment = st.file_uploader("Attach PDF (Optional)", type=["pdf"], key="pdf_uploader")
        attached_link = st.text_input("Attach Link (Optional)", placeholder="https://yourlink.com")
        send_btn = st.button("Send Emails", type="primary")

    if send_btn:
        hf_api_key = os.getenv("HUGGINGFACE_API_KEY")
        if not product_name or not product_desc:
            st.error("Please fill in Product Name and Description above first.")
        elif not sender_email_input or not sender_password_input:
            st.error("Please configure Email Settings in the sidebar first.")
        elif not hf_api_key:
            st.error("HuggingFace API Key not found. Please add HUGGINGFACE_API_KEY to your .env file.")
        else:
            # Handle Attachment
            temp_pdf_path = None
            if pdf_attachment:
                with open("temp_attachment.pdf", "wb") as f:
                    f.write(pdf_attachment.getbuffer())
                temp_pdf_path = os.path.abspath("temp_attachment.pdf")

            try:
                # Initialize LLM only when needed
                status_container = st.status("Starting outreach campaign...", expanded=True)
                llm = LLMClient(api_key=hf_api_key)
                writer = EmailWriter(llm)
                
                total_leads = len(st.session_state.leads)
                
                for i, lead in enumerate(st.session_state.leads):
                    username = lead['username']
                    email = lead['email']
                    # Use lead-specific query if available (for multi-target), else fallback to main input
                    lead_audience = lead.get('query', target_audience)
                    
                    status_container.write(f"**[{i+1}/{total_leads}]** Processing {username}...")
                    
                    # 1. Generate Email
                    status_container.write(f"   Generating email for {username}...")
                    email_body = writer.write_email(
                        name=username,
                        product=product_name,
                        description=product_desc,
                        target_audience=lead_audience
                    )
                    
                    # 2. Send Email
                    status_container.write(f"   Sending email to {email}...")
                    try:
                        send_email.send_email(
                            sender=sender_email_input,
                            app_password=sender_password_input,
                            receiver=email,
                            subject=f"Opportunity regarding {product_name}", 
                            body=email_body,
                            attachment_path=temp_pdf_path,
                            link=attached_link
                        )
                        status_container.write(f"   ✅ Sent successfully!")
                    except Exception as e:
                        status_container.write(f"   ❌ Failed to send: {e}")
                    
                status_container.update(label="Campaign Finished!", state="complete", expanded=False)
                st.success("All emails processed!")
                
                # Cleanup temp file
                if temp_pdf_path and os.path.exists(temp_pdf_path):
                    os.remove(temp_pdf_path)
                
            except Exception as e:
                st.error(f"Error executing campaign: {e}")
    
    # --- MANUAL ADD LEAD ---
    with st.expander("➕ Manually Add Lead"):
        with st.form("add_lead_form"):
            new_username = st.text_input("Username/Name")
            new_email = st.text_input("Email Address")
            new_query = st.text_input("Target Audience (Query)", value=target_audience)
            submitted = st.form_submit_button("Add Lead", type="primary")
            
            if submitted:
                if new_username and new_email and new_query:
                    new_lead = {"username": new_username, "email": new_email, "query": new_query}
                    
                    # Updates Session State
                    st.session_state.leads.append(new_lead)
                    
                    # Update CSVs
                    df_new = pd.DataFrame([new_lead])
                    
                    # emails.csv
                    if os.path.exists("data/emails.csv"):
                         df_new.to_csv("data/emails.csv", mode='a', header=False, index=False)
                    else:
                         df_new.to_csv("data/emails.csv", index=False)
                    
                    # history.csv
                    hist_entry = df_new[["username", "email"]]
                    if os.path.exists("data/history.csv"):
                         hist_entry.to_csv("data/history.csv", mode='a', header=False, index=False)
                    else:
                         hist_entry.to_csv("data/history.csv", index=False)
                    
                    st.success(f"Added {new_username} to the list!")
                    st.rerun()
                else:
                    st.error("Please fill all fields.")

else:
    st.info("No leads found yet. Use the search button above.")
