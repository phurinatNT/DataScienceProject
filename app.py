from pathlib import Path
import json
import pandas as pd
import streamlit as st
from model_utils import load_model, predict

ROOT = Path(__file__).resolve().parent
st.set_page_config(page_title='StayWise | ประเมินการยกเลิกการจอง', page_icon='🏨', layout='wide', initial_sidebar_state='expanded')
# Embedded styles keep the deployed interface in sync with this app version.
APP_CSS = '<style>\n@import url(\'https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Thai:wght@400;500;600;700&family=Inter:wght@400;500;600;700&display=swap\');\n:root{--ink:#172b46;--muted:#475569;--blue:#185adb;--line:#dbe3ef;--surface:#fff;--canvas:#f3f6fc}\nhtml,body,.stApp,input,button,textarea{font-family:Inter,\'IBM Plex Sans Thai\',Tahoma,sans-serif}\n.stApp,[data-testid="stMain"]{background:var(--canvas);color:var(--ink);color-scheme:light}\n/* Reserve space for the real Streamlit toolbar, including on narrow screens. */\n[data-testid="stMainBlockContainer"],.block-container{padding-top:6rem!important;padding-bottom:3rem!important;max-width:1480px}\nheader[data-testid="stHeader"]{background:#fff!important;border-bottom:1px solid var(--line);color:var(--ink)!important}\nheader[data-testid="stHeader"] button,header[data-testid="stHeader"] svg,header[data-testid="stHeader"] p{color:var(--ink)!important}\nh1,h2,h3{font-family:Inter,\'IBM Plex Sans Thai\',Tahoma,sans-serif!important;color:var(--ink);line-height:1.5!important;overflow-wrap:anywhere}\nh2{font-size:1.7rem!important}h3{font-size:1.12rem!important}\n[data-testid="stMain"] [data-testid="stMarkdownContainer"]{color:var(--ink)}\n[data-testid="stMain"] [data-testid="stCaptionContainer"] p{color:var(--muted)!important;font-size:14px!important;line-height:1.8}\n[data-testid="stSidebar"]{background:#11233d;color:#f8fafc;color-scheme:dark;border-right:1px solid #253d5c}\n[data-testid="stSidebar"] [data-testid="stMarkdownContainer"],[data-testid="stSidebar"] p,[data-testid="stSidebar"] label,[data-testid="stSidebar"] button{color:#f1f5f9!important}\n[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p{color:#bacce3!important}\n[data-testid="stSidebar"] [data-testid="stRadio"] label{padding:14px 10px;margin:5px 0;border-radius:10px}\n[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked){background:#253f63;border:1px solid #5778a1}\n.brand{display:flex;align-items:center;gap:12px;color:white;font-size:28px;font-weight:700;margin:12px 0 40px}.brandmark{display:grid;place-items:center;flex-shrink:0;width:48px;height:48px;background:#2368dd;border-radius:14px;color:#fff}.brand small{display:block;font-size:10px;letter-spacing:1px;color:#c3d2e6;font-weight:500;margin-top:3px}.side-note{margin-top:70px;padding-top:24px;border-top:1px solid #38506e}.side-note small{font-size:11px;letter-spacing:1.2px;color:#9fcaff}.side-note p{font-size:16px;line-height:1.9}.side-note span{font-size:14px;color:#c3d2e6}\n.topline{display:flex;align-items:center;flex-wrap:wrap;gap:10px;padding:0 0 18px;border-bottom:1px solid var(--line);color:#475569;font-size:13px;margin-bottom:26px;line-height:1.8}.topline span{color:#526780}.topline b{margin-left:auto;font-size:12px;font-weight:600;color:#204b8c;background:#e5edfb;padding:5px 12px;border-radius:30px}\n.heading{margin-bottom:28px}.eyebrow{font-size:12px;letter-spacing:1.5px;font-weight:700;color:#2257a0}.heading h1{font-size:clamp(1.8rem,2.6vw,2.6rem);font-weight:700;padding:12px 0 8px;margin:0;letter-spacing:-.5px}.heading h1 span{color:var(--blue)}.heading p{font-size:16px;color:var(--muted);line-height:1.9;margin:0}\n.stat{background:white;border:1px solid var(--line);border-radius:16px;padding:22px 24px;min-height:146px;box-shadow:0 4px 20px #172b4605;border-top:4px solid #90b4f1}.stat>span{display:block;font-size:14px;color:#475569}.stat strong{display:block;color:var(--ink);font-size:clamp(1.4rem,2vw,1.85rem);line-height:1.7;margin:5px 0;overflow-wrap:anywhere}.stat small{font-size:13px;color:#475569}\n[data-testid="stLayoutWrapper"]:has(> [data-testid="stVerticalBlock"][style*="border"]){background:white;border-radius:16px}\n.st-key-booking_card,.st-key-result_card{background:white!important;border:1px solid var(--line)!important;border-radius:20px!important;padding:26px!important;box-shadow:0 8px 30px #172b4608}.st-key-result_card{border-top:4px solid var(--blue)!important}\n.paneltitle{font-size:21px;font-weight:700;display:flex;align-items:center;gap:12px;margin-bottom:10px}.paneltitle>span{font-size:13px;background:#eaf0fc;color:#2257a0;border-radius:8px;padding:7px 10px}\n[data-testid="stForm"]{border:0!important;padding:0!important;background:white!important}\n[data-testid="stMain"] [data-testid="stWidgetLabel"] p{color:var(--ink)!important;font-size:15px!important;font-weight:600;line-height:1.7}\n[data-testid="stNumberInput"] [data-baseweb="input"],[data-testid="stNumberInput"] [data-baseweb="base-input"],[data-testid="stNumberInput"] input{background:#f5f8fd!important;color:var(--ink)!important;-webkit-text-fill-color:var(--ink)!important;font-size:16px!important}\n[data-testid="stNumberInput"] [data-baseweb="input"]{border-color:#aebdd0!important;border-radius:10px!important}\n[data-testid="stNumberInput"] button{background:#e8eef8!important;color:#214b83!important}\n[data-testid="stSelectbox"] [data-baseweb="select"]>div{background:#f5f8fd!important;color:var(--ink)!important;border-color:#aebdd0!important;border-radius:10px!important;min-height:46px}\n[data-testid="stSelectbox"] span,[data-testid="stSelectbox"] input{color:var(--ink)!important;-webkit-text-fill-color:var(--ink)!important}\n[data-testid="stSelectbox"] svg{fill:#334155!important}\n[data-baseweb="popover"] [role="listbox"],[data-baseweb="popover"] [role="option"]{background:#fff!important;color:#172b46!important}\n[data-baseweb="popover"] [role="option"]:hover,[data-baseweb="popover"] [role="option"][aria-selected="true"]{background:#e8effc!important;color:#172b46!important}\n[data-testid="stMain"] button[kind="secondary"]{background:white!important;color:#214b83!important;border:1px solid #aebdd0!important}\n[data-testid="stMain"] button[kind="secondary"] p{color:#214b83!important}\n[data-testid="stMain"] button[kind="primary"]{background:var(--blue)!important;color:white!important;border-color:var(--blue)!important;box-shadow:0 5px 14px #185adb20}\n[data-testid="stMain"] button[kind="primary"] p{color:white!important}\n.stButton button,.stFormSubmitButton button{min-height:48px;border-radius:10px!important;font-weight:600}\ninput:focus-visible,button:focus-visible,summary:focus-visible{outline:3px solid #5389e6!important;outline-offset:3px}\n.sw-empty{text-align:center;padding:42px 12px}.sw-empty-icon{width:80px;height:80px;display:grid;place-items:center;margin:0 auto 24px;border-radius:24px;background:#eaf0fc;color:#245db9;font-size:42px}.sw-empty-title{font-size:21px!important;font-weight:600;color:var(--ink)!important;line-height:1.8}.sw-empty-description{font-size:16px!important;color:var(--muted)!important;line-height:1.9}.sw-empty-meta{font-size:13px!important;color:#475569!important;margin-top:28px!important}\n.modelnote{padding:20px;border:1px solid #cddbf1;background:#edf3fd;border-radius:12px;margin-top:20px;color:#214b83}.modelnote strong{font-size:15px}.modelnote p{font-size:14px;color:#334b6b;line-height:1.9;margin:8px 0 0}.resultlabel{color:#475569;font-size:14px}\n[data-testid="stMetricValue"]{color:var(--ink)!important}[data-testid="stMetricLabel"] p{color:#475569!important}\n[data-testid="stAlert"]{background:#edf3fd!important;border:1px solid #cddbf1!important;color:#233e62!important}[data-testid="stAlert"] p,[data-testid="stAlert"] svg{color:#233e62!important}\n[data-testid="stExpander"]{background:white!important;border-color:var(--line)!important;border-radius:12px!important}[data-testid="stExpander"] summary{color:var(--ink)!important}\n[data-testid="stCode"],[data-testid="stCode"] pre,[data-testid="stCode"] code{background:#edf2f8!important;color:#172b46!important}\n.insight{background:#e9f1fd;border:1px solid #c8d9f2;border-left:4px solid var(--blue);border-radius:12px;padding:23px 26px;margin-top:28px;color:#204573}.insight strong{font-size:16px}.insight p{font-size:14px;color:#334b6b;line-height:1.9;margin:7px 0 0}\n.sw-table{width:100%;overflow-x:auto;background:white;border:1px solid #dbe3ef;border-radius:12px;margin:10px 0 18px;color:#172b46;color-scheme:light}.sw-table table{border-collapse:collapse;width:100%;font-size:14px;line-height:1.8}.sw-table th{background:#eaf0f9;color:#213e65;font-weight:600;text-align:left!important;padding:14px 16px;white-space:nowrap}.sw-table td{padding:14px 16px;color:#172b46;border-top:1px solid #e1e7f0;min-width:80px}.sw-table tr:nth-child(even) td{background:#f6f8fc}.sw-table tr:hover td{background:#edf3fd}\n.footer{display:flex;justify-content:space-between;flex-wrap:wrap;gap:16px;border-top:1px solid var(--line);padding-top:24px;margin-top:36px;font-size:13px;color:#475569;line-height:1.8}\n@media(max-width:768px){[data-testid="stMainBlockContainer"],.block-container{padding:6rem 1rem 2rem!important}.heading h1{font-size:1.85rem}.topline b{margin-left:0}.stat{min-height:125px;padding:18px}.st-key-booking_card,.st-key-result_card{padding:18px!important}.sw-empty{padding:28px 8px}.brand{margin-bottom:26px}.side-note{margin-top:35px}.footer{flex-direction:column}}\n@media(prefers-reduced-motion:reduce){*{scroll-behavior:auto!important;transition:none!important}}\n\n\n/* V5: semantic colors, large percentages, and a distinct dashboard layout. */\n.heading{padding:28px 32px 30px;border-radius:22px;background:linear-gradient(120deg,#102746,#1d426e);margin-bottom:26px;border:1px solid #284d76}\n.heading h1{color:#fff!important}.heading h1 span{color:#8dd9ff}.heading .eyebrow{color:#a9d7ff}.heading p{color:#dce8f7!important}\n.outcome-section{margin:12px 0 26px;background:white;border:1px solid #dbe3ef;border-radius:22px;padding:28px}\n.section-intro{display:flex;justify-content:space-between;align-items:flex-start;gap:20px;margin-bottom:24px}.section-intro h2{font-size:1.5rem!important;margin:8px 0!important;padding:0!important}.section-intro p{margin:0;color:#475569;font-size:15px}.release-pill{white-space:nowrap;background:#eaf0fc;border:1px solid #c2d2ef;border-radius:24px;color:#204573;padding:7px 12px;font-size:12px}\n.outcome-grid,.comparison-grid{display:grid;grid-template-columns:1fr 1fr;gap:22px}.outcome-card{border-radius:18px;padding:26px;border:1px solid}.outcome-card.keep{background:#edf9f3;border-color:#a8d9c0}.outcome-card.cancel{background:#fff0f2;border-color:#efb7c0}.keep{--semantic:#08734f;--track:#cdebdc}.cancel{--semantic:#b42338;--track:#f6d3da}\n.status-tag{display:inline-flex;align-items:center;border:1px solid currentColor;border-radius:24px;padding:6px 12px;font-size:15px;font-weight:600;color:var(--semantic)}.outcome-number{font-size:clamp(2.8rem,5vw,4.5rem);font-weight:700;letter-spacing:-2px;color:var(--semantic);line-height:1.4;margin-top:14px}.outcome-number span{font-size:.45em;margin-left:5px;letter-spacing:0}.outcome-card p{font-size:16px;color:#334155;margin:4px 0 18px}.outcome-card strong{font-size:20px}.outcome-card small{display:block;font-size:13px;color:#475569;margin-top:10px}.outcome-track,.compare-track{background:var(--track);border-radius:20px;overflow:hidden;height:10px}.outcome-track>div,.compare-track>div{height:100%;background:var(--semantic);border-radius:20px}\n.distribution{display:flex;border-radius:10px;overflow:hidden;margin-top:24px;min-height:44px}.distribution>div{display:flex;align-items:center;justify-content:center;color:white!important;font-size:14px;font-weight:600;padding:10px 4px;box-sizing:border-box}.keep-segment{background:#08734f}.cancel-segment{background:#b42338}\n.chart-footnote{font-size:14px!important;color:#475569!important;line-height:1.9!important;margin:18px 0 0!important}.comparison-grid{margin-bottom:28px}.comparison-card{background:white;border:1px solid #dbe3ef;border-radius:20px;padding:26px}.comparison-card h3{font-size:1.25rem!important;margin:12px 0!important;padding:0!important}.comparison-card>p{color:#475569;font-size:15px;line-height:1.9}.compare-row{margin-top:25px}.compare-label{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:10px;color:#172b46;font-size:15px}.compare-label strong{font-size:24px;color:var(--semantic);white-space:nowrap}.compare-track{height:14px}.compare-row small{display:block;color:#475569;font-size:13px;margin-top:8px}.scale-note{color:#475569;font-size:12px;margin-top:24px;padding-top:14px;border-top:1px solid #dbe3ef}\n@media(max-width:850px){.outcome-grid,.comparison-grid{grid-template-columns:1fr}.section-intro{flex-wrap:wrap}.outcome-section,.comparison-card{padding:20px}.heading{padding:23px}.distribution>div{font-size:11px}.outcome-number{font-size:3.5rem}}\n</style>\n'
st.markdown(APP_CSS, unsafe_allow_html=True)

