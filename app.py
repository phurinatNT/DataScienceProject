from pathlib import Path

import joblib
import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Hotel Cancellation Predictor",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded",
)

MODEL_PATH = Path(__file__).resolve().parent / "hotel_model.pkl"

st.markdown(
    """
    <style>
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #f7fbff 0%, #eef4ff 52%, #f9fbff 100%);
    }
    [data-testid="stHeader"] { background: rgba(0, 0, 0, 0); }
    .block-container {
        max-width: 1180px;
        padding-top: 2.5rem;
        padding-bottom: 3rem;
    }
    .hero {
        padding: 1.7rem 2rem;
        border-radius: 24px;
        color: white;
        background: linear-gradient(120deg, #123b68 0%, #176b87 55%, #24a19a 100%);
        box-shadow: 0 18px 45px rgba(18, 59, 104, 0.18);
        margin-bottom: 1.5rem;
    }
    .hero h1 {
        margin: 0 0 0.35rem;
        font-size: clamp(1.8rem, 4vw, 2.8rem);
        letter-spacing: -0.03em;
    }
    .hero p { margin: 0; opacity: 0.9; font-size: 1.05rem; }
    .section-card {
        padding: 1.25rem 1.35rem 0.7rem;
        border: 1px solid #dbe7f4;
        border-radius: 18px;
        background: rgba(255, 255, 255, 0.86);
        box-shadow: 0 8px 25px rgba(39, 74, 112, 0.07);
    }
    .section-card h3 { margin-top: 0; color: #123b68; }
    div.stButton > button {
        border: 0;
        border-radius: 12px;
        min-height: 3rem;
        font-weight: 700;
        background: linear-gradient(90deg, #176b87, #24a19a);
    }
    div.stButton > button:hover { border: 0; filter: brightness(1.05); }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource(show_spinner=False)
def load_model():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"ไม่พบไฟล์โมเดล: {MODEL_PATH.name}")
    return joblib.load(MODEL_PATH)


st.markdown(
    """
    <div class="hero">
        <h1>🏨 Hotel Cancellation Prediction</h1>
        <p>ประเมินแนวโน้มการยกเลิกการจอง เพื่อช่วยวางแผนการดูแลลูกค้าได้อย่างมั่นใจมากขึ้น</p>
    </div>
    """,
    unsafe_allow_html=True,
)

try:
    model = load_model()
except FileNotFoundError as error:
    st.error(str(error))
    st.info("โปรดวางไฟล์ hotel_model.pkl ไว้ในโฟลเดอร์เดียวกับ app.py แล้วลองเปิดแอปใหม่")
    st.stop()

with st.sidebar:
    st.markdown("### วิธีใช้งาน")
    st.markdown(
        "กรอกข้อมูลการจองให้ครบ แล้วกด **ประเมินความเสี่ยง** "
        "ระบบจะแสดงความน่าจะเป็นและคำแนะนำเบื้องต้น"
    )
    st.divider()
    st.caption("โมเดล: Random Forest pipeline")
    st.caption("ผลลัพธ์ใช้เพื่อประกอบการตัดสินใจ ไม่ใช่การรับประกัน")

input_col, result_col = st.columns([1.05, 0.95], gap="large")

with input_col:
    st.markdown('<div class="section-card"><h3>ข้อมูลการจอง</h3>', unsafe_allow_html=True)
    with st.form("booking_form"):
        lead_days = st.number_input(
            "จำนวนวันที่จองล่วงหน้า (Lead days)",
            min_value=0,
            max_value=120,
            value=30,
            help="จำนวนวันตั้งแต่วันที่จองจนถึงวันเข้าพัก",
        )
        nights = st.number_input("จำนวนคืน (Nights)", min_value=1, max_value=30, value=2)
        guests = st.number_input("จำนวนผู้เข้าพัก (Guests)", min_value=1, max_value=20, value=2)
        special_requests = st.number_input(
            "จำนวนคำขอพิเศษ (Special requests)",
            min_value=0,
            max_value=20,
            value=0,
        )
        deposit_paid = st.selectbox("จ่ายมัดจำแล้วหรือไม่", ["Yes", "No"])
        room_type = st.selectbox("ประเภทห้อง", ["Standard", "Deluxe", "Family"])
        submitted = st.form_submit_button(
            "🔍 ประเมินความเสี่ยงการยกเลิก", use_container_width=True
        )
    st.markdown("</div>", unsafe_allow_html=True)

with result_col:
    st.markdown('<div class="section-card"><h3>ผลการประเมิน</h3>', unsafe_allow_html=True)
    if not submitted:
        st.info("กรอกข้อมูลทางซ้าย แล้วกดปุ่มเพื่อดูผลการประเมิน")
    elif not hasattr(model, "predict_proba"):
        st.error("โมเดลนี้ไม่รองรับการคำนวณความน่าจะเป็น (predict_proba)")
    else:
        row = pd.DataFrame([{
            "lead_days": lead_days,
            "nights": nights,
            "guests": guests,
            "special_requests": special_requests,
            "deposit_paid": deposit_paid,
            "room_type": room_type,
        }])
        pred = int(model.predict(row)[0])
        prob = min(max(float(model.predict_proba(row)[0, 1]), 0.0), 1.0)

        st.metric("โอกาสยกเลิกการจอง", f"{prob:.1%}")
        st.progress(prob)
        if pred == 1:
            st.warning(
                "⚠️ **มีแนวโน้มยกเลิกการจอง**\n\n"
                "แนะนำให้ติดตามหรือยืนยันการจองกับลูกค้าเพิ่มเติม"
            )
        else:
            st.success(
                "✅ **มีแนวโน้มไม่ยกเลิกการจอง**\n\n"
                "การจองมีสัญญาณความเสี่ยงอยู่ในระดับต่ำจากข้อมูลที่ให้"
            )
        st.caption(
            "ผลลัพธ์เป็นการคาดการณ์จากข้อมูลในชุดฝึก "
            "ไม่ใช่การรับประกันพฤติกรรมของลูกค้า"
        )
    st.markdown("</div>", unsafe_allow_html=True)
