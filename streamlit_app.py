import streamlit as st
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MinMaxScaler

# โหลดข้อมูลจากไฟล์ Excel
df = pd.read_excel("spot server.xlsx", engine="openpyxl")

# ส่วนหัวของแอป
st.title("🔍 ระบบแนะนำสถานที่ติวที่เหมาะสม")

# รับค่าจากผู้ใช้ผ่าน widgets
open_time = st.slider("เปิดไม่เกิน (ชั่วโมง)", 0, 24, 8)
close_time = st.slider("ปิดไม่ต่ำกว่า (ชั่วโมง)", 0, 24, 16)
distance = st.slider("ระยะทาง (กม.)", 0.5, 5.0, 1.0)
air = st.radio("แอร์", ["ต้องการ", "ไม่ต้องการ"]) == "ต้องการ"
private = st.radio("ห้องส่วนตัว", ["ต้องการ", "ไม่ต้องการ"]) == "ต้องการ"
show_recommendation = st.radio("ต้องการแสดงสถานที่แนะนำหรือไม่", ["แสดง", "ไม่แสดง"]) == "แสดง"

# เมื่อผู้ใช้กดปุ่มค้นหา
if st.button("🔍 ค้นหาสถานที่ติว"):
    # กรองข้อมูลตามเงื่อนไข
    filtered = df[
        (df["open_time"] <= open_time) &
        (df["close_time"] >= close_time) &
        (df["distance"] <= distance)
    ]

    if filtered.empty:
        st.error("❌ ไม่มีสถานที่ติวที่ตรงกับเงื่อนไขของคุณ")
    elif show_recommendation:
        # เตรียมข้อมูลสำหรับ KNN
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

        # แสดงผลลัพธ์แบบแนวนอน พร้อมปุ่มเลือก
        st.subheader("📍 สถานที่แนะนำ:")
        selected_place = None
        cols = st.columns(len(indices[0]))
        for col, idx in zip(cols, indices[0]):
            place = filtered.iloc[idx]
            with col:
                st.markdown(f"""
                #### {place['name']}
                - ระยะทาง: {place['distance']} กม.
                - เวลาเปิด-ปิด: {place['open_time']} - {place['close_time']}
                - แอร์: {'มี' if place['air_conditioned'] else 'ไม่มี'}
                - ห้องส่วนตัว: {'มี' if place['private_room'] else 'ไม่มี'}
                - 🌐 ดูแผนที่
                """)
                if st.button(f"✅ เลือก {place['name']}", key=place['name']):
                    selected_place = place['name']

        if selected_place:
            st.success(f"คุณเลือกสถานที่: {selected_place}")
        else:
            st.info("คุณยังไม่ได้เลือกสถานที่ใด")
    else:
        st.info("คุณเลือกไม่แสดงสถานที่แนะนำ")

