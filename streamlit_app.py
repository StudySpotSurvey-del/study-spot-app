import streamlit as st
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MinMaxScaler

# Load data from the uploaded Excel file
df = pd.read_excel("spot server 4.xlsx", engine="openpyxl")

# App title
st.title("🔍 ระบบแนะนำสถานที่ติวที่เหมาะสม")

# User input widgets
open_time = st.slider("เปิดไม่เกิน (ชั่วโมง)", 0, 24, 8)
close_time = st.slider("ปิดไม่ต่ำกว่า (ชั่วโมง)", 0, 24, 16)
distance = st.slider("ระยะทาง (กม.)", 0.5, 6.0, 1.0)
air = st.radio("แอร์", ["ต้องการ", "ไม่ต้องการ"]) == "ต้องการ"
private = st.radio("ห้องส่วนตัว", ["ต้องการ", "ไม่ต้องการ"]) == "ต้องการ"

# Search button
if st.button("🔍 ค้นหาสถานที่ติว"):
    # Filter data based on user input
    filtered = df[
        (df["open_time"] <= open_time) &
        (df["close_time"] >= close_time) &
        (df["distance"] <= distance)
    ]

    if filtered.empty:
        st.error("❌ ไม่มีสถานที่ติวที่ตรงกับเงื่อนไขของคุณ")
    else:
        # Prepare data for KNN
        features = ["distance", "air_conditioned", "private_room"]
        user_vector = pd.DataFrame([{
            "distance": distance,
            "air_conditioned": int(air),
            "private_room": int(private)
        }])
        scaler = MinMaxScaler()
        scaled = scaler.fit_transform(filtered[features])
        scaled_user = scaler.transform(user_vector)
        model = NearestNeighbors(n_neighbors=min(5, len(filtered)))
        model.fit(scaled)
        _, indices = model.kneighbors(scaled_user)

        # Display recommended places horizontally
        st.subheader("📍 สถานที่แนะนำ:")
        cols = st.columns(len(indices[0]))
        for col, idx in zip(cols, indices[0]):
            place = filtered.iloc[idx]
            lat = place['latitude']
            lon = place['longitude']
            map_url = f"https://www.google.com/maps?q={lat},{lon}"
            with col:
                st.markdown(f"""
                #### {place['name']}
                - ระยะทาง: {place['distance']} กม.
                - เวลาเปิด-ปิด: {place['open_time']} - {place['close_time']}
                - แอร์: {'มี' if place['air_conditioned'] else 'ไม่มี'}
                - ห้องส่วนตัว: {'มี' if place['private_room'] else 'ไม่มี'}
                """)
                if st.button(f"✅ ไปที่ {place['name']}", key=place['name']):
                    st.markdown(f"[🌐 เปิดแผนที่ Google Maps]({map_url})")
                    st.markdown(f"<meta http-equiv='refresh' content='0; url={map_url}'>", unsafe_allow_html=True)