@st.cache_data
def data_source():
    raw = pd.read_excel(ROOT / 'hotel_dataset.xlsx', sheet_name='Raw_Data')
    clean = raw.drop_duplicates().copy()
    for column in ['deposit_paid', 'room_type']:
        clean[column] = clean[column].str.strip().str.lower()
    return raw, clean

@st.cache_data
def model_source():
    return load_model()

@st.cache_data
def training_results():
    """โหลดค่า CV F1 จากผลการทดลอง Decision Tree และ KNN"""
    path = ROOT / 'gridsearch_results.json'
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return None

try:
    model = model_source()
except (OSError, ValueError) as error:
    st.error('โหลด model.json ไม่สำเร็จ กรุณาตรวจว่าอัปโหลดไฟล์โมเดลพร้อม app.py แล้ว')
    st.stop()

def heading(kicker, title, description):
    st.markdown(f'<div class="heading"><div class="eyebrow">{kicker}</div><h1>{title}</h1><p>{description}</p></div>', unsafe_allow_html=True)

def readable_table(frame, show_index=False):
    # Small read-only tables use HTML so their colors do not depend on canvas theme.
    st.markdown('<div class="sw-table">' + frame.to_html(index=show_index, escape=True, border=0) + '</div>', unsafe_allow_html=True)

