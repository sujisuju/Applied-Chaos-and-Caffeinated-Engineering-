import streamlit as st
import cv2
import numpy as np
import pandas as pd

st.set_page_config(page_title="Advanced FTIR Digitizer", layout="wide")
st.title("🔬 Advanced FTIR Visual Graph Digitizer")
st.write("Upload a clean screenshot of an FTIR spectrum graph to extract numeric data and analyze peaks.")

# 1. Image File Uploader
uploaded_image = st.file_uploader("📂 Upload FTIR Graph Image (.png, .jpg)", type=["png", "jpg", "jpeg"])

if uploaded_image is not None:
    # Convert uploaded file into an OpenCV image matrix
    file_bytes = np.asarray(bytearray(uploaded_image.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    h_img, w_img, _ = img.shape

    col1, col2 = st.columns(2)
    with col1:
        st.image(uploaded_image, caption="Original Spectrum Screenshot", use_container_width=True)

    # 2. Computer Vision Processing: Isolate the spectral line
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Binary thresholding: isolate dark pixels (the curve) from light background
    _, thresh = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY_INV)

    # 3. Extract Pixel Coordinates
    pixel_x = []
    pixel_y = []
    for x in range(w_img):
        # Find all black pixels in this column
        column_pixels = np.where(thresh[:, x] == 255)[0]
        if len(column_pixels) > 0:
            # Take the average row position of the line in this column
            y_center = int(np.mean(column_pixels))
            pixel_x.append(x)
            # Invert Y axis because pixel index (0) starts at the top of the screen
            pixel_y.append(h_img - y_center)

    # 4. Calibration Parameters (User input for mapping)
    st.sidebar.header("📐 Axis Calibration")
    st.sidebar.write("Set the boundaries matching your uploaded image's axes:")
    wn_start = st.sidebar.number_input("Leftmost Wavenumber (cm⁻¹)", value=4000)
    wn_end = st.sidebar.number_input("Rightmost Wavenumber (cm⁻¹)", value=400)
    
    if len(pixel_x) > 0:
        # Convert pixel values to chemical scale coordinates
        wavenumbers = wn_start + (np.array(pixel_x) / w_img) * (wn_end - wn_start)
        
        # Normalize the extracted Y pixels to a relative absorbance scale (0.0 to 1.0)
        min_y, max_y = min(pixel_y), max(pixel_y)
        absorbance = (np.array(pixel_y) - min_y) / (max_y - min_y) if max_y != min_y else np.zeros_like(pixel_y)

        # Structure data into a dataframe
        extracted_df = pd.DataFrame({"wavenumber": wavenumbers, "absorbance": absorbance})

        with col2:
            st.subheader("📈 Digitized Numerical Data Plot")
            st.line_chart(data=extracted_df, x="wavenumber", y="absorbance")

        # 5. Algorithmic Peak Detection (Simplified local maxima search)
        st.subheader("🔍 Automated Peak Analysis & Database Matching")
        detected_peaks = []
        
        # Simple window checking loop to identify peaks
        for i in range(5, len(absorbance) - 5):
            if absorbance[i] == max(absorbance[i-5:i+5]) and absorbance[i] > 0.15:
                wn_val = wavenumbers[i]
                abs_val = absorbance[i]
                
                # Check against functional group reference database thresholds
                assignment = "Fingerprint Region / Unassigned"
                if 3200 <= wn_val <= 3600:
                    assignment = "O-H Stretch (Alcohol/Hydroxyl group) — Broad Peak"
                elif 2850 <= wn_val <= 3000:
                    assignment = "C-H Stretch (Alkane aliphatic group)"
                elif 1650 <= wn_val <= 1800:
                    assignment = "C=O Stretch (Carbonyl structural group) — Sharp Peak"
                elif 1500 <= wn_val <= 1600:
                    assignment = "C=C Stretch (Aromatic / Alkene ring system)"
                
                detected_peaks.append({"Wavenumber (cm⁻¹)": round(wn_val, 1), "Relative Intensity": round(abs_val, 2), "Functional Group Assignment": assignment})

        if detected_peaks:
            # Drop duplicates caused by adjacent matching indices
            peaks_df = pd.DataFrame(detected_peaks).drop_duplicates(subset=["Wavenumber (cm⁻¹)"]).reset_index(drop=True)
            st.table(peaks_df)
        else:
            st.info("No significant peaks detected above baseline threshold.")
            
else:
    st.info("💡 App is active. Please upload an image file of an FTIR graph to run the digitization matrix.")
