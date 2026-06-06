import streamlit as st
import cv2
import numpy as np
import pandas as pd

st.title("🔬 Advanced FTIR Spectral Digitizer & Molecular Interpreter")
st.write("Extract precise optical data from visual infrared spectra and generate automated structural diagnostics.")

uploaded_image = st.file_uploader("📂 Upload FTIR Graph Image (.png, .jpg, .jpeg, .webp)", type=["png", "jpg", "jpeg", "webp"])

if uploaded_image is not None:
    # Decode image matrix into OpenCV format
    file_bytes = np.asarray(bytearray(uploaded_image.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    h_img, w_img, _ = img.shape

    # --- SIDEBAR TUNING CONTROLS ---
    st.sidebar.header("🎛️ Optical Calibration")
    crop_left = st.sidebar.slider("Crop Left Margin (Axes Lines)", 0, 50, 10)
    crop_right = st.sidebar.slider("Crop Right Margin", 0, 50, 5)
    crop_top = st.sidebar.slider("Crop Top Margin", 0, 50, 5)
    crop_bottom = st.sidebar.slider("Crop Bottom Margin (Wavenumber Labels)", 0, 50, 10)
    line_threshold = st.sidebar.slider("Spectral Line Sensitivity", 5, 255, 120)
    
    st.sidebar.subheader("📐 Wavenumber Scale Calibration")
    wn_start = st.sidebar.number_input("Leftmost Wavenumber (cm⁻¹)", value=4000)
    wn_end = st.sidebar.number_input("Rightmost Wavenumber (cm⁻¹)", value=400)

    # Boundary math for cropping
    x_start_px = int(w_img * (crop_left / 100))
    x_end_px = int(w_img * (1 - (crop_right / 100)))
    y_start_px = int(h_img * (crop_top / 100))
    y_end_px = int(h_img * (1 - (crop_bottom / 100)))

    # Matrix Binarization to capture the thin curve
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, line_threshold, 255, cv2.THRESH_BINARY_INV)

    debug_img = img.copy()
    cv2.rectangle(debug_img, (x_start_px, y_start_px), (x_end_px, y_end_px), (0, 255, 0), 2)

    col1, col2 = st.columns(2)
    with col1:
        st.image(debug_img, caption="Active Scanning Zone (Green Box)", use_container_width=True)
        st.image(thresh[y_start_px:y_end_px, x_start_px:x_end_px], caption="Isolated Infrared Trace Mask", use_container_width=True)

    # Coordinate Extraction
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
        # Interpolation mapping array math
        wavenumbers = wn_start + (np.array(scan_x) / scan_width) * (wn_end - wn_start)
        min_y, max_y = min(scan_y), max(scan_y)
        absorbance = (np.array(scan_y) - min_y) / (max_y - min_y) if max_y != min_y else np.zeros_like(scan_y)

        # Smooth signal noise using a 3-pixel rolling mean window filter
        smooth_abs = pd.Series(absorbance).rolling(window=3, center=True).mean().fillna(0).values
        extracted_df = pd.DataFrame({"wavenumber": wavenumbers, "absorbance": smooth_abs})

        with col2:
            st.subheader("📈 Reconstructed Absorbance Coordinate Array")
            st.line_chart(data=extracted_df, x="wavenumber", y="absorbance")

        st.subheader("🔍 Identified Absorptivity Peaks & Structural Signatures")
        detected_peaks = []
        
        # Local coordinate maxima check loop
        for i in range(5, len(smooth_abs) - 5):
            if smooth_abs[i] == max(smooth_abs[i-5:i+5]) and smooth_abs[i] > 0.12:
                wn_val = wavenumbers[i]
                abs_val = smooth_abs[i]
                
                # Rigorous reference assignment matching logic
                assignment = "Fingerprint Region (C-O, C-C, C-N Skeletal Vibrations)"
                group_class = "Complex Skeletal Matrix"
                
                if 3200 <= wn_val <= 3650:
                    assignment = "O-H Stretching Mode (Intermolecular Hydrogen Bonding)"
                    group_class = "Alcohol / Hydroxyl / Bound Water"
                elif 3250 <= wn_val <= 3400:
                    assignment = "N-H Stretching Vibration (Amide/Amine Coordination)"
                    group_class = "Polyamide / Peptide Backbone"
                elif 2840 <= wn_val <= 3000:
                    assignment = "C-H Aliphatic Stretch (CH₂ and CH₃ symmetric/asymmetric stretching)"
                    group_class = "Saturated Alkanes / Polymer Backbone"
                elif 1690 <= wn_val <= 1750:
                    assignment = "C=O Stretching Mode (Strong Carbonyl Dipole Moment)"
                    group_class = "Esters / Aldehydes / Ketones / Carboxylic Acids"
                elif 1630 <= wn_val <= 1689:
                    assignment = "Amide I Band (Primary/Secondary C=O Stretching with N-H coupling)"
                    group_class = "Proteins / Nylon / Polyurethane Linkages"
                elif 1500 <= wn_val <= 1600:
                    assignment = "Amide II Band (N-H In-Plane Bending combined with C-N stretching)"
                    group_class = "Nitrogenous Structural Complexes"
                elif 2100 <= wn_val <= 2260:
                    assignment = "C≡N or C≡C Triple Bond Stretching"
                    group_class = "Nitriles / Alkyne Formations"

                detected_peaks.append({
                    "Wavenumber (cm⁻¹)": round(wn_val, 1),
                    "Relative Intensity": round(abs_val, 2),
                    "Vibrational Assignment": assignment,
                    "Functional Group Class": group_class
                })

        if detected_peaks:
            peaks_df = pd.DataFrame(detected_peaks).drop_duplicates(subset=["Wavenumber (cm⁻¹)"]).reset_index(drop=True)
            st.table(peaks_df)
            
            # --- SCIENTIFIC INTERPRETATION GENERATOR ---
            st.markdown("### 📝 Detailed Spectroscopic Interpretation Summary")
            st.write("This section breaks down the physical meaning behind the graph's layout based on the rules of infrared quantum mechanics:")
            
            # Global assessment check
            classes_found = peaks_df["Functional Group Class"].values
            
            if "Polyamide / Peptide Backbone" in classes_found or "Proteins / Nylon / Polyurethane Linkages" in classes_found:
                st.success("🧬 **Material Diagnosis - Polyamide (Nylon-Type) Structure Identified:**\n"
                           "The simultaneous presence of the **Amide I band** (strong C=O stretching near 1640–1650 cm⁻¹) and the **Amide II band** (N-H bending combination near 1540 cm⁻¹), backed by the high-frequency N-H stretch, is a classic fingerprint profile of nylon polymer variants or protein backbones. The graph is explicitly expressing a heavily coupled secondary amide network.")
            elif "Esters / Aldehydes / Ketones / Carboxylic Acids" in classes_found and "Alcohol / Hydroxyl / Bound Water" in classes_found:
                st.warning("🧪 **Material Diagnosis - Carboxylic Acid or Hydrolyzed Ester Matrix:**\n"
                           "The matching of a broad, wide absorption envelope in the 3200–3600 cm⁻¹ region alongside a sharp, intense carbonyl peak in the 1700 cm⁻¹ region indicates strong hydrogen-bonded acid groups or moisture-compromised structures.")

            # Point-by-point scientific translation loop
            for index, row in peaks_df.iterrows():
                wn = row["Wavenumber (cm⁻¹)"]
                int_val = row["Relative Intensity"]
                vib = row["Vibrational Assignment"]
                fg = row["Functional Group Class"]
                
                st.markdown(f"**📍 Peak Feature at {wn} cm⁻¹:**")
                st.write(f"- **The Science Behind It:** When infrared light passed through your sample, the molecular covalent bonds matching the frequency of **{wn} cm⁻¹** absorbed the photons. This precise packet of energy caused the chemical bonds to experience an active **{vib}**.")
                st.write(f"- **What the Graph is Indicating:** The vertical absorbance height of **{int_val}** expresses the relative strength of the changing dipole moment. A sharper, deeper transmittance drop (or higher absorbance peak) indicates a highly concentrated population of the **{fg}** functional cluster within the structural matrix of your material.")
        else:
            st.info("💡 Adjust the tuning sliders on the left sidebar to change sensitivity and lock onto your spectrum curve.")
else:
    st.info("💡 Ready. Drop a clean screenshot of an FTIR graph in to run advanced computer vision diagnostics.")