def stats(items):
    cols = st.columns(len(items))
    for col, (label, value, note) in zip(cols, items):
        with col:
            st.markdown(f'<div class="stat"><span>{label}</span><strong>{value}</strong><small>{note}</small></div>', unsafe_allow_html=True)

DEFAULTS = {'lead_days': 60.0, 'nights': 3, 'guests': 2, 'special_requests': 1, 'deposit': 'จ่ายมัดจำแล้ว', 'room': 'Standard — ห้องมาตรฐาน'}
def set_defaults(sample=False):
    values = DEFAULTS.copy()
    if sample:
        values.update(lead_days=90.0, nights=5, guests=2, special_requests=0, deposit='ยังไม่จ่ายมัดจำ')
    for key, value in values.items():
        st.session_state[key] = value
    st.session_state.pop('assessment', None)
    st.session_state.pop('assessed_inputs', None)

for key, value in DEFAULTS.items():
    # Reassign on every page to preserve widget values when navigation hides them.
    st.session_state[key] = st.session_state.get(key, value)

with st.sidebar:
    st.markdown('<div class="brand"><span class="brandmark">S</span><div>StayWise<small>HOTEL BOOKING INTELLIGENCE</small></div></div>', unsafe_allow_html=True)
    st.caption('พื้นที่ทำงาน')
    page = st.radio('เมนูหลัก', ['ประเมินการจอง', 'สำรวจข้อมูล', 'ผลทดสอบโมเดล'], label_visibility='collapsed', key='page')
    st.markdown('<div class="side-note"><small>DATA SCIENCE PROJECT</small><p>จากข้อมูล สู่การวางแผน<br>การจองที่เข้าใจได้</p><span>ภูริณัฐ สมศรี</span></div>', unsafe_allow_html=True)

