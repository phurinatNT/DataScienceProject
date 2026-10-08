from pathlib import Path
import pandas as pd
import altair as alt
import streamlit as st
from model_utils import load_model, predict

ROOT = Path(__file__).resolve().parent
st.set_page_config(page_title='StayWise | ประเมินการยกเลิกการจอง', page_icon='🏨', layout='wide', initial_sidebar_state='expanded')
st.markdown((ROOT / 'style.css').read_text(encoding='utf-8'), unsafe_allow_html=True)

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

try:
    model = model_source()
except (OSError, ValueError) as error:
    st.error('โหลด model.json ไม่สำเร็จ กรุณาตรวจว่าอัปโหลดไฟล์โมเดลพร้อม app.py แล้ว')
    st.stop()

def heading(kicker, title, description):
    st.markdown(f'<div class="heading"><div class="eyebrow">{kicker}</div><h1>{title}</h1><p>{description}</p></div>', unsafe_allow_html=True)

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
    st.session_state.setdefault(key, value)

with st.sidebar:
    st.markdown('<div class="brand"><span class="brandmark">S</span><div>StayWise<small>HOTEL BOOKING INTELLIGENCE</small></div></div>', unsafe_allow_html=True)
    st.caption('พื้นที่ทำงาน')
    page = st.radio('เมนูหลัก', ['ประเมินการจอง', 'สำรวจข้อมูล', 'ผลทดสอบโมเดล'], label_visibility='collapsed', key='page')
    st.markdown('<div class="side-note"><small>DATA SCIENCE PROJECT</small><p>จากข้อมูล สู่การวางแผน<br>การจองที่เข้าใจได้</p><span>ภูริณัฐ สมศรี</span></div>', unsafe_allow_html=True)

st.markdown(f'<div class="topline">Hotel cancellation <span>/</span> {page}<b>Classification project</b></div>', unsafe_allow_html=True)

if page == 'ประเมินการจอง':
    heading('BOOKING RISK ASSESSMENT', 'เข้าใจความเสี่ยงของทุกการจอง<span>.</span>', 'กรอกข้อมูลการจอง เพื่อประเมินแนวโน้มการยกเลิกก่อนวันเข้าพัก')
    stats([('ข้อมูลหลังลบรายการซ้ำ', '1,050', 'การจอง'), ('อัตรายกเลิกใน Dataset', '23.62%', '248 จาก 1,050 รายการ'), ('โมเดลที่ใช้ประเมิน', 'Decision Tree', '6 Features · ความลึก 3 ระดับ')])
    st.write('')
    left, right = st.columns([1.1, 1], gap='large')
    with left:
        with st.container(border=True):
            st.markdown('<div class="paneltitle"><span>01</span> ข้อมูลการจอง</div>', unsafe_allow_html=True)
            st.button('ใช้ข้อมูลตัวอย่าง', on_click=set_defaults, args=(True,), key='sample')
            with st.form('booking_form'):
                a, b = st.columns(2)
                with a:
                    lead = st.number_input('จองล่วงหน้ากี่วัน', min_value=0.0, max_value=3650.0, step=1.0, key='lead_days', help='จำนวนวันตั้งแต่จองจนถึงวันเข้าพัก')
                    guests = st.number_input('จำนวนผู้เข้าพัก (คน)', min_value=1, max_value=100, step=1, key='guests')
                with b:
                    nights = st.number_input('จำนวนคืนที่เข้าพัก', min_value=1, max_value=365, step=1, key='nights')
                    requests = st.number_input('จำนวนคำขอพิเศษ', min_value=0, max_value=100, step=1, key='special_requests', help='เช่น ขอเตียงเสริม หรือห้องชั้นสูง ถ้าไม่มีให้กรอก 0')
                deposit = st.radio('สถานะการจ่ายมัดจำ', ['จ่ายมัดจำแล้ว', 'ยังไม่จ่ายมัดจำ'], horizontal=True, key='deposit')
                room = st.selectbox('ประเภทห้องพัก', ['Standard — ห้องมาตรฐาน', 'Deluxe — ห้องดีลักซ์', 'Family — ห้องครอบครัว'], key='room')
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
        with st.container(border=True):
            st.markdown('<div class="paneltitle"><span>02</span> ผลการประเมิน</div>', unsafe_allow_html=True)
            result = st.session_state.get('assessment')
            if not result:
                st.markdown('<div class="empty"><div>◈</div><h3>การจองนี้มีความเสี่ยงแค่ไหน?</h3><p>กรอกข้อมูลด้านซ้าย แล้วกดประเมิน<br>เพื่อดูผลจากโมเดล</p><small>Decision Tree · ทดสอบกับข้อมูล 210 รายการ</small></div>', unsafe_allow_html=True)
            else:
                high = bool(result['cancelled'])
                color = '#b56e1b' if high else '#24756b'
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
                    st.dataframe(display, hide_index=True, width='stretch')
                st.caption('หากเปลี่ยนข้อมูล กรุณากดประเมินอีกครั้งเพื่ออัปเดตผล')
            st.markdown('<div class="modelnote"><strong>ใช้เป็นข้อมูลประกอบการวางแผน</strong><p>Recall 62% และ Precision 34.07% สำหรับกลุ่มยกเลิก โมเดลยังมีข้อผิดพลาด ควรยืนยันกับลูกค้าก่อนดำเนินการ</p></div>', unsafe_allow_html=True)
    st.markdown('<div class="insight"><strong>มัดจำสัมพันธ์กับการยกเลิกอย่างชัดเจนใน Dataset นี้</strong><p>กลุ่มไม่จ่ายมัดจำยกเลิก 38.24% เทียบกับ 9.25% ของกลุ่มที่จ่ายแล้ว ความสัมพันธ์นี้ไม่ได้ยืนยันเหตุและผล</p></div>', unsafe_allow_html=True)

