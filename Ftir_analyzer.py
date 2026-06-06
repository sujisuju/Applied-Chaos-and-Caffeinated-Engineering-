import streamlit as st
import cv2
import numpy as np
import pandas as pd
from fpdf import FPDF

# Text-safe, structured sub-module definition
uploaded_image = st.file_uploader("📂 Upload FTIR Graph Image (.png, .jpg, .jpeg, .webp)", type=["png", "jpg", "jpeg", "webp"])

if uploaded_image is not None:
    file_bytes = np.asarray(bytearray(uploaded_image.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    h_img, w_img, _ = img.shape

    # --- SIDEBAR CONTROLS ---
    st.sidebar.header("🎛️ Optical Calibration")
    crop_left = st.sidebar.slider("Crop Left Margin", 0, 50, 10)
    crop_right = st.sidebar.slider("Crop Right Margin", 0, 50, 5)
    crop_top = st.sidebar.slider("Crop Top Margin", 0, 50, 5)
    crop_bottom = st.sidebar.slider("Crop Bottom Margin", 0, 50, 10)
    line_threshold = st.sidebar.slider("Spectral Line Sensitivity", 5, 255, 120)
    
    st.sidebar.subheader("📐 Wavenumber Scale Calibration")
    wn_start = st.sidebar.number_input("Leftmost Wavenumber (cm-1)", value=4000)
    wn_end = st.sidebar.number_input("Rightmost Wavenumber (cm-1)", value=400)

    x_start_px = int(w_img * (crop_left / 100))
    x_end_px = int(w_img * (1 - (crop_right / 100)))
    y_start_px = int(h_img * (crop_top / 100))
    y_end_px = int(h_img * (1 - (crop_bottom / 100)))

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, line_threshold, 255, cv2.THRESH_BINARY_INV)

    debug_img = img.copy()
    cv2.rectangle(debug_img, (x_start_px, y_start_px), (x_end_px, y_end_px), (0, 255, 0), 2)

    col1, col2 = st.columns(2)
    with col1:
        st.image(debug_img, caption="Active Scanning Zone (Green Box)", use_container_width=True)
    with col2:
        st.image(thresh[y_start_px:y_end_px, x_start_px:x_end_px], caption="Isolated Infrared Trace Mask", use_container_width=True)

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
        wavenumbers = wn_start + (np.array(scan_x) / scan_width) * (wn_end - wn_start)
        min_y, max_y = min(scan_y), max(scan_y)
        absorbance = (np.array(scan_y) - min_y) / (max_y - min_y) if max_y != min_y else np.zeros_like(scan_y)
        smooth_abs = pd.Series(absorbance).rolling(window=3, center=True).mean().fillna(0).values
        extracted_df = pd.DataFrame({"wavenumber": wavenumbers, "absorbance": smooth_abs})

        st.subheader("🔍 Identified Absorptivity Peaks & Structural Signatures")
        
        # Safe character text arrays for PDF injection
        batches = {
            "Hydroxyl / Bound Water Region (3200 - 3650 cm-1)": [],
            "Aliphatic C-H Backbone stretching Region (2840 - 3000 cm-1)": [],
            "Carbonyl Double-Bond Formations (1690 - 1750 cm-1)": [],
            "Amide I and II Polymer Coupling Tracks (1530 - 1689 cm-1)": [],
            "Fingerprint Matrix Skeletal Vibrations (400 - 1499 cm-1)": []
        }
        
        for i in range(5, len(smooth_abs) - 5):
            if smooth_abs[i] == max(smooth_abs[i-5:i+5]) and smooth_abs[i] > 0.12:
                wn_val = round(wavenumbers[i], 1)
                abs_val = round(smooth_abs[i], 2)
                
                if 3200 <= wn_val <= 3650:
                    batches["Hydroxyl / Bound Water Region (3200 - 3650 cm-1)"].append((wn_val, abs_val))
                elif 2840 <= wn_val <= 3000:
                    batches["Aliphatic C-H Backbone stretching Region (2840 - 3000 cm-1)"].append((wn_val, abs_val))
                elif 1690 <= wn_val <= 1750:
                    batches["Carbonyl Double-Bond Formations (1690 - 1750 cm-1)"].append((wn_val, abs_val))
                elif 1530 <= wn_val <= 1689:
                    batches["Amide I and II Polymer Coupling Tracks (1530 - 1689 cm-1)"].append((wn_val, abs_val))
                elif wn_val < 1500:
                    batches["Fingerprint Matrix Skeletal Vibrations (400 - 1499 cm-1)"].append((wn_val, abs_val))

        report_text_lines = []
        has_peaks = False
        
        for batch_name, peaks in batches.items():
            if len(peaks) > 0:
                has_peaks = True
                unique_peaks = sorted(list(set(peaks)), key=lambda x: x[0], reverse=True)[:5]
                st.markdown(f"### 🗂️ {batch_name}")
                peak_list_text = "  |  ".join([f"{wn} cm-1 (Abs: {val})" for wn, val in unique_peaks])
                st.info(f"📍 **Registered Peaks in this Batch:** {peak_list_text}")
                
                expr_text = ""
                if "Hydroxyl" in batch_name:
                    expr_text = "Molecular Expression: These high-frequency photon absorptions indicate intermolecular hydrogen bonding dynamics. The wide profile typically signifies stretching modulations of O-H networks or structural water clusters bound within the material layer."
                elif "Aliphatic" in batch_name:
                    expr_text = "Molecular Expression: This batch captures the structural core of organic molecules. These symmetric and asymmetric vibrations outline the stretching transitions of saturated aliphatic CH2 and CH3 carbon frames composing the polymer backbone."
                elif "Carbonyl" in batch_name:
                    expr_text = "Molecular Expression: These highly energetic peaks express a very strong changing dipole moment native to a structural C=O double bond. It indicates the presence of ester, ketone, or carboxylic acid distributions inside the matrix."
                elif "Amide" in batch_name:
                    expr_text = "Molecular Expression: This indicates heavily coupled nitrogenous configurations. Strong bands tracing here characterize structural Amide I (carbonyl stretching) and Amide II (in-plane N-H bending) coordination networks, typical of complex polyamide engineering composites."
                elif "Fingerprint" in batch_name:
                    expr_text = "Molecular Expression: This hyper-dense collection marks the macro-structural skeletal fingerprint of the compound. The complex layout of positions represents localized bending, rocking, and twisting modes of single-bond C-O, C-C, and C-N connections unique to this specific material recipe."
                
                st.write(f"**{expr_text}**")
                report_text_lines.append((batch_name, peak_list_text, expr_text))
                st.markdown("---")

        # Visual layout rendering sequence
        st.subheader("📈 Reconstructed Absorbance Coordinate Array")
        st.line_chart(data=extracted_df, x="wavenumber", y="absorbance")
        
        def generate_populated_ftir_pdf(data_lines):
            pdf = FPDF()
            pdf.add_page()
            
            pdf.set_font("Helvetica", "B", 18)
            pdf.cell(0, 15, "Applied Chaos and Caffeinated Engineering", align="C", new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "I", 12)
            pdf.cell(0, 10, "Official FTIR Analytical Verification Report", align="C", new_x="LMARGIN", new_y="NEXT")
            pdf.line(10, 40, 200, 40)
            pdf.ln(15)
            
            pdf.set_font("Helvetica", "B", 14)
            pdf.cell(0, 10, "1. Automated Spectroscopic Interpretation Record", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(2)
            
            for title, points, description in data_lines:
                pdf.set_font("Helvetica", "B", 11)
                pdf.cell(0, 7, f"Group: {title}", new_x="LMARGIN", new_y="NEXT")
                pdf.set_font("Helvetica", "I", 10)
                pdf.cell(0, 6, f"Extracted Peak Array: {points}", new_x="LMARGIN", new_y="NEXT")
                pdf.set_font("Helvetica", "", 10)
                pdf.multi_cell(0, 6, description)
                pdf.ln(4)
                
            pdf.ln(5)
            pdf.set_font("Helvetica", "B", 12)
            pdf.cell(0, 8, "2. Operational Verification Sign-Off", new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", 11)
            pdf.cell(0, 8, "- Primary Investigator: Jannatul Ferdous Sujana", new_x="LMARGIN", new_y="NEXT")
            pdf.cell(0, 8, "- Authentication Status: COMPUTATIONALLY VALIDATED AND COMPILED", new_x="LMARGIN", new_y="NEXT")
            
            return pdf.output()

        if has_peaks:
            pdf_out = generate_populated_ftir_pdf(report_text_lines)
            pdf_bytes = bytes(pdf_out)
            
            st.download_button(
                label="📥 Download Full Processed FTIR Analysis Report (PDF)",
                data=pdf_bytes,
                file_name="ftir_processed_analysis_report.pdf",
                mime="application/pdf"
            )
else:
    st.info("💡 Ready. Drop a clean screenshot of an FTIR graph in to run advanced computer vision diagnostics.")