st.markdown(f'<div class="topline">Hotel cancellation <span>/</span> {page}<b>StayWise · V5</b></div>', unsafe_allow_html=True)

if page == 'ประเมินการจอง':
    heading('BOOKING RISK ASSESSMENT', 'เข้าใจความเสี่ยงของทุกการจอง</span>', 'กรอกข้อมูลการจอง เพื่อประเมินแนวโน้มการยกเลิกก่อนวันเข้าพัก')
    stats([('ข้อมูลก่อนลบรายการซ้ำ', '1,062', 'การจอง'),('ข้อมูลหลังลบรายการซ้ำ', '1,050', 'การจอง'), ('อัตรายกเลิกใน Dataset', '23.62%', '248 จาก 1,050 รายการ'), ('โมเดลที่ใช้ประเมิน', 'Decision Tree', '6 Features')])
    st.write('')
    left, right = st.columns([1.1, 1], gap='large')
    with left:
        with st.container(border=True, key='booking_card'):
            st.markdown('<div class="paneltitle"><span>01</span> ข้อมูลการจอง</div>', unsafe_allow_html=True)
            st.caption('กรอกข้อมูล 6 ช่องด้านล่าง แล้วกดปุ่มสีน้ำเงินเพื่อประเมิน')
            st.button('ใช้ข้อมูลตัวอย่าง', on_click=set_defaults, args=(True,), key='sample')
            with st.form('booking_form'):
                a, b = st.columns(2)
                with a:
                    lead = st.number_input('1. จองล่วงหน้าก่อนเข้าพัก (วัน)', min_value=0.0, max_value=3650.0, step=1.0, key='lead_days', help='ระยะเวลาตั้งแต่วันที่จองจนถึงวันที่เข้าพัก')
                    st.caption('เช่น จองวันนี้และเข้าพักอีก 30 วัน ให้กรอก 30')
                    guests = st.number_input('3. จำนวนผู้เข้าพัก (คน)', min_value=1, max_value=100, step=1, key='guests')
                    st.caption('จำนวนคนทั้งหมดในการจองนี้ เช่น 2 คน ให้กรอก 2')
                with b:
                    nights = st.number_input('2. จำนวนคืนที่เข้าพัก', min_value=1, max_value=365, step=1, key='nights')
                    st.caption('เช่น เข้าพัก 10 ต.ค. ออก 12 ต.ค. เท่ากับ 2 คืน')
                    requests = st.number_input('4. จำนวนคำขอพิเศษ (รายการ)', min_value=0, max_value=100, step=1, key='special_requests', help='เช่น ขอเตียงเสริม หรือห้องชั้นสูง ถ้าไม่มีให้กรอก 0')
                    st.caption('จำนวนรายการที่ขอเพิ่มเติม เช่น ขอเตียงเสริม 1 รายการ ถ้าไม่มีให้กรอก 0')
                deposit = st.selectbox('5. ลูกค้าจ่ายมัดจำแล้วหรือยัง?', ['จ่ายมัดจำแล้ว', 'ยังไม่จ่ายมัดจำ'], key='deposit')
                st.caption('เลือกสถานะที่ทราบ ณ เวลาประเมิน ไม่ใช่สถานะหลังยกเลิกการจอง')
                room = st.selectbox('6. ประเภทห้องพักที่จอง', ['Standard — ห้องมาตรฐาน', 'Deluxe — ห้องดีลักซ์', 'Family — ห้องครอบครัว'], key='room')
                st.caption('เลือกประเภทห้องตามรายการจอง: มาตรฐาน / ดีลักซ์ / ครอบครัว')
                submitted = st.form_submit_button('ประเมินความเสี่ยงการยกเลิก', type='primary', width='stretch')
            if submitted:
                inputs = {'lead_days': lead, 'nights': nights, 'guests': guests, 'special_requests': requests, 'deposit_paid': 'yes' if deposit == 'จ่ายมัดจำแล้ว' else 'no', 'room_type': room.split(' — ')[0].lower()}
                try:
                    st.session_state['assessment'] = predict(model, inputs)
                    st.session_state['assessed_inputs'] = inputs
                except ValueError as error:
                    st.error(str(error))
            st.button('เริ่มใหม่', on_click=set_defaults, key='reset', width='stretch')
            st.caption('ไม่ต้องกรอกชื่อหรือข้อมูลติดต่อของลูกค้า')
    with right:
        with st.container(border=True, key='result_card'):
            st.markdown('<div class="paneltitle"><span>02</span> ผลการประเมิน</div>', unsafe_allow_html=True)
            result = st.session_state.get('assessment')
            if not result:
                st.markdown('<div class="sw-empty"><span class="sw-empty-icon" aria-hidden="true">◈</span><p class="sw-empty-title">การจองนี้มีความเสี่ยงแค่ไหน?</p><p class="sw-empty-description">กรอกข้อมูลการจอง แล้วกดปุ่ม<br>“ประเมินความเสี่ยงการยกเลิก”</p><p class="sw-empty-meta">Decision Tree · ทดสอบกับข้อมูล 210 รายการ</p></div>', unsafe_allow_html=True)
            else:
                high = bool(result['cancelled'])
                color = '#b42338' if high else '#08734f'
                label = 'มีแนวโน้มยกเลิก' if high else 'มีแนวโน้มไม่ยกเลิก'
                st.markdown(f'<div class="resultlabel">ผลที่โมเดลทำนาย</div><h2 style="color:{color}">{label}</h2>', unsafe_allow_html=True)
                st.metric('คะแนนความเสี่ยงของโมเดล', f'{result["score"] * 100:.1f} / 100')
                st.progress(result['score'])
                st.caption('คะแนนจากโมเดลที่ถ่วงน้ำหนักคลาส ไม่ใช่เปอร์เซ็นต์โอกาสยกเลิกจริง เกณฑ์ตัดสินอยู่ที่คะแนนมากกว่า 50')
                message = 'ควรติดตามยืนยันวันเข้าพักและเงื่อนไขมัดจำกับลูกค้า ไม่ควรยกเลิกการจองแทนลูกค้าจากผลโมเดลเพียงอย่างเดียว' if high else 'ดูแลการจองตามขั้นตอนปกติ และยืนยันก่อนเข้าพักตามนโยบายโรงแรม ผลนี้ไม่ได้รับประกันว่าจะไม่มีการยกเลิก'
                st.info(message)
                st.markdown('**เหตุผลตามเส้นทาง Decision Tree**')
                names = {'num__lead_days': 'วันจองล่วงหน้า', 'num__nights': 'จำนวนคืน', 'num__guests': 'จำนวนผู้เข้าพัก', 'num__special_requests': 'จำนวนคำขอพิเศษ'}
                inputs = st.session_state['assessed_inputs']
                for step in result['path']:
                    if step['feature'] == 'cat__deposit_paid_no':
                        text = 'สถานะมัดจำ: ' + ('จ่ายแล้ว' if inputs['deposit_paid'] == 'yes' else 'ยังไม่จ่าย')
                    else:
                        condition = 'ไม่เกิน' if step['left'] else 'มากกว่า'
                        text = f'{names.get(step["feature"], step["feature"])}: {step["value"]:g} ({condition} {step["threshold"]:g})'
                    st.markdown(f'- {text}')
                if result['outside_training_range']:
                    st.warning('บางค่าอยู่นอกช่วงที่พบใน Dataset ผลทำนายอาจไม่น่าเชื่อถือเท่าข้อมูลที่โมเดลเคยเรียนรู้')
                with st.expander('ข้อมูลที่ใช้ประเมินครั้งล่าสุด'):
                    display = pd.DataFrame([inputs]).rename(columns={'lead_days': 'วันจองล่วงหน้า', 'nights': 'จำนวนคืน', 'guests': 'ผู้เข้าพัก', 'special_requests': 'คำขอพิเศษ', 'deposit_paid': 'มัดจำ', 'room_type': 'ประเภทห้อง'})
                    display['มัดจำ'] = display['มัดจำ'].map({'yes': 'จ่ายแล้ว', 'no': 'ยังไม่จ่าย'})
                    display['ประเภทห้อง'] = display['ประเภทห้อง'].map({'standard': 'มาตรฐาน', 'deluxe': 'ดีลักซ์', 'family': 'ครอบครัว'})
                    readable_table(display)
                st.caption('หากเปลี่ยนข้อมูล กรุณากดประเมินอีกครั้งเพื่ออัปเดตผล')
            st.markdown('<div class="modelnote"><strong>ใช้เป็นข้อมูลประกอบการวางแผน</strong><p>Recall 62% และ Precision 34.07% สำหรับกลุ่มยกเลิก โมเดลยังมีข้อผิดพลาด ควรยืนยันกับลูกค้าก่อนดำเนินการ</p></div>', unsafe_allow_html=True)
    st.markdown('<div class="insight"><strong>มัดจำสัมพันธ์กับการยกเลิกอย่างชัดเจนใน Dataset นี้</strong><p>กลุ่มไม่จ่ายมัดจำยกเลิก 38.24% เทียบกับ 9.25% ของกลุ่มที่จ่ายแล้ว ความสัมพันธ์นี้ไม่ได้ยืนยันเหตุและผล</p></div>', unsafe_allow_html=True)

