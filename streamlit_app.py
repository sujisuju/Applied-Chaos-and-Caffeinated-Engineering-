import streamlit as st
from fpdf import FPDF

st.set_page_config(page_title="Ultimate Materials Suite", layout="wide")

# --- MASTER CSS: DESIGN PLAYGROUND ---
st.markdown("""
    <style>
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
    .hero-title span { color: #deff9a; }
    .hero-subtitle { color: #cbd5e1; font-size: 20px; }
    
    .feature-card {
        background-color: #111827;
        padding: 30px;
        border-radius: 18px;
        border: 1px solid #1e293b;
        height: 100%;
    }
    .card-icon { font-size: 38px; margin-bottom: 12px; }
    .card-title { color: #deff9a; font-size: 24px; font-weight: 600; margin-bottom: 12px; }
    .card-desc { color: #94a3b8; font-size: 15px; line-height: 1.6; }
    </style>
    """, unsafe_allow_html=True)

# --- TOP NAVIGATION TABS ---
tab_home, tab_ftir, tab_cv, tab_gcms = st.tabs([
    "🏠 Home Dashboard", 
    "📊 FTIR Spectroscopic Analysis", 
    "⚡ Cyclic Voltammetry", 
    "🧪 GCMS Elution Profile"
])

# ==========================================
# 🏠 TAB 1: HOME LAYOUT & REPORT GENERATOR
# ==========================================
with tab_home:
    st.markdown("""
        <div class="hero-container">
            <div class="lab-badge">⚗️🧪</div>
            <div class="hero-title">Welcome to <span>Applied Chaos & Caffeinated Engineering</span></div>
            <div class="hero-subtitle">The Unified Materials, Energy Storage, and Spectroscopic Digitization Platform</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.write("Select an analytical module from the top tabs to process your graph captures.")
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="feature-card"><div class="card-icon">🔮</div><div class="card-title">FTIR Optical Suite</div><div class="card-desc">Isolates infrared baseline curves to reconstruct physical absorbance arrays from flat screenshots.</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="feature-card"><div class="card-icon">⚗️</div><div class="card-title">Voltammetry Sweep Engine</div><div class="card-desc">Maps dynamic redox curves to track faradaic oxidation and reduction spikes directly from captures.</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="feature-card"><div class="card-icon">🧪</div><div class="card-title">GCMS Resolution Hub</div><div class="card-desc">Groups chromatogram retention segments into detailed diagnostic zone summaries.</div></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("📑 Export Blank Laboratory Report Templates")
    st.write("Need a professional record for your lab notebook? Generate a clean, formal PDF log frame instantly below:")

  def generate_pdf_report(Ftir_peaks, cv_peaks, Gcms_peaks):
    pdf = FPDF()
    pdf.add_page()
    
    # --- HEADER BLOCK ---
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 12, "Applied Chaos & Caffeinated Engineering", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "I", 11)
    pdf.cell(0, 8, "Official Laboratory Data Suite Verification Report", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.line(10, 32, 200, 32)
    pdf.ln(10)
    
    # --- SECTION 1: EXEC SUMMARY ---
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "1. Computational Data Reconstruction Summary", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 6, "This document certifies the computational data array reconstruction from visual graphical instrumentation sources. The digitization matrix successfully extracted sub-pixel tracking vectors to map localized spectroscopic maxima and thermodynamic peak patterns without manual processing bias.")
    pdf.ln(5)
    
    # --- SECTION 2: FTIR PEAKS ---
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 10, "2. Module I: Resolved FTIR Spectral Peaks", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    for p in ftir_peaks:
        pdf.cell(0, 6, f"- Peak at {p['Wavenumber (cm-1)']} cm-1 | Intensity: {p['Relative Intensity']} | Group: {p['Functional Group Class']}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    
    # --- SECTION 3: CV SWEEP ---
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 10, "3. Module II: Resolved Cyclic Voltammetry Intersections", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    for p in cv_peaks:
        pdf.cell(0, 6, f"- Sweep Point: {p['Potential (V)']} V | Relative Current Density: {p['Relative Intensity']}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    
    # --- SECTION 4: GCMS REPORT ---
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 10, "4. Module III: Resolved GCMS Chromatogram Components", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    for p in gcms_peaks:
        pdf.cell(0, 6, f"- Retention Time: {p['Retention Time (min)']} min | Abundance Height: {p['Relative Abundance Peak Height']}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(10)
    
    # --- SIGN-OFF BLOCK ---
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 6, "Name", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, "Date", new_x="LMARGIN", new_y="NEXT")
    
    return pdf.output()
      
# ==========================================
# 📊 SUB-MODULE TAB EXTENSIONS
# ==========================================
with tab_ftir:
    exec(open("Ftir_analyzer.py").read())

with tab_cv:
    exec(open("cv_analyzer.py").read())

with tab_gcms:
    exec(open("Gcms_analyzer.py").read())
