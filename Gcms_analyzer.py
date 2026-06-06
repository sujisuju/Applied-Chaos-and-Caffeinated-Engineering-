import streamlit as st
import cv2
import numpy as np
import pandas as pd

st.title("🧪 Advanced GCMS Chromatogram Digitizer & Interpreter")
st.write("Extract numerical data arrays from visual chromatograms and generate automated diagnostic summaries.")

uploaded_image = st.file_uploader("📂 Upload GCMS Graph Image (.png, .jpg, .jpeg, .webp)", type=["png", "jpg", "jpeg", "webp"])

if uploaded_image is not None:
    file_bytes = np.asarray(bytearray(uploaded_image.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    h_img, w_img, _ = img.shape

    # --- SIDEBAR TUNING ---
    st.sidebar.header("🎛️ Chromatogram Scaling")
    crop_left = st.sidebar.slider("Crop Left Margin (Cut Y-Axis Text)", 0, 50, 10)
    crop_right = st.sidebar.slider("Crop Right Margin", 0, 50, 5)
    crop_top = st.sidebar.slider("Crop Top Margin", 0, 50, 5)
    crop_bottom = st.sidebar.slider("Crop Bottom Margin (Cut X-Axis Text)", 0, 50, 12)
    line_threshold = st.sidebar.slider("Peak Detection Sensitivity", 5, 255, 100)
    
    st.sidebar.subheader("⏱️ Retention Time Alignment")
    rt_start = st.sidebar.number_input("Leftmost Retention Time (min)", value=0.0)
    rt_end = st.sidebar.number_input("Rightmost Retention Time (min)", value=30.0)

    # Coordinate boundaries
    x_start_px = int(w_img * (crop_left / 100))
    x_end_px = int(w_img * (1 - (crop_right / 100)))
    y_start_px = int(h_img * (crop_top / 100))
    y_end_px = int(h_img * (1 - (crop_bottom / 100)))

    # Isolate lines via OpenCV
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, line_threshold, 255, cv2.THRESH_BINARY_INV)

    debug_img = img.copy()
    cv2.rectangle(debug_img, (x_start_px, y_start_px), (x_end_px, y_end_px), (255, 165, 0), 2)

    col1, col2 = st.columns(2)
    with col1:
        st.image(debug_img, caption="Scanning Boundary Box", use_container_width=True)
        st.image(thresh[y_start_px:y_end_px, x_start_px:x_end_px], caption="Isolated Clean Signal Track", use_container_width=True)

    scan_x, scan_y = [], []
    scan_width = x_end_px - x_start_px
    scan_height = y_end_px - y_start_px

    for x in range(x_start_px, x_end_px):
        column_pixels = np.where(thresh[y_start_px:y_end_px, x] == 255)[0]
        if len(column_pixels) > 0:
            y_center = int(np.mean(column_pixels))
            scan_x.append(x - x_start_px)
            scan_y.append(scan_height - y_center)

    if len(scan_x) > 0:
        retention_times = rt_start + (np.array(scan_x) / scan_width) * (rt_end - rt_start)
        min_y, max_y = min(scan_y), max(scan_y)
        abundance = (np.array(scan_y) - min_y) / (max_y - min_y) if max_y != min_y else np.zeros_like(scan_y)

        extracted_df = pd.DataFrame({"Retention Time (min)": retention_times, "Relative Abundance": abundance})

        with col2:
            st.subheader("📈 Reconstructed Chromatogram Plot")
            st.line_chart(data=extracted_df, x="Retention Time (min)", y="Relative Abundance")

        st.subheader("🔍 Automated Peak Analysis Report")
        detected_peaks = []
        
        for i in range(5, len(abundance) - 5):
            if abundance[i] == max(abundance[i-5:i+5]) and abundance[i] > 0.12:
                rt_val = retention_times[i]
                ab_val = abundance[i]
                
                # Automated Library Matching Logic based on your guide's case studies
                chemical_guess = "Unknown Hydrocarbon Component"
                if 1.5 <= rt_val <= 1.8:
                    chemical_guess = "Ethanol (Residual Manufacturing Solvent)"
                elif 8.5 <= rt_val <= 9.5:
                    chemical_guess = "Benzene Derivative Cluster (Contaminant/Epoxy Failure Factor)"
                elif 18.8 <= rt_val <= 19.2:
                    chemical_guess = "Palmitic Acid (Saturated Fatty Acid)"
                elif 20.4 <= rt_val <= 20.65:
                    chemical_guess = "Linoleic Acid (Polyunsaturated Fatty Acid)"
                elif 20.66 <= rt_val <= 20.75:
                    chemical_guess = "Oleic Acid (Monounsaturated Fatty Acid)"
                elif 20.8 <= rt_val <= 21.2:
                    chemical_guess = "Stearic Acid (Saturated Fatty Acid)"
                    
                detected_peaks.append({
                    "Retention Time (min)": round(rt_val, 2),
                    "Relative Peak Height (Y-Intensity)": round(ab_val, 2),
                    "Automated Library Match": chemical_guess
                })

        if detected_peaks:
            peaks_df = pd.DataFrame(detected_peaks).drop_duplicates(subset=["Retention Time (min)"]).reset_index(drop=True)
            st.table(peaks_df)
            
            # --- DEEP DESCRIPTIVE INTERPRETATION GENERATOR ---
            st.markdown("### 📝 Detailed Chromatographic Interpretation Summary")
            
            for index, row in peaks_df.iterrows():
                rt = row["Retention Time (min)"]
                intensity = row["Relative Peak Height (Y-Intensity)"]
                match = row["Automated Library Match"]
                
                st.markdown(f"**📍 Peak at {rt} minutes:**")
                st.write(f"- **What the Graph is Expressing:** The detector registered a chemical elution at exactly {rt} minutes on the horizontal axis timeline. This component took longer to pass through the stationary phase column column because of its chemical attraction profile.")
                st.write(f"- **Concentration/Intensity Breakdown:** The vertical height reaches a relative scale of {intensity}. This means this component ionized strongly at this specific retention mark.")
                
                # Injecting the Guide's Case Knowledge
                if "Benzene" in match:
                    st.error(f"⚠️ **Industrial Troubleshooting Warning:** This matches the **Epoxy Outgassing Contamination Failure** model. A large concentration of Benzene near the 9-minute mark indicates a failure to cure correctly or severe chemical breakdown.")
                elif "Ethanol" in match:
                    st.warning(f"💊 **Pharmaceutical Process Log:** This matches the **Residual Solvent Quality Control** model. Detecting this peak at {rt} minutes confirms that trace ethanol processing solvents are still volatile within the final product sample matrix.")
                elif "Acid" in match:
                    st.success(f"🌱 **Lipid Profile Grouping:** Identified as a major constituent of **Vegetable Cooking Oils**. The structural stacking of Palmitic, Linoleic, and Oleic tracks allows you to map out the saturation ratio for food manufacturing verification.")
        else:
            st.info("Adjust the sliders on the left sidebar to isolate the data lines.")
else:
    st.info("💡 Ready. Upload a screenshot of your Gas Chromatogram graph to run digitizing diagnostics.")
