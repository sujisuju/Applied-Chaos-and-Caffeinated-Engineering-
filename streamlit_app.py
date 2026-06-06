import streamlit as st

st.set_page_config(page_title="Ultimate Materials Suite", layout="wide")

# --- MASTER CSS: FIXED SYNTAX & CHEMISTRY DESIGN THEME ---
st.markdown("""
    <style>
    /* Main Landing Page Hero Banner */
    .hero-container {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        padding: 45px;
        border-radius: 20px;
        border: 1px solid #334155;
        border-left: 6px solid #deff9a;
        margin-bottom: 30px;
        position: relative;
        overflow: hidden;
    }
    
    /* Canva-Style Decorative Chemistry Floating Badges */
    .lab-badge {
        position: absolute;
        right: 40px;
        top: 35px;
        font-size: 70px;
        opacity: 0.25;
    }
    
    .hero-title {
        color: #f8fafc;
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 12px;
    }
    .hero-title span {
        color: #deff9a;
    }
    .hero-subtitle {
        color: #cbd5e1;
        font-size: 20px;
    }
    
    /* Dynamic Lab Feature Grid Cards */
    .feature-card {
        background-color: #111827;
        padding: 30px;
        border-radius: 18px;
        border: 1px solid #1e293b;
        height: 100%;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
    }
    .card-icon {
        font-size: 38px;
        margin-bottom: 12px;
    }
    .card-title {
        color: #deff9a;
        font-size: 24px;
        font-weight: 600;
        margin-bottom: 12px;
    }
    .card-desc {
        color: #94a3b8;
        font-size: 15px;
        line-height: 1.6;
    }
    </style>
    """, unsafe_allow_html=True) # <-- TYPO FIXED HERE!

# --- TOP NAVIGATION TABS ---
tab_home, tab_ftir, tab_cv, tab_gcms = st.tabs([
    "🏠 Home Dashboard", 
    "📊 FTIR Spectroscopic Analysis", 
    "⚡ Cyclic Voltammetry", 
    "🧪 GCMS Elution Profile"
])

# ==========================================
# 🏠 TAB 1: STYLIZED CHEMISTRY HOME LAYOUT
# ==========================================
with tab_home:
    # Stylized Hero Block with Floating Chemistry Graphics
    st.markdown("""
        <div class="hero-container">
            <div class="lab-badge">🧪🧪</div>
            <div class="hero-title">Welcome to <span>Applied Chaos & Caffeinated Engineering</span></div>
            <div class="hero-subtitle">The Unified Materials, Energy Storage, and Spectroscopic Digitization Platform</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.write("Select any of the specialized analytical modules above from the top tabs to begin processing your laboratory graph captures.")
    st.markdown("---")
    
    # 3-Column Visual Feature Grid Layout
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div class="feature-card">
                <div class="card-icon">🔮</div>
                <div class="card-title">FTIR Optical Suite</div>
                <div class="card-desc">
                    Leverages computer vision matrix thresholding to isolate infrared baseline curves, 
                    reconstructing physical absorbance data points from flat screenshots.
                </div>
            </div>
            """, unsafe_allow_html=True)
            
    with col2:
        st.markdown("""
            <div class="feature-card">
                <div class="card-icon">⚗️</div>
                <div class="card-title">Voltammetry Sweep Engine</div>
                <div class="card-desc">
                    Maps dynamic faradaic redox curves to calculate potential intervals, isolating 
                    anodic and cathodic sweep interactions directly from instrument captures.
                </div>
            </div>
            """, unsafe_allow_html=True)
            
    with col3:
        st.markdown("""
            <div class="feature-card">
                <div class="card-icon">🧪</div>
                <div class="card-title">GCMS Resolution Hub</div>
                <div class="card-desc">
                    Groups chromatogram retention intervals into descriptive batch zones, evaluating 
                    solvent purity, degradation traces, and macro-structural signatures.
                </div>
            </div>
            """, unsafe_allow_html=True)

# ==========================================
# 📊 TAB 2: FTIR ANALYZER GATEWAY
# ==========================================
with tab_ftir:
    exec(open("Ftir_analyzer.py").read())

# ==========================================
# ⚡ TAB 3: VOLTAMMETRY GATEWAY
# ==========================================
with tab_cv:
    exec(open("cv_analyzer.py").read())

# ==========================================
# 🧪 TAB 4: GCMS GATEWAY
# ==========================================
with tab_gcms:
    exec(open("Gcms_analyzer.py").read())
