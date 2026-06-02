import streamlit as st
import pandas as pd

st.set_page_config(page_title="Cyclic Voltammetry Analyzer", layout="wide")
st.title("⚡ POTENTIOSTAT ANALYZER — Cyclic Voltammetry Dashboard")

uploaded_file = st.file_uploader("📂 Drag and drop your CV CSV file here", type=["csv"])

if uploaded_file is not None:
    try:
        data = pd.read_csv(uploaded_file)
        potential = data["potential"].values
        current = data["current"].values
        
        st.success(f"📊 Loaded {len(potential)} data points successfully!")
        
        # Display the Voltammogram
        st.subheader("📈 Interactive Voltammogram (I vs E)")
        st.line_chart(data=data, x="potential", y="current")
        
        # Peak Calculations
        max_idx = data["current"].idxmax()
        Ipa = current[max_idx]
        Epa = potential[max_idx]

        min_idx = data["current"].idxmin()
        Ipc = current[min_idx]
        Epc = potential[min_idx]
        
        col1, col2, col3 = st.columns(3)
        delta_Ep = abs(Epa - Epc)
        current_ratio = abs(Ipa / Ipc) if Ipc != 0 else 0
        
        col1.metric("🔴 Anodic Peak (Ipa)", f"{Ipa:.3f} mA", f"{Epa:.2f} V")
        col2.metric("🔵 Cathodic Peak (Ipc)", f"{Ipc:.3f} mA", f"{Epc:.2f} V")
        col3.metric("📏 Peak Separation (ΔEp)", f"{delta_Ep:.2f} V")

        # Interpretation
        st.subheader("🔬 Electrochemical Interpretation")
        if delta_Ep < 0.10 and 0.9 <= current_ratio <= 1.1:
            st.success("Verdict: REVERSIBLE electron transfer (Small ΔEp + Ipa/Ipc ≈ 1.0)")
        elif delta_Ep < 0.20:
            st.warning("Verdict: QUASI-REVERSIBLE electron transfer")
        else:
            st.error("Verdict: IRREVERSIBLE electron transfer (Large ΔEp or unequal peak currents)")
            
    except Exception as e:
        st.error(f"Error: Make sure columns are labeled 'potential' and 'current'. Details: {e}")
else:
    st.info("💡 Waiting for a CV data file...")
