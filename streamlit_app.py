import streamlit as st
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MinMaxScaler
import webbrowser

# โหลดข้อมูลจากไฟล์ Excel
df = pd.read_excel("spot server.xlsx", engine="openpyxl")

# ส่วนหัวของแอป
st.title("🔍 ระบบแนะนำสถานที่ติวที่เหมาะสม")

# รับค่าจากผู้ใช้ผ่าน widgets
open_time = st.slider("เปิดไม่เกิน (ชั่วโมง)", 0, 24, 8)
close_time = st.slider("ปิดไม่ต่ำกว่า (ชั่วโมง)", 0, 24, 16)
distance = st.slider("ระยะทาง (กม.)", 0.5, 6.0, 1.0)
air = st.radio("แอร์", ["ต้องการ", "ไม่ต้องการ"]) == "ต้องการ"
private = st.radio("ห้องส่วนตัว", ["ต้องการ", "ไม่ต้องการ"]) == "ต้องการ"

# ตัวแปร session state สำหรับการเลือก
if "selected_place" not in st.session_state:
    st.session_state.selected_place = None
if "confirmed" not in st.session_state:
    st.session_state.confirmed = False
if "declined" not in st.session_state:
    st.session_state.declined = False

# เมื่อผู้ใช้กดปุ่มค้นหา
if st.button("🔍 ค้นหาสถานที่ติว"):
    st.session_state.selected_place = None
    st.session_state.confirmed = False
    st.session_state.declined = False

    filtered = df[
        (df["open_time"] <= open_time) &
        (df["close_time"] >= close_time) &
        (df["distance"] <= distance)
    ]

    if filtered.empty:
        st.error("❌ ไม่มีสถานที่ติวที่ตรงกับเงื่อนไขของคุณ")
    else:
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

        st.subheader("📍 สถานที่แนะนำ:")
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
                """)
                if st.button(f"✅ เลือก {place['name']}", key=place['name']):
                    st.session_state.selected_place = place
                    st.session_state.confirmed = False
                    st.session_state.declined = False

# ถ้ามีการเลือกสถานที่
if st.session_state.selected_place:
    st.markdown("---")
    st.subheader("คุณต้องการเลือกสถานที่ที่แนะนำหรือไม่?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ ยืนยันการเลือกสถานที่"):
            st.session_state.confirmed = True
            st.session_state.declined = False
    with col2:
        if st.button("❌ ยังไม่ต้องการเลือก"):
            st.session_state.declined = True
            st.session_state.confirmed = False

# แสดงผลลัพธ์หลังการยืนยัน
if st.session_state.confirmed and st.session_state.selected_place is not None:
    place = st.session_state.selected_place
    lat = place['latitude']
    lon = place['longitude']
    map_url = f"https://www.google.com/maps?q={lat},{lon}"
    st.success(f"คุณเลือกสถานที่: {place['name']}")
    st.markdown(f"[🌐 เปิดแผนที่ Google Maps]({map_url})")
    st.markdown(f"<meta http-equiv='refresh' content='0; url={map_url}'>", unsafe_allow_html=True)

elif st.session_state.declined:
    st.info("คุณเลือกไม่ต้องการเลือกสถานที่ใด")