elif page == 'สำรวจข้อมูล':
    heading('DATASET EXPLORER', 'รู้จักข้อมูลก่อนทำนาย<span>.</span>', 'หนึ่งแถวแทนการจองโรงแรมหนึ่งรายการ โดย cancelled เป็นตัวแปรเป้าหมาย')
    try:
        raw, data = data_source()
    except (OSError, ValueError) as error:
        st.error('กรุณาอัปโหลด hotel_dataset.xlsx พร้อมโปรเจกต์ และตรวจว่ามีชีต Raw_Data')
        st.stop()
    stats([('ข้อมูลดิบ', f'{len(raw):,}', 'รายการ'), ('แถวซ้ำที่ลบออก', f'{raw.duplicated().sum():,}', 'ซ้ำทั้งแถว'), ('ข้อมูลหลังลบซ้ำ', f'{len(data):,}', '6 Features + Identifier + Target')])
    st.write('')
    chart_style = {'labelColor': '#728198', 'titleColor': '#324763', 'gridColor': '#edf1f7'}
    def chart_theme(chart):
        return chart.configure_view(strokeWidth=0).configure_axis(**chart_style).configure_legend(labelColor='#728198', title=None).configure(background='transparent')
    c1, c2, c3 = st.columns(3, gap='medium')
    with c1, st.container(border=True):
        st.subheader('สัดส่วนผลการจอง')
        counts = pd.DataFrame({'ผลการจอง': ['ไม่ยกเลิก', 'ยกเลิก'], 'จำนวน': [(data.cancelled == 0).sum(), (data.cancelled == 1).sum()]})
        chart = alt.Chart(counts).mark_arc(innerRadius=65).encode(theta='จำนวน:Q', color=alt.Color('ผลการจอง:N', scale=alt.Scale(domain=['ไม่ยกเลิก', 'ยกเลิก'], range=['#256de8', '#f39a43'])), tooltip=['ผลการจอง', 'จำนวน']).properties(height=250)
        st.altair_chart(chart_theme(chart), use_container_width=True)
        st.caption('กลุ่มไม่ยกเลิกมีจำนวนมากกว่า จึงต้องดู Recall และ F1 ร่วมกับ Accuracy')
    with c2, st.container(border=True):
        st.subheader('มัดจำกับอัตรายกเลิก')
        deposits = data.groupby('deposit_paid', as_index=False).cancelled.mean().rename(columns={'cancelled': 'อัตรายกเลิก'})
        deposits['มัดจำ'] = deposits.deposit_paid.map({'yes': 'จ่ายแล้ว', 'no': 'ยังไม่จ่าย'})
        chart = alt.Chart(deposits).mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5).encode(x=alt.X('มัดจำ:N', title=None, axis=alt.Axis(labelAngle=0)), y=alt.Y('อัตรายกเลิก:Q', axis=alt.Axis(format='.0%'), title=None), color=alt.Color('มัดจำ:N', scale=alt.Scale(domain=['จ่ายแล้ว', 'ยังไม่จ่าย'], range=['#256de8', '#f39a43']), legend=None), tooltip=['มัดจำ', alt.Tooltip('อัตรายกเลิก:Q', format='.2%')]).properties(height=250)
        st.altair_chart(chart_theme(chart), use_container_width=True)
        st.caption('ไม่รวมรายการที่สถานะมัดจำว่าง ความสัมพันธ์ไม่ได้ยืนยันเหตุและผล')
    with c3, st.container(border=True):
        st.subheader('วันจองล่วงหน้าเฉลี่ย')
        leads = data.groupby('cancelled', as_index=False).lead_days.mean()
        leads['ผลการจอง'] = leads.cancelled.map({0: 'ไม่ยกเลิก', 1: 'ยกเลิก'})
        chart = alt.Chart(leads).mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5).encode(x=alt.X('ผลการจอง:N', title=None, axis=alt.Axis(labelAngle=0)), y=alt.Y('lead_days:Q', title='วัน'), color=alt.Color('ผลการจอง:N', scale=alt.Scale(domain=['ไม่ยกเลิก', 'ยกเลิก'], range=['#256de8', '#f39a43']), legend=None), tooltip=['ผลการจอง', alt.Tooltip('lead_days:Q', format='.2f')]).properties(height=250)
        st.altair_chart(chart_theme(chart), use_container_width=True)
        st.caption('กลุ่มยกเลิกจองล่วงหน้าเฉลี่ยนานกว่า คำนวณจากข้อมูลที่ไม่ว่างก่อนเติมค่า')
    with st.container(border=True):
        st.subheader('ความหมายของตัวแปร')
        dictionary = pd.DataFrame([('booking_id', 'รหัสการจอง', 'Identifier — ตัดออกจากโมเดล'), ('lead_days', 'วันจองล่วงหน้า', 'Feature ตัวเลข'), ('nights', 'จำนวนคืน', 'Feature ตัวเลขจำนวนเต็ม'), ('guests', 'จำนวนผู้เข้าพัก', 'Feature ตัวเลขจำนวนเต็ม'), ('special_requests', 'จำนวนคำขอพิเศษ', 'Feature ตัวเลขจำนวนเต็ม'), ('deposit_paid', 'สถานะมัดจำ', 'Feature หมวดหมู่ Yes/No'), ('room_type', 'ประเภทห้อง', 'Feature หมวดหมู่ไม่มีลำดับ'), ('cancelled', '0 = ไม่ยกเลิก / 1 = ยกเลิก', 'Target')], columns=['คอลัมน์', 'ความหมาย', 'บทบาท'])
        st.dataframe(dictionary, hide_index=True, width='stretch')
    with st.expander('การตรวจคุณภาพและเตรียมข้อมูล'):
        quality = pd.DataFrame({'คอลัมน์': raw.columns, 'ค่าว่างในข้อมูลดิบ': raw.isna().sum().values, 'ชนิดข้อมูล': raw.dtypes.astype(str).values})
        st.dataframe(quality, hide_index=True, width='stretch')
        st.markdown('''1. ลบแถวซ้ำ 12 แถวก่อนแบ่ง Train/Test
2. ตัดช่องว่างและปรับตัวพิมพ์ในสถานะมัดจำและประเภทห้อง
3. เปลี่ยนค่าทศนิยมในจำนวนคืน 2 ค่า ผู้เข้าพัก 1 ค่า และคำขอพิเศษ 1 ค่า เป็นค่าว่าง
4. แบ่งข้อมูลแบบ Stratified 80/20 จากนั้นเติม Median/Mode โดยเรียนรู้จาก Train เท่านั้น
5. ทำ One-Hot Encoding สำหรับหมวดหมู่ ใช้ StandardScaler สำหรับ KNN
6. ใช้ Features ทั้ง 6 ตัวหลังตัด booking_id ไม่ใช้ cancelled เป็นข้อมูลนำเข้า

lead_days สูงสุด 182.4 วันยังเก็บไว้ เพราะอาจเกิดขึ้นจริง ควรตรวจต้นทางก่อนลบหรือแก้ไข''')

