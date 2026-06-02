import streamlit as st

st.set_page_config(page_title="Ultimate Materials Suite", layout="wide")

# --- CUSTOM DESIGN: BEAUTIFUL APPLIED CHEMISTRY BUTTONS ---
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        height: 120px;
        font-size: 24px;
        font-weight: bold;
        border-radius: 15px;
        background-color: #deff9a;
        color: black;
        border: 2px solid #cbd5e1;
        transition: transform 0.2s;
    }
    .stButton>button:hover {
        transform: scale(1.02);
        background-color: #c5f07b;
        border-color: #deff9a;
    }
    </style>
    """, unsafe_allow_html=True)

# --- NAVIGATION SIDEBAR ---
st.sidebar.title("🔬 Master Control Panel")
choice = st.sidebar.radio("Go to Analysis Module:", ["🏠 Home Dashboard", "📊 FTIR Analysis", "⚡ Cyclic Voltammetry", "🧪 GCMS Analysis"])

# --- CORE APP DISPATCH LOGIC ---
if choice == "🏠 Home Dashboard":
    st.title("🌟 Applied Chaos & Caffeinated Engineering")
    st.subheader("Unified Computational Materials Architecture")
    st.write("Welcome, researcher. Select a localized analysis sub-engine below or from the sidebar to digitize, process, and interpret raw visual spectra.")
    st.write("---")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### Module 01")
        if st.button("📊 FTIR ANALYSIS"):
            st.info("Directing to FTIR Matrix Digitizer via Sidebar...")
            
    with col2:
        st.markdown("### Module 02")
        if st.button("⚡ VOLTAMMETRY"):
            st.success("Directing to Redox Engine via Sidebar...")
            
    with col3:
        st.markdown("### Module 03")
        if st.button("🧪 GCMS ANALYSIS"):
            st.warning("Directing to GCMS Tracker via Sidebar...")

elif choice == "📊 FTIR Analysis":
    try:
        exec(open("Ftir_analyzer.py").read())
    except FileNotFoundError:
        st.error("Execution Failure: 'Ftir_analyzer.py' could not be located in your cloud repository storage.")

elif choice == "⚡ Cyclic Voltammetry":
    try:
        exec(open("cv_analyzer.py").read())
    except FileNotFoundError:
        st.error("Execution Failure: 'cv_analyzer.py' could not be located in your cloud repository storage.")

elif choice == "🧪 GCMS Analysis":
    try:
        exec(open("gcms_analyzer.py").read())
    except FileNotFoundError:
        st.error("Execution Failure: 'gcms_analyzer.py' could not be located in your cloud repository storage.")