elif page == 'สำรวจข้อมูล':
    heading('DATASET EXPLORER', 'ภาพรวมการจองโรงแรม</span>', 'หนึ่งแถวแทนการจองโรงแรมหนึ่งรายการ โดย cancelled เป็นตัวแปรเป้าหมาย')
    try:
        raw, data = data_source()
    except (OSError, ValueError) as error:
        st.error('กรุณาอัปโหลด hotel_dataset.xlsx พร้อมโปรเจกต์ และตรวจว่ามีชีต Raw_Data')
        st.stop()
    stats([('ข้อมูลดิบ', f'{len(raw):,}', 'รายการ'), ('แถวซ้ำที่ลบออก', f'{raw.duplicated().sum():,}', 'ซ้ำทั้งแถว'), ('ข้อมูลหลังลบซ้ำ', f'{len(data):,}', '6 Features + Identifier + Target')])
    st.write('')
    total = len(data)
    cancelled = int((data.cancelled == 1).sum())
    kept = int((data.cancelled == 0).sum())
    cancel_pct, keep_pct = cancelled / total * 100, kept / total * 100
    st.markdown(f'''<section class="outcome-section">
<div class="section-intro"><div><span class="eyebrow">BOOKING OVERVIEW</span><h2>การจองทั้งหมด แบ่งเป็นกี่กลุ่ม?</h2><p>สัดส่วนจากข้อมูลหลังลบแถวซ้ำ {total:,} รายการ</p></div><span class="release-pill">ดีไซน์ใหม่ · V5</span></div>
<div class="outcome-grid">
<article class="outcome-card keep"><span class="status-tag">● ไม่ยกเลิกการจอง</span><div class="outcome-number">{keep_pct:.2f}<span>%</span></div><p><strong>{kept:,}</strong> จาก {total:,} รายการ</p><div class="outcome-track"><div style="width:{keep_pct:.4f}%"></div></div><small>การจองที่มี cancelled = 0</small></article>
<article class="outcome-card cancel"><span class="status-tag">● ยกเลิกการจอง</span><div class="outcome-number">{cancel_pct:.2f}<span>%</span></div><p><strong>{cancelled:,}</strong> จาก {total:,} รายการ</p><div class="outcome-track"><div style="width:{cancel_pct:.4f}%"></div></div><small>การจองที่มี cancelled = 1</small></article>
</div><div class="distribution" role="img" aria-label="ไม่ยกเลิก {keep_pct:.2f} เปอร์เซ็นต์ ยกเลิก {cancel_pct:.2f} เปอร์เซ็นต์"><div class="keep-segment" style="width:{keep_pct:.4f}%">ไม่ยกเลิก {keep_pct:.2f}%</div><div class="cancel-segment" style="width:{cancel_pct:.4f}%">ยกเลิก {cancel_pct:.2f}%</div></div>
<p class="chart-footnote">กลุ่มไม่ยกเลิกมีจำนวนมากกว่า จึงต้องพิจารณา Recall และ F1 ร่วมกับ Accuracy</p></section>''', unsafe_allow_html=True)

    def comparison_row(label, value, max_value, unit, tone, note=''):
        width = min(100, value / max_value * 100) if max_value else 0
        return f'<div class="compare-row {tone}"><div class="compare-label"><span>{label}</span><strong>{value:.2f}{unit}</strong></div><div class="compare-track"><div style="width:{width:.4f}%"></div></div><small>{note}</small></div>'

    deposits = data.groupby('deposit_paid').cancelled.agg(['mean', 'count'])
    deposit_rows = ''
    for key, label in [('yes', 'จ่ายมัดจำแล้ว'), ('no', 'ยังไม่จ่ายมัดจำ')]:
        row = deposits.loc[key]
        deposit_rows += comparison_row(label, row['mean'] * 100, 100, '%', 'cancel', f"จากข้อมูล {int(row['count']):,} รายการที่ทราบผลการจอง")
    leads = data.groupby('cancelled').lead_days.mean()
    lead_rows = ''.join(comparison_row(label, float(leads.loc[key]), 100, ' วัน', tone) for key, label, tone in [(0, 'กลุ่มไม่ยกเลิก', 'keep'), (1, 'กลุ่มยกเลิก', 'cancel')])
    st.markdown(f'''<div class="comparison-grid"><section class="comparison-card"><span class="eyebrow">DEPOSIT & CANCELLATION</span><h3>จ่ายมัดจำแล้ว ยกเลิกต่างกันเท่าไร?</h3><p>ตัวเลขด้านล่างคือ <b>อัตรายกเลิก</b> ภายในแต่ละกลุ่มมัดจำ</p>{deposit_rows}<div class="scale-note">ความยาวแท่ง: 0–100% · สีแดงหมายถึงอัตรายกเลิก</div><p class="chart-footnote">ไม่นับสถานะมัดจำที่ว่าง ความสัมพันธ์นี้ไม่ได้ยืนยันเหตุและผล</p></section><section class="comparison-card"><span class="eyebrow">BOOKING LEAD TIME</span><h3>แต่ละกลุ่มจองล่วงหน้ากี่วัน?</h3><p>เปรียบเทียบ <b>จำนวนวันเฉลี่ย</b> ก่อนวันเข้าพัก</p>{lead_rows}<div class="scale-note">ความยาวแท่ง: 0–100 วัน · ตัวเลขเป็นวัน ไม่ใช่เปอร์เซ็นต์</div><p class="chart-footnote">คำนวณจากวันที่ไม่ว่างก่อนเติมค่า เพื่ออธิบายข้อมูลที่พบจริง</p></section></div>''', unsafe_allow_html=True)
    with st.container(border=True):
        st.subheader('ความหมายของ Feature')
        dictionary = pd.DataFrame([('booking_id', 'รหัสการจอง', 'Identifier — ตัดออกจากโมเดล'), ('lead_days', 'วันจองล่วงหน้า', 'Feature ตัวเลข'), ('nights', 'จำนวนคืน', 'Feature ตัวเลขจำนวนเต็ม'), ('guests', 'จำนวนผู้เข้าพัก', 'Feature ตัวเลขจำนวนเต็ม'), ('special_requests', 'จำนวนคำขอพิเศษ', 'Feature ตัวเลขจำนวนเต็ม'), ('deposit_paid', 'สถานะมัดจำ', 'Feature หมวดหมู่ Yes/No'), ('room_type', 'ประเภทห้อง', 'Feature หมวดหมู่ไม่มีลำดับ'), ('cancelled', '0 = ไม่ยกเลิก / 1 = ยกเลิก', 'Target')], columns=['คอลัมน์', 'ความหมาย', 'บทบาท'])
        readable_table(dictionary)
    with st.expander('การตรวจคุณภาพและเตรียมข้อมูล'):
        quality = pd.DataFrame({'คอลัมน์': raw.columns, 'ค่าว่างในข้อมูลดิบ': raw.isna().sum().values, 'ชนิดข้อมูล': raw.dtypes.astype(str).values})
        readable_table(quality)
        st.markdown('''1. ลบแถวซ้ำ 12 แถวก่อนแบ่ง Train/Test
2. ตัดช่องว่างและปรับตัวพิมพ์ในสถานะมัดจำและประเภทห้อง
3. เปลี่ยนค่าทศนิยมในจำนวนคืน 2 ค่า ผู้เข้าพัก 1 ค่า และคำขอพิเศษ 1 ค่า เป็นค่าว่าง
4. แบ่งข้อมูลแบบ Stratified 80/20 จากนั้นเติม Median/Mode โดยเรียนรู้จาก Train เท่านั้น
5. ทำ One-Hot Encoding สำหรับหมวดหมู่ ใช้ StandardScaler สำหรับ KNN
6. ใช้ Features ทั้ง 6 ตัวหลังตัด booking_id ไม่ใช้ cancelled เป็นข้อมูลนำเข้า

lead_days สูงสุด 182.4 วันยังเก็บไว้ เพราะอาจเกิดขึ้นจริง ควรตรวจต้นทางก่อนลบหรือแก้ไข''')

