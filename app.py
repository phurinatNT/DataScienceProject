import streamlit as st
import pandas as pd
import joblib

st.set_page_config(page_title="Hotel Cancellation Predictor", page_icon="🏨", layout="centered")

@st.cache_resource
def load_model():
    return joblib.load("hotel_model.pkl")

model = load_model()

st.title("🏨 Hotel Cancellation Prediction")
st.caption("ทำนายแนวโน้มการยกเลิกการจองโรงแรมด้วย Machine Learning")

lead_days = st.number_input("จำนวนวันที่จองล่วงหน้า (Lead days)", min_value=0, max_value=120, value=30)
nights = st.number_input("จำนวนคืน (Nights)", min_value=1, max_value=30, value=2)
guests = st.number_input("จำนวนผู้เข้าพัก (Guests)", min_value=1, max_value=20, value=2)
special_requests = st.number_input("จำนวนคำขอพิเศษ (Special requests)", min_value=0, max_value=20, value=0)
deposit_paid = st.selectbox("จ่ายมัดจำแล้วหรือไม่", ["Yes", "No"])
room_type = st.selectbox("ประเภทห้อง", ["Standard", "Deluxe", "Family"])

if st.button("🔍 Predict", use_container_width=True):
    row = pd.DataFrame([{
        "lead_days": lead_days,
        "nights": nights,
        "guests": guests,
        "special_requests": special_requests,
        "deposit_paid": deposit_paid,
        "room_type": room_type
    }])
    pred = int(model.predict(row)[0])
    prob = float(model.predict_proba(row)[0, 1])

    st.metric("Cancellation probability", f"{prob:.1%}")
    if pred == 1:
        st.warning("⚠️ โมเดลประเมินว่า: มีแนวโน้มยกเลิกการจอง")
    else:
        st.success("✅ โมเดลประเมินว่า: มีแนวโน้มไม่ยกเลิกการจอง")

    st.progress(min(max(prob, 0.0), 1.0))
    st.caption("ผลลัพธ์เป็นการคาดการณ์จากข้อมูลในชุดฝึก ไม่ใช่การรับประกันพฤติกรรมของลูกค้า")
