import streamlit as st
import mysql.connector
import requests
import os
import time
from datetime import datetime

# Config
API_URL = os.getenv("API_URL", "http://api:5000")
DB_HOST = "mysql"

# Page config
st.set_page_config(
    page_title="OpsMind V7 | IT Operations Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional CSS with your color palette
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Dark professional background */
    .main {
        background-color: #1A1A2E;
    }
    
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Header styling */
    h1 {
        color: #F9F9F9;
        font-weight: 700;
        font-size: 2.5rem !important;
        letter-spacing: -0.02em;
        margin-bottom: 2rem !important;
    }
    
    h2, h3 {
        color: #E94560;
        font-weight: 600;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #16213E;
        border-right: 1px solid #0F3460;
    }
    
    [data-testid="stSidebar"] * {
        color: #F9F9F9 !important;
    }
    
    [data-testid="stSidebar"] hr {
        border-color: #0F3460;
    }
    
    /* Metrics styling */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: #E94560;
    }
    
    [data-testid="stMetricLabel"] {
        color: #F9F9F9 !important;
        font-weight: 500;
    }
    
    /* Status cards */
    .status-operational {
        background: linear-gradient(135deg, #0F3460 0%, #16213E 100%);
        color: #F9F9F9;
        padding: 1.5rem 2rem;
        border-radius: 12px;
        font-size: 1.25rem;
        font-weight: 600;
        text-align: center;
        border: 1px solid #0F3460;
        box-shadow: 0 4px 20px rgba(15, 52, 96, 0.3);
    }
    
    .status-alert {
        background: linear-gradient(135deg, #E94560 0%, #C7365F 100%);
        color: #F9F9F9;
        padding: 1.5rem 2rem;
        border-radius: 12px;
        font-size: 1.25rem;
        font-weight: 600;
        text-align: center;
        border: 1px solid #E94560;
        box-shadow: 0 4px 20px rgba(233, 69, 96, 0.4);
    }
    
    /* Ticket card styling */
    .ticket-card {
        background: #16213E;
        border: 1px solid #0F3460;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        border-left: 4px solid #E94560;
        transition: all 0.3s ease;
    }
    
    .ticket-card:hover {
        border-left-width: 6px;
        box-shadow: 0 8px 30px rgba(233, 69, 96, 0.2);
    }
    
    /* Button styling */
    .stButton>button {
        background: linear-gradient(135deg, #E94560 0%, #C7365F 100%);
        color: #F9F9F9;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        font-size: 0.95rem;
        letter-spacing: 0.02em;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(233, 69, 96, 0.3);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 25px rgba(233, 69, 96, 0.5);
    }
    
    /* Code blocks */
    .stCodeBlock {
        background: #0F3460 !important;
        border-radius: 8px;
        border: 1px solid #16213E;
    }
    
    code {
        color: #F9F9F9 !important;
        background: #0F3460 !important;
    }
    
    /* Info boxes */
    .stAlert {
        background: #16213E;
        border: 1px solid #0F3460;
        border-radius: 8px;
        color: #F9F9F9;
    }
    
    /* Toggle switch */
    .stCheckbox {
        color: #F9F9F9 !important;
    }
    
    /* Divider */
    hr {
        border-color: #0F3460;
        margin: 2rem 0;
    }
    
    /* Badge styling */
    .severity-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        background: #E94560;
        color: #F9F9F9;
    }
    
    .ticket-header {
        color: #E94560;
        font-weight: 700;
        font-size: 1.5rem;
        margin-bottom: 0.5rem;
    }
    
    .section-header {
        color: #E94560;
        font-weight: 600;
        font-size: 1.1rem;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("## ⚙️ Control Panel")
    st.markdown("---")
    
    # Stats
    try:
        conn = mysql.connector.connect(host=DB_HOST, user="root", password="TuanBulut2019", database="IT_Support_Bot")
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT COUNT(*) as total FROM incidents")
        total_tickets = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as completed FROM incidents WHERE status='COMPLETED'")
        completed = cursor.fetchone()['completed']
        
        cursor.execute("SELECT COUNT(*) as pending FROM incidents WHERE status='AWAITING_APPROVAL'")
        pending = cursor.fetchone()['pending']
        
        conn.close()
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total", total_tickets)
        col2.metric("Resolved", completed)
        col3.metric("Pending", pending)
        
    except:
        st.error("⚠️ Database Offline")
    
    st.markdown("---")
    st.markdown("### Settings")
    auto_refresh = st.toggle("Auto-Refresh", value=True)
    refresh_rate = st.slider("Refresh Rate (s)", 1, 10, 2)
    
    st.markdown("---")
    if st.button("🔄 Manual Refresh", use_container_width=True):
        st.rerun()
    
    st.markdown("---")
    st.markdown("### System Status")
    st.markdown(f"**Time:** {datetime.now().strftime('%H:%M:%S')}")
    st.markdown(f"**Date:** {datetime.now().strftime('%Y-%m-%d')}")

# Main Title
st.markdown("<h1>🛡️ OpsMind V7 | IT Operations Dashboard</h1>", unsafe_allow_html=True)

# Track hidden tickets
if 'hidden_tickets' not in st.session_state:
    st.session_state.hidden_tickets = set()

# Approval handler
def approve_ticket(ticket_id):
    try:
        response = requests.post(f"{API_URL}/approve_fix/{ticket_id}", timeout=5)
        if response.status_code == 200:
            st.session_state.hidden_tickets.add(ticket_id)
            st.success(f"✅ Ticket #{ticket_id} approved and executed")
            time.sleep(1)
            st.rerun()
        else:
            st.error(f"❌ Failed: {response.status_code}")
    except Exception as e:
        st.error(f"❌ API Error: {e}")

# Auto-refresh dashboard
@st.fragment(run_every=f"{refresh_rate}s" if auto_refresh else None)
def show_dashboard():
    # Fetch pending tickets
    try:
        conn = mysql.connector.connect(host=DB_HOST, user="root", password="TuanBulut2019", database="IT_Support_Bot")
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM incidents WHERE status='AWAITING_APPROVAL' ORDER BY id DESC")
        incidents = cursor.fetchall()
        conn.close()
    except Exception as e:
        st.error(f"🔴 Database Error: {e}")
        incidents = []
    
    # Filter hidden tickets
    incidents = [inc for inc in incidents if inc['id'] not in st.session_state.hidden_tickets]
    
    # Cleanup hidden tickets
    all_db_ids = {inc['id'] for inc in incidents}
    st.session_state.hidden_tickets = st.session_state.hidden_tickets & all_db_ids
    
    # Status display
    if not incidents:
        st.markdown(f"""
        <div class="status-operational">
            ✅ All Systems Operational
            <br>
            <small style="opacity: 0.8;">Last Scan: {time.strftime('%H:%M:%S')}</small>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="status-alert">
            🚨 ACTION REQUIRED: {len(incidents)} Pending Ticket(s)
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Display tickets
        for row in incidents:
            st.markdown('<div class="ticket-card">', unsafe_allow_html=True)
            
            col1, col2 = st.columns([1, 3])
            
            with col1:
                st.markdown(f'<div class="ticket-header">Ticket #{row["id"]}</div>', unsafe_allow_html=True)
                st.markdown(f"**Server:** `{row['server_name']}`")
                st.markdown(f'<span class="severity-badge">{row["severity"]}</span>', unsafe_allow_html=True)
                st.markdown("")
                if st.button("Approve & Execute", key=f"approve_{row['id']}", use_container_width=True):
                    approve_ticket(row['id'])
            
            with col2:
                st.markdown('<div class="section-header">Error Details</div>', unsafe_allow_html=True)
                st.code(row['error_msg'], language=None)
                
                st.markdown('<div class="section-header">AI Recommended Fix</div>', unsafe_allow_html=True)
                ai_fix = row['ai_fix']
                if len(ai_fix) <= 150:
                    st.code(ai_fix, language="bash")
                else:
                    st.code(ai_fix[:150] + "...", language="bash")
            
            st.markdown('</div>', unsafe_allow_html=True)

# Run dashboard
show_dashboard()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #F9F9F9; opacity: 0.6; padding: 1rem;'>
    <strong>OpsMind V7</strong> | Enterprise IT Operations Platform
</div>
""", unsafe_allow_html=True)