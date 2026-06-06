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
    st.subheader("📑 Export Full Laboratory Report Templates")
    st.write("Generate a clean, formal PDF log frame instantly below:")

    # Fixed Indentation: Exactly 4 spaces from the left margin
    def generate_pdf_report():
        pdf = FPDF()
        pdf.add_page()
        
        # Header block
        pdf.set_font("Helvetica", "B", 18)
        pdf.cell(0, 15, "Applied Chaos & Caffeinated Engineering", align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "I", 12)
        pdf.cell(0, 10, "Official Laboratory Analytical Verification Report", align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.line(10, 40, 200, 40)
        pdf.ln(15)
        
        # Section 1
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 10, "1. Executive Material Diagnostics Summary", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 11)
        pdf.multi_cell(0, 7, "This document certifies the computational data array reconstruction from visual graphical instrumentation sources. The digitization matrix successfully extracted the sub-pixel tracking vectors to map localized spectroscopic maxima and thermodynamic peak trends.")
        pdf.ln(10)
        
        # Section 2
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 10, "2. Operational Parameters & Verification Sign-Off", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(0, 8, "- Name: _______________________", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 8, "- Date", new_x="LMARGIN", new_y="NEXT")
        
        return pdf.output()

    # Create report data stream
    pdf_string = generate_pdf_report()
    pdf_bytes = bytes(pdf_string)
    
    st.download_button(
        label="📥 Download Laboratory Report Sheet (PDF)",
        data=pdf_bytes,
        file_name="materials_suite_lab_report.pdf",
        mime="application/pdf"
    )

# ==========================================
# 📊 SUB-MODULE TAB EXTENSIONS
# ==========================================
with tab_ftir:
    exec(open("Ftir_analyzer.py").read())

with tab_cv:
    exec(open("cv_analyzer.py").read())

with tab_gcms:
    exec(open("Gcms_analyzer.py").read())
