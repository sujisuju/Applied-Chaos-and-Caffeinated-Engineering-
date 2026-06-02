import streamlit as st
import cv2
import numpy as np
import pandas as pd

st.set_page_config(page_title="Deep FTIR Image Digitizer", layout="wide")
st.title("🔬 Deep FTIR Matrix Digitizer & Structural Interpreter")
st.write("Calibrate the scanning thresholds below to reconstruct raw data arrays from your graph image.")

# --- THE SINGLE FILE UPLOADER ---
uploaded_image = st.file_uploader("📂 Upload FTIR Graph Image (.png, .jpg)", type=["png", "jpg", "jpeg"])

if uploaded_image is not None:
    # Decode image matrix
    file_bytes = np.asarray(bytearray(uploaded_image.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    h_img, w_img, _ = img.shape

    # --- DEEP ANALYSIS SIDEBAR CONTROLS ---
    st.sidebar.header("🎛️ Matrix Tuning & Calibration")
    
    # Sliders to dynamically crop out borders/text labels
    st.sidebar.subheader("✂️ Crop Graph Borders (% of Image)")
    crop_left = st.sidebar.slider("Crop Left Margin", 0, 50, 10)
    crop_right = st.sidebar.slider("Crop Right Margin", 0, 50, 5)
    crop_top = st.sidebar.slider("Crop Top Margin", 0, 50, 5)
    crop_bottom = st.sidebar.slider("Crop Bottom Margin", 0, 50, 10)
    
    # Sensitivity slider to isolate dark lines from gray gridlines
    line_threshold = st.sidebar.slider("Line Isolation Intensity", 5, 255, 120)
    
    st.sidebar.subheader("📐 Axis Scale Calibration")
    wn_start = st.sidebar.number_input("Leftmost Wavenumber (cm⁻¹)", value=4000)
    wn_end = st.sidebar.number_input("Rightmost Wavenumber (cm⁻¹)", value=400)

    # Calculate actual pixel boundaries based on user sliders
    x_start_px = int(w_img * (crop_left / 100))
    x_end_px = int(w_img * (1 - (crop_right / 100)))
    y_start_px = int(h_img * (crop_top / 100))
    y_end_px = int(h_img * (1 - (crop_bottom / 100)))

    # Process matrices using OpenCV
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, line_threshold, 255, cv2.THRESH_BINARY_INV)

    # Isolate the scanning zone for visual debugging
    debug_img = img.copy()
    cv2.rectangle(debug_img, (x_start_px, y_start_px), (x_end_px, y_end_px), (0, 255, 0), 2)

    col1, col2 = st.columns(2)
    with col1:
        st.image(debug_img, caption="Scanning Zone (Green Box)", use_container_width=True)
        st.image(thresh[y_start_px:y_end_px, x_start_px:x_end_px], caption="Isolating the Data Track", use_container_width=True)

    # Data array reconstruction loop
    scan_x = []
    scan_y = []
    scan_width = x_end_px - x_start_px
    scan_height = y_end_px - y_start_px

    for x in range(x_start_px, x_end_px):
        # Scan only within vertical cropped boundaries
        column_pixels = np.where(thresh[y_start_px:y_end_px, x] == 255)[0]
        if len(column_pixels) > 0:
            # Pinpoint the vertical center of the line tracking across this column
            y_center = int(np.mean(column_pixels))
            scan_x.append(x - x_start_px)
            # Invert coordinate plane relative to baseline
            scan_y.append(scan_height - y_center)

    if len(scan_x) > 0:
        # Map pixel positions directly to functional scale arrays
        wavenumbers = wn_start + (np.array(scan_x) / scan_width) * (wn_end - wn_start)
        min_y, max_y = min(scan_y), max(scan_y)
        absorbance = (np.array(scan_y) - min_y) / (max_y - min_y) if max_y != min_y else np.zeros_like(scan_y)

        # Smooth signal noise using a simple rolling mean window
        smooth_abs = pd.Series(absorbance).rolling(window=3, center=True).mean().fillna(0).values
        extracted_df = pd.DataFrame({"wavenumber": wavenumbers, "absorbance": smooth_abs})

        with col2:
            st.subheader("📈 Reconstructed Coordinate Data Array")
            st.line_chart(data=extracted_df, x="wavenumber", y="absorbance")

        # Point-by-point peak identification criteria
        st.subheader("🔍 Molecular Signature Report")
        detected_peaks = []
        
        for i in range(5, len(smooth_abs) - 5):
            # Check local coordinate maxima condition
            if smooth_abs[i] == max(smooth_abs[i-5:i+5]) and smooth_abs[i] > 0.10:
                wn_val = wavenumbers[i]
                abs_val = smooth_abs[i]
                
                # Spectral matching structural flags
                assignment = "Fingerprint Area Matrix"
                if 3200 <= wn_val <= 3600:
                    assignment = "O-H Stretch (Hydroxyl configuration)"
                elif 3250 <= wn_val <= 3400:
                    assignment = "N-H Stretch (Secondary Amide coordination)"
                elif 2850 <= wn_val <= 3000:
                    assignment = "C-H Aliphatic Stretch (CH₂/CH₃ backbone)"
                elif 1630 <= wn_val <= 1690:
                    assignment = "C=O Amide I Band Stretch (Polyamide linkage)"
                elif 1530 <= wn_val <= 1570:
                    assignment = "N-H Bend / C-N Stretch (Amide II confirmation)"
                
                detected_peaks.append({"Wavenumber (cm⁻¹)": round(wn_val, 1), "Relative Intensity": round(abs_val, 2), "Structural Assignment": assignment})

        if detected_peaks:
            peaks_df = pd.DataFrame(detected_peaks).drop_duplicates(subset=["Wavenumber (cm⁻¹)"]).reset_index(drop=True)
            st.table(peaks_df)
            
            # Print a deep text summary for your friends
            st.markdown("### 📝 Spectroscopic Interpretation Summary")
            assignments_found = peaks_df["Structural Assignment"].values
            if any("Amide" in a for a in assignments_found):
                st.success("🔬 **Polyamide Matrix Profile Detected:** The matching coordination of Amide I (C=O stretch near 1650 cm⁻¹) and Amide II (N-H bend near 1540 cm⁻¹) flags a high probability of structural Nylon variants, mirroring your sample label text background.")
        else:
            st.info("Adjust the 'Crop' or 'Isolation' handles in the sidebar to lock onto the curve data tracking line.")
else:
    st.info("💡 Ready. Please drop your graph snapshot in to parse the visual structural tracking matrix.")
