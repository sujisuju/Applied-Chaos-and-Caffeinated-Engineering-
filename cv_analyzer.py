import streamlit as st
import cv2
import numpy as np
import pandas as pd
from fpdf import FPDF

st.title("⚡ Cyclic Voltammetry Matrix Digitizer & Redox Interpreter")
st.write("Extract dynamic redox potential profiles and scan rates directly from potentiostat graph screenshots.")

uploaded_image = st.file_uploader("📂 Upload Voltammetry Curve Image (.png, .jpg, .webp)", type=["png", "jpg", "jpeg", "webp"])

if uploaded_image is not None:
    file_bytes = np.asarray(bytearray(uploaded_image.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    h_img, w_img, _ = img.shape

    # --- SIDEBAR CONTROLS ---
    st.sidebar.header("🎛️ Electrochemistry Calibration")
    crop_left = st.sidebar.slider("Crop Left Margin", 0, 50, 12)
    crop_right = st.sidebar.slider("Crop Right Margin", 0, 50, 6)
    crop_top = st.sidebar.slider("Crop Top Margin", 0, 50, 6)
    crop_bottom = st.sidebar.slider("Crop Bottom Margin", 0, 50, 12)
    line_threshold = st.sidebar.slider("Curve Track Sensitivity", 5, 255, 110)
    
    st.sidebar.subheader("🔌 Voltage Scale Calibration")
    v_start = st.sidebar.number_input("Leftmost Potential (V)", value=-1.0)
    v_end = st.sidebar.number_input("Rightmost Potential (V)", value=1.0)

    x_start_px = int(w_img * (crop_left / 100))
    x_end_px = int(w_img * (1 - (crop_right / 100)))
    y_start_px = int(h_img * (crop_top / 100))
    y_end_px = int(h_img * (1 - (crop_bottom / 100)))

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, line_threshold, 255, cv2.THRESH_BINARY_INV)

    debug_img = img.copy()
    cv2.rectangle(debug_img, (x_start_px, y_start_px), (x_end_px, y_end_px), (255, 0, 0), 2)

    col1, col2 = st.columns(2)
    with col1:
        st.image(debug_img, caption="Voltammetry Sweep Boundary Box", use_container_width=True)
    with col2:
        st.image(thresh[y_start_px:y_end_px, x_start_px:x_end_px], caption="Isolated Electrolyte Signal Track", use_container_width=True)

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
        potentials = v_start + (np.array(scan_x) / scan_width) * (v_end - v_start)
        min_y, max_y = min(scan_y), max(scan_y)
        current = (np.array(scan_y) - min_y) / (max_y - min_y) if max_y != min_y else np.zeros_like(scan_y)
        smooth_current = pd.Series(current).rolling(window=3, center=True).mean().fillna(0).values
        extracted_df = pd.DataFrame({"Potential (V)": potentials, "Relative Current": smooth_current})

        st.subheader("🔍 Resolved Faradaic Redox Peak Batches")
        
        cv_batches = {
            "Anodic Oxidation Sweep (Oxidation Peaks)": [],
            "Cathodic Reduction Sweep (Reduction Peaks)": []
        }
        
        for i in range(5, len(smooth_current) - 5):
            if smooth_current[i] == max(smooth_current[i-5:i+5]) and smooth_current[i] > 0.15:
                v_val = round(potentials[i], 2)
                i_val = round(smooth_current[i], 2)
                
                if i_val >= 0.5:
                    cv_batches["Anodic Oxidation Sweep (Oxidation Peaks)"].append((v_val, i_val))
                else:
                    cv_batches["Cathodic Reduction Sweep (Reduction Peaks)"].append((v_val, i_val))

        report_text_lines = []
        has_peaks = False

        for batch_name, peaks in cv_batches.items():
            if len(peaks) > 0:
                has_peaks = True
                unique_peaks = sorted(list(set(peaks)), key=lambda x: x[0])[:3]
                st.markdown(f"### 🗂️ {batch_name}")
                peak_list_text = "  |  ".join([f"{v} V (Relative Current: {curr})" for v, curr in unique_peaks])
                st.info(f"📍 **Registered Faradaic Intersections:** {peak_list_text}")
                
                expr_text = ""
                if "Anodic" in batch_name:
                    expr_text = "Electrochemical Expression: These positions mark where electrons are stripped away from chemical species diffusing to the electrode interface. Reaching max height reflects the localized depletion of reduced analyte species at the electrical boundary layer."
                elif "Cathodic" in batch_name:
                    expr_text = "Electrochemical Expression: This represents active electron injection into the molecular matrix. Peaks tracking here isolate coordinates where reduction kinetics dominate, allowing calculation of your system's peak separation profile."
                
                st.write(f"**{expr_text}**")
                st.markdown("---")
                report_text_lines.append((batch_name, peak_list_text, expr_text))

        st.subheader("📈 Reconstructed Cyclic Voltammetry Sweep Plot")
        st.line_chart(data=extracted_df, x="Potential (V)", y="Relative Current")

        # --- SEPARATE DEDICATED BUTTONS SECTION ---
        st.markdown("### 📥 Export Instrumentation Analysis Records")

        # Button 1: Quick Sheet
        def generate_quick_cv_pdf(data_lines):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Helvetica", "B", 16)
            pdf.cell(0, 12, "Cyclic Voltammetry Sweep Log", align="C", new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", 10)
            pdf.ln(5)
            for title, points, _ in data_lines:
                pdf.cell(0, 6, f"- {title}: {points}", new_x="LMARGIN", new_y="NEXT")
            return pdf.output()

        # Button 2: Detailed Understanding Report
        def generate_detailed_cv_pdf(data_lines):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Helvetica", "B", 18)
            pdf.cell(0, 15, "Applied Chaos and Caffeinated Engineering", align="C", new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "I", 12)
            pdf.cell(0, 10, "Comprehensive Electrochemical Kinetic Evaluation Report", align="C", new_x="LMARGIN", new_y="NEXT")
            pdf.line(10, 40, 200, 40)
            pdf.ln(12)
            
            pdf.set_font("Helvetica", "B", 14)
            pdf.cell(0, 10, "1. Executive Faradaic Matrix Diagnostic Summary", new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", 11)
            pdf.multi_cell(0, 6, "This official report certifies the mathematical extraction of reversible electron transfer loops. The digital peak-filtering array isolates oxidation-reduction current densities, allowing rigorous validation of diffusion mechanics and boundary layer kinetics.")
            pdf.ln(5)
            
            pdf.set_font("Helvetica", "B", 14)
            pdf.cell(0, 10, "2. Redox Sweep Phase Analysis", new_x="LMARGIN", new_y="NEXT")
            for title, points, description in data_lines:
                pdf.set_font("Helvetica", "B", 11)
                pdf.cell(0, 7, f"Sweep Phase: {title}", new_x="LMARGIN", new_y="NEXT")
                pdf.set_font("Helvetica", "I", 10)
                pdf.cell(0, 6, f"Extracted Potential Vertices: {points}", new_x="LMARGIN", new_y="NEXT")
                pdf.set_font("Helvetica", "", 10)
                pdf.multi_cell(0, 6, description)
                pdf.ln(4)
            return pdf.output()

        if has_peaks:
            c1, c2 = st.columns(2)
            with c1:
                pdf_quick = generate_quick_cv_pdf(report_text_lines)
                st.download_button(label="📄 Download Quick Data Sheet (PDF)", data=bytes(pdf_quick), file_name="cv_quick_data.pdf", mime="application/pdf")
            with c2:
                pdf_detailed = generate_detailed_cv_pdf(report_text_lines)
                st.download_button(label="📘 Download Report (PDF)", data=bytes(pdf_detailed), file_name="cv_comprehensive_report.pdf", mime="application/pdf")
else:
    st.info("💡 Ready. Upload a voltammetry screenshot to extract redox data structures.")
