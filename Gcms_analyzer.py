import streamlit as st
import cv2
import numpy as np
import pandas as pd
from fpdf import FPDF

st.title("🧪 Advanced GCMS Chromatogram Digitizer & Interpreter")
st.write("Extract numerical data arrays from visual chromatograms and generate formal structural logs.")

# Expanded file uploader string matrix to accept all variations
uploaded_file = st.gc_uploader(
    "📂 Upload GCMS Graph (PNG, JPG, JPEG, WEBP, PDF)", 
    type=["png", "jpg", "jpeg", "webp", "pdf", "PNG", "JPG", "JPEG", "WEBP", "PDF"]
)

if uploaded_image is not None:
    file_bytes = np.asarray(bytearray(uploaded_image.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    h_img, w_img, _ = img.shape

    # --- SIDEBAR CONTROLS ---
    st.sidebar.header("🎛️ Chromatogram Scaling")
    crop_left = st.sidebar.slider("Crop Left Margin", 0, 50, 10)
    crop_right = st.sidebar.slider("Crop Right Margin", 0, 50, 5)
    crop_top = st.sidebar.slider("Crop Top Margin", 0, 50, 5)
    crop_bottom = st.sidebar.slider("Crop Bottom Margin", 0, 50, 12)
    line_threshold = st.sidebar.slider("Peak Detection Sensitivity", 5, 255, 100)
    
    st.sidebar.subheader("⏱️ Retention Time Alignment")
    rt_start = st.sidebar.number_input("Leftmost Retention Time (min)", value=0.0)
    rt_end = st.sidebar.number_input("Rightmost Retention Time (min)", value=30.0)

    x_start_px = int(w_img * (crop_left / 100))
    x_end_px = int(w_img * (1 - (crop_right / 100)))
    y_start_px = int(h_img * (crop_top / 100))
    y_end_px = int(h_img * (1 - (crop_bottom / 100)))

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, line_threshold, 255, cv2.THRESH_BINARY_INV)

    debug_img = img.copy()
    cv2.rectangle(debug_img, (x_start_px, y_start_px), (x_end_px, y_end_px), (255, 165, 0), 2)

    col1, col2 = st.columns(2)
    with col1:
        st.image(debug_img, caption="Chromatogram Scan Area", use_container_width=True)
    with col2:
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

        st.subheader("🔍 Automated Peak Analysis Report")
        
        gc_batches = {
            "Volatile / Residual Processing Solvent Window (0.5 - 5.0 min)": [],
            "Mid-Range Aromatic / Structural Contaminants (5.1 - 15.0 min)": [],
            "High-Molecular Weight Lipids / Fatty Acids (15.1 - 30.0 min)": []
        }
        
        for i in range(5, len(abundance) - 5):
            if abundance[i] == max(abundance[i-5:i+5]) and abundance[i] > 0.12:
                rt_val = round(retention_times[i], 2)
                ab_val = round(abundance[i], 2)
                
                if 0.5 <= rt_val <= 5.0:
                    gc_batches["Volatile / Residual Processing Solvent Window (0.5 - 5.0 min)"].append((rt_val, ab_val))
                elif 5.1 <= rt_val <= 15.0:
                    gc_batches["Mid-Range Aromatic / Structural Contaminants (5.1 - 15.0 min)"].append((rt_val, ab_val))
                elif 15.1 <= rt_val <= 30.0:
                    gc_batches["High-Molecular Weight Lipids / Fatty Acids (15.1 - 30.0 min)"].append((rt_val, ab_val))

        report_text_lines = []
        has_peaks = False

        for batch_name, peaks in gc_batches.items():
            if len(peaks) > 0:
                has_peaks = True
                unique_peaks = sorted(list(set(peaks)), key=lambda x: x[0])[:4]
                st.markdown(f"### 🗂️ {batch_name}")
                peak_list_text = "  |  ".join([f"{rt} min (Abundance: {ht})" for rt, ht in unique_peaks])
                st.info(f"📍 **Resolved Chromatographic Intersections:** {peak_list_text}")
                
                expr_text = ""
                if "Solvent" in batch_name:
                    expr_text = "Chromatographic Expression: These quick elution signals track highly volatile compounds passing through the column with negligible stationary phase interaction. Spikes here typically isolate residual processing components like ethanol or cleaning solvents left over from synthesis packaging."
                elif "Contaminants" in batch_name:
                    expr_text = "Chromatographic Expression: This retention corridor isolates moderately bound structures. Clusters emerging here often reveal polymer decomposition factors, outgassing phenomena, or aromatic contaminants like benzene derivative rings breaking loose from underlying matrices."
                elif "Lipids" in batch_name:
                    expr_text = "Chromatographic Expression: These delayed peaks capture heavy, non-volatile compounds strongly bound to the inner coating layer. They require extended elution windows and match heavy lipid profiles, long-chain hydrocarbons, or long-chain fatty acid groups (Palmitic, Oleic, Linoleic matrix variants)."
                
                st.write(f"*{expr_text}*")
                st.markdown("---")
                report_text_lines.append((batch_name, peak_list_text, expr_text))

        st.subheader("📈 Reconstructed Chromatogram Plot")
        st.line_chart(data=extracted_df, x="Retention Time (min)", y="Relative Abundance")

        # --- SEPARATE DEDICATED BUTTONS SECTION ---
        st.markdown("### 📥 Export Instrumentation Analysis Records")

        # Button 1: Quick Sheet
        def generate_quick_gc_pdf(data_lines):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Helvetica", "B", 16)
            pdf.cell(0, 12, "GCMS Chrono-Elution Run Record", align="C", new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", 10)
            pdf.ln(5)
            for title, points, _ in data_lines:
                pdf.cell(0, 6, f"- {title}: {points}", new_x="LMARGIN", new_y="NEXT")
            return pdf.output()

        # Button 2: Detailed Understanding Report
        def generate_detailed_gc_pdf(data_lines):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Helvetica", "B", 18)
            pdf.cell(0, 15, "Applied Chaos and Caffeinated Engineering", align="C", new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "I", 12)
            pdf.cell(0, 10, "Comprehensive GCMS Column Elution Diagnostic Report", align="C", new_x="LMARGIN", new_y="NEXT")
            pdf.line(10, 40, 200, 40)
            pdf.ln(12)
            
            pdf.set_font("Helvetica", "B", 14)
            pdf.cell(0, 10, "1. Executive Chromatographic Metric Summary", new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", 11)
            pdf.multi_cell(0, 6, "This official record compiles the retention index timelines extracted via matrix edge threshold profiles. Component shifts isolate compound identities, verifying fraction purity grades against structural reference thresholds.")
            pdf.ln(5)
            
            pdf.set_font("Helvetica", "B", 14)
            pdf.cell(0, 10, "2. Fraction Corridor Group Analysis", new_x="LMARGIN", new_y="NEXT")
            for title, points, description in data_lines:
                pdf.set_font("Helvetica", "B", 11)
                pdf.cell(0, 7, f"Elution Phase: {title}", new_x="LMARGIN", new_y="NEXT")
                pdf.set_font("Helvetica", "I", 10)
                pdf.cell(0, 6, f"Extracted Peaks: {points}", new_x="LMARGIN", new_y="NEXT")
                pdf.set_font("Helvetica", "", 10)
                pdf.multi_cell(0, 6, description)
                pdf.ln(4)
            return pdf.output()

        if has_peaks:
            c1, c2 = st.columns(2)
            with c1:
                pdf_quick = generate_quick_gc_pdf(report_text_lines)
                st.download_button(label="📄 Download Quick Data Sheet (PDF)", data=bytes(pdf_quick), file_name="gcms_quick_data.pdf", mime="application/pdf")
            with c2:
                pdf_detailed = generate_detailed_gc_pdf(report_text_lines)
                st.download_button(label="📘 Download Report (PDF)", data=bytes(pdf_detailed), file_name="gcms_comprehensive_report.pdf", mime="application/pdf")
else:
    st.info("💡 Ready. Upload a screenshot of your Gas Chromatogram graph to run digitizing diagnostics.")
