import streamlit as st
import cv2
import numpy as np
import pandas as pd

st.title("🧪 GCMS Visual Chromatogram Digitizer")
st.write("Isolate visual peaks from a GCMS screenshot to analyze retention times and relative peak intensities.")

uploaded_image = st.file_uploader("📂 Upload GCMS Graph Image (.png, .jpg, .jpeg, .webp)", type=["png", "jpg", "jpeg", "webp"])

if uploaded_image is not None:
    # Decode image matrix
    file_bytes = np.asarray(bytearray(uploaded_image.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    h_img, w_img, _ = img.shape

    # Sidebars for cropping out chromatogram boundaries
    st.sidebar.header("🎛️ Chromatogram Tuning")
    crop_left = st.sidebar.slider("Crop Left Margin", 0, 50, 10)
    crop_right = st.sidebar.slider("Crop Right Margin", 0, 50, 5)
    crop_top = st.sidebar.slider("Crop Top Margin", 0, 50, 5)
    crop_bottom = st.sidebar.slider("Crop Bottom Margin", 0, 50, 12)
    line_threshold = st.sidebar.slider("Peak Isolation Intensity", 5, 255, 100)
    
    st.sidebar.subheader("⏱️ Retention Time Axis Scale")
    rt_start = st.sidebar.number_input("Start Time (min)", value=0.0)
    rt_end = st.sidebar.number_input("End Time (min)", value=30.0)

    # Calculate coordinate system bounds
    x_start_px = int(w_img * (crop_left / 100))
    x_end_px = int(w_img * (1 - (crop_right / 100)))
    y_start_px = int(h_img * (crop_top / 100))
    y_end_px = int(h_img * (1 - (crop_bottom / 100)))

    # OpenCV Matrix Binarization
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, line_threshold, 255, cv2.THRESH_BINARY_INV)

    debug_img = img.copy()
    cv2.rectangle(debug_img, (x_start_px, y_start_px), (x_end_px, y_end_px), (255, 165, 0), 2)

    col1, col2 = st.columns(2)
    with col1:
        st.image(debug_img, caption="Chromatogram Scan Area", use_container_width=True)
        st.image(thresh[y_start_px:y_end_px, x_start_px:x_end_px], caption="Isolated Chromatogram Track", use_container_width=True)

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
            st.subheader("📈 Reconstructed Chromatogram Array")
            st.line_chart(data=extracted_df, x="Retention Time (min)", y="Relative Abundance")

        st.subheader("🔍 Resolved Chromatographic Peaks")
        detected_peaks = []
        
        # Local maxima detection window loop
        for i in range(5, len(abundance) - 5):
            if abundance[i] == max(abundance[i-5:i+5]) and abundance[i] > 0.15:
                rt_val = retention_times[i]
                ab_val = abundance[i]
                detected_peaks.append({"Retention Time (min)": round(rt_val, 2), "Relative Abundance Peak Height": round(ab_val, 2)})

        if detected_peaks:
            peaks_df = pd.DataFrame(detected_peaks).drop_duplicates(subset=["Retention Time (min)"]).reset_index(drop=True)
            st.table(peaks_df)
        else:
            st.info("Adjust the 'Tuning' handles in the left sidebar to lock onto the chromatogram line trace.")
else:
    st.info("💡 Ready. Drop a screenshot of your GCMS chromatogram trace to run pixel extraction.")
