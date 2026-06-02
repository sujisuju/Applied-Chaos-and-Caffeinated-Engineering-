import streamlit as st
import pandas as pd

# Set up a beautiful web layout
st.set_page_config(page_title="FTIR Spectroscopic Analyzer", layout="wide")

st.title("🔬 FTIR Spectrum Functional Group Analyzer")
st.write("Upload a spectrum text/CSV file with 'wavenumber' and 'absorbance' columns to begin.")

# 1. File Uploader Component
uploaded_file = st.file_uploader("📂 Drag and drop your FTIR CSV file here", type=["csv"])

if uploaded_file is not None:
    try:
        # 2. Read the uploaded file into Pandas
        data = pd.read_csv(uploaded_file)
        
        # Ensure column names match expected formats
        wavenumber = data["wavenumber"].values
        absorbance = data["absorbance"].values
        
        st.success(f"Successfully loaded {len(wavenumber)} data points!")
        
        # 3. Display the raw data plot dynamically
        st.subheader("📈 Interactive Spectral Data Plot")
        st.line_chart(data=data, x="wavenumber", y="absorbance")
        
        # 4. Global Maximum Detection
        max_idx = data["absorbance"].idxmax()
        max_abs = absorbance[max_idx]
        max_wn = wavenumber[max_idx]
        
        st.metric(label="Global Maximum Peak", value=f"{max_abs:.3f} Abs", delta=f"{max_wn:.1f} cm⁻¹")
        
        # 5. Core Chemistry Logic: Carbonyl Detection Example
        st.subheader("🔬 Chemical Interpretation")
        
        carbonyl_absorbances = [absorbance[i] for i in range(len(wavenumber)) if 1650 <= wavenumber[i] <= 1800]
        
        if carbonyl_absorbances and max(carbonyl_absorbances) > 0.05:
            st.success("✅ Carbonyl (C=O) Stretch DETECTED in the 1650–1800 cm⁻¹ region!")
        else:
            st.info("❌ No significant carbonyl peak detected in the standard region.")
            
    except Exception as e:
        st.error(f"Error parsing file: {e}. Please ensure columns are labeled exactly 'wavenumber' and 'absorbance'.")
else:
    st.info("💡 Waiting for a file to be uploaded. Drag one in to run the calculator!")