else:
    heading('MODEL EVALUATION', 'ทำนายได้ดีแค่ไหน<span>?</span>', 'ผลทดลองใหม่จากไฟล์แนบ แยก Test ออกจากการฝึกและเลือกพารามิเตอร์')
    stats([('Train', '840', '80% ของข้อมูล'), ('Test', '210', '20% · ยกเลิกจริง 50 รายการ'), ('Validation', '5-Fold', 'Stratified · เลือกตาม F1')])
    st.write('')
    with st.container(border=True):
        st.subheader('เปรียบเทียบผลบนชุด Test')
        scores = pd.DataFrame([['Decision Tree — ใช้ในแอป', '62.38%', '34.07%', '62.00%', '43.97%'], ['KNN', '73.81%', '40.74%', '22.00%', '28.57%'], ['ทายว่าไม่ยกเลิกทุกคน', '76.19%', '—', '0.00%', '0.00%']], columns=['โมเดล', 'Accuracy', 'Precision', 'Recall', 'F1'])
        st.dataframe(scores, hide_index=True, width='stretch')
        st.caption('Precision, Recall และ F1 เป็นค่าของกลุ่ม cancelled = 1')
    a, b = st.columns(2, gap='large')
    with a, st.container(border=True):
        st.subheader('Confusion Matrix: Decision Tree')
        cm = pd.DataFrame(model['metrics']['confusion'], index=['ไม่ยกเลิกจริง', 'ยกเลิกจริง'], columns=['ทายว่าไม่ยกเลิก', 'ทายว่ายกเลิก'])
        st.dataframe(cm, width='stretch')
        st.info('ตรวจพบผู้ยกเลิกจริง 31 จาก 50 รายการ พลาด 19 รายการ และแจ้งเตือนผิด 60 รายการ')
    with b, st.container(border=True):
        st.subheader('Accuracy สูง ยังจับการยกเลิกได้น้อย')
        st.write('ทายว่าไม่ยกเลิกทุกคนก็ได้ Accuracy 76.19% แต่ตรวจพบผู้ยกเลิกไม่ได้เลย Decision Tree จับผู้ยกเลิกได้มากกว่า KNN ในการทดลองนี้ แต่ยังมีการแจ้งเตือนผิดจำนวนมาก')
        st.markdown('**Recall:** จับผู้ยกเลิกจริงได้กี่เปอร์เซ็นต์\n\n**Precision:** คนที่ทายว่าจะยกเลิก ยกเลิกจริงกี่เปอร์เซ็นต์\n\n**F1:** ประเมิน Precision และ Recall ร่วมกัน')
    with st.expander('วิธีทดลองและข้อจำกัด'):
        st.write('Train/Test แบบ stratify=y, random_state=42 ปรับพารามิเตอร์ด้วย GridSearchCV แบบ Stratified 5-Fold บน Train โดยเลือก F1 ของกลุ่มยกเลิก ทำการเติมค่า Encoding และ Scaling ภายใน Pipeline เพื่อป้องกัน Data Leakage')
        st.code('Decision Tree: max_depth=3, min_samples_leaf=1, class_weight="balanced"\nKNN: n_neighbors=5, weights="uniform", metric="manhattan"', language='text')
        st.write('โมเดลยังไม่แม่นยำเพียงพอสำหรับตัดสินใจแทนโรงแรม ข้อมูลสองกลุ่มไม่สมดุล Features ยังแยกสองกลุ่มไม่ชัด และผลทดสอบครั้งเดียวไม่รับประกันผลกับข้อมูลอนาคต คะแนนยังไม่ผ่านการปรับเทียบความน่าจะเป็น')

st.markdown('<div class="footer">StayWise / Hotel Cancellation Classification <span>จัดทำโดย ภูริณัฐ สมศรี</span></div>', unsafe_allow_html=True)