else:
    heading('MODEL EVALUATION', 'ทำนายได้ดีแค่ไหน<span>?</span>', 'ผลทดลองใหม่จากไฟล์แนบ แยก Test ออกจากการฝึกและเลือกพารามิเตอร์')
    training = training_results()
    cv_scores = {}
    if training:
        cv_scores = {
            name: details['cv_mean_f1']
            for name, details in training.get('models', {}).items()
            if 'cv_mean_f1' in details
        }
    cv_average = sum(cv_scores.values()) / len(cv_scores) if cv_scores else None
    selected_cv = cv_scores.get(training.get('selected_by_cv')) if training else None
    stats([
        ('Train', '840', '80% ของข้อมูล'),
        ('Test', '210', '20% '),
        ('โมเดลที่เลือก', training.get('selected_by_cv', 'Decision Tree') if training else 'Decision Tree', f'CV F1 {selected_cv * 100:.2f}%' if selected_cv is not None else 'เลือกตาม F1'),
    ])
    st.write('')
    with st.container(border=True):
        st.subheader('เปรียบเทียบผลบนชุด Test')
        scores = pd.DataFrame([
            ['Decision Tree ', '53.41%', '62.38%', '34.07%', '62.00%', '43.97%'],
            ['KNN', '35.11%', '73.81%', '40.74%', '22.00%', '28.57%'],
        ], columns=['โมเดล', 'CV F1 เฉลี่ย', 'Accuracy', 'Precision', 'Recall', 'F1'])
        readable_table(scores)
        st.caption('CV F1 คือค่าเฉลี่ยจาก Stratified 5-Fold บน Train ส่วน Precision, Recall และ F1 เป็นค่าของกลุ่ม cancelled = 1 บน Test')
    a, b = st.columns(2, gap='large')
    with a, st.container(border=True):
        st.subheader('Confusion Matrix: Decision Tree')
        cm = pd.DataFrame(model['metrics']['confusion'], index=['ไม่ยกเลิกจริง', 'ยกเลิกจริง'], columns=['ทายว่าไม่ยกเลิก', 'ทายว่ายกเลิก'])
        readable_table(cm, show_index=True)
        st.info('ตรวจพบผู้ยกเลิกจริง 31 จาก 50 รายการ พลาด 19 รายการ และแจ้งเตือนผิด 60 รายการ')
    with b, st.container(border=True):
        st.subheader('Accuracy สูง ยังจับการยกเลิกได้น้อย')
        st.write('ทายว่าไม่ยกเลิกทุกคนก็ได้ Accuracy 76.19% แต่ตรวจพบผู้ยกเลิกไม่ได้เลย Decision Tree จับผู้ยกเลิกได้มากกว่า KNN ในการทดลองนี้ แต่ยังมีการแจ้งเตือนผิดจำนวนมาก')
        st.markdown('**Recall:** จับผู้ยกเลิกจริงได้กี่เปอร์เซ็นต์\n\n**Precision:** คนที่ทายว่าจะยกเลิก ยกเลิกจริงกี่เปอร์เซ็นต์\n\n**F1:** ประเมิน Precision และ Recall ร่วมกัน')
    with st.expander('วิธีทดลองและข้อจำกัด'):
        st.write('Train/Test แบบ stratify=y, random_state=42 ปรับพารามิเตอร์ด้วย GridSearchCV แบบ Stratified 5-Fold บน Train โดยเลือก F1 ของกลุ่มยกเลิก ทำการเติมค่า Encoding และ Scaling ภายใน Pipeline เพื่อป้องกัน Data Leakage')
        st.code('Decision Tree: max_depth=3, min_samples_leaf=1, class_weight="balanced"\nKNN: n_neighbors=5, weights="uniform", metric="manhattan"', language='text')
        st.write('โมเดลยังไม่แม่นยำเพียงพอสำหรับตัดสินใจแทนโรงแรม ข้อมูลสองกลุ่มไม่สมดุล Features ยังแยกสองกลุ่มไม่ชัด และผลทดสอบครั้งเดียวไม่รับประกันผลกับข้อมูลอนาคต คะแนนยังไม่ผ่านการปรับเทียบความน่าจะเป็น')

st.markdown('<div class="footer">StayWise / Hotel Cancellation Classification · UI 5.0 <span>จัดทำโดย ภูริณัฐ สมศรี</span></div>', unsafe_allow_html=True)
