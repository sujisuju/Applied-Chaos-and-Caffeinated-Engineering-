import streamlit as st
import pandas as pd

st.set_page_config(page_title="GC-MS Chromatogram Analyzer", layout="wide")
st.title("🧪 GC-MS Chromatogram Analyzer & Integrator")

uploaded_file = st.file_uploader("📂 Drag and drop your GC-MS CSV file here", type=["csv"])

if uploaded_file is not None:
    try:
        data = pd.read_csv(uploaded_file)
        time = data["time"].values
        intensity = data["intensity"].values
        
        st.success(f"📊 Loaded {len(time)} chromatographic data points!")
        st.line_chart(data=data, x="time", y="intensity")
        
        # Peak detection
        peak_times, peak_intensities = [], []
        for i in range(1, len(intensity) - 1):
            if intensity[i] > intensity[i-1] and intensity[i] > intensity[i+1] and intensity[i] >= 1.0:
                peak_times.append(time[i])
                peak_intensities.append(intensity[i])
                
        st.subheader(f"🔍 Detected Peaks ({len(peak_times)})")
        
        # Simple Peak Integration (Trapezoidal Area)
        total_area = 0
        peak_areas = []
        for rt in peak_times:
            area = 0
            for i in range(len(time) - 1):
                if rt - 0.5 <= time[i] <= rt + 0.5:
                    area += (intensity[i] + intensity[i+1]) * (time[i+1] - time[i]) / 2
            peak_areas.append(area)
            total_area += area
            
        # Build Summary Table
        summary_data = []
        for n, (rt, h, area) in enumerate(zip(peak_times, peak_intensities, peak_areas), start=1):
            pct = (area / total_area) * 100 if total_area > 0 else 0
            summary_data.append({"Peak #": n, "Retention Time (min)": round(rt, 2), "Height": round(h, 1), "Area": round(area, 1), "% of Total Area": f"{pct:.1f}%"})
            
        st.table(pd.DataFrame(summary_data))
        
    except Exception as e:
        st.error(f"Error: Ensure columns are labeled 'time' and 'intensity'. Details: {e}")
else:
    st.info("💡 Waiting for a GC-MS chromatogram file...")
