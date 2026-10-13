# StayWise — Streamlit

## อัปเดต UI 3.0

ลำดับช่องกรอก 1–6 พร้อมตัวอย่าง สีตัวอักษรอ่านชัดขึ้น การ์ดฟอร์มและผลลัพธ์แยกชัดเจน เก็บค่าฟอร์มเมื่อสลับหน้า แสดงข้อมูลที่ใช้ประเมินครั้งล่าสุดเป็นภาษาไทย และมี SLIDES_PROMPT_TH.txt สำหรับสั่งทำสไลด์ 14 หน้า พร้อม Speaker notes และคำถามเตรียมตอบอาจารย์

อัปเดตไฟล์ทั้งหมดจากชุดนี้แทนชุดเดิม แล้ว Commit และ Reboot app ถ้าใช้ Python 3.12 อยู่แล้วไม่ต้องลบแอป ตรวจว่าใต้หน้าเว็บขึ้น UI 3.0 เพื่อยืนยันว่าได้เปิดฉบับล่าสุด

ต้องมี .streamlit/config.toml ที่ root ของ GitHub repository (อยู่ระดับเดียวกับ app.py) เพื่อให้ Theme ทำงาน ไม่วาง config.toml เปล่า ๆ โดยไม่มีโฟลเดอร์ .streamlit

เว็บประเมินการยกเลิกการจองโรงแรม UI ภาษาไทย โทนน้ำเงิน รองรับจอคอมและมือถือ มีหน้าประเมิน หน้าสำรวจข้อมูลพร้อมกราฟ 3 ชุด และหน้าผลทดสอบโมเดล

## Deploy บน Streamlit Community Cloud

1. แตกไฟล์ ZIP
2. สร้าง GitHub repository ใหม่ แล้วอัปโหลด **ไฟล์ภายในโฟลเดอร์** staywise_streamlit ให้อยู่ที่ root ของ repository รวมโฟลเดอร์ `.streamlit` ด้วย ไม่อัปโหลด ZIP ทั้งก้อนหรือโฟลเดอร์ `.venv`
3. ตรวจว่ามี `app.py`, `model_utils.py`, `model.json`, `hotel_dataset.xlsx`, `style.css` และ `requirements.txt` อยู่ด้วยกัน
4. ไปที่ https://share.streamlit.io/ และเชื่อม GitHub
5. เลือก Create app แล้วเลือก repository และ branch ที่อัปโหลด
6. กำหนด Main file path เป็น `app.py` ถ้าอัปโหลดทั้งโฟลเดอร์แทน ให้ใช้ `staywise_streamlit/app.py`
7. ใน Advanced settings เลือก Python **3.12** แล้วกด Deploy อย่าปล่อยเป็น Python 3.14 สำหรับแพ็กเกจชุดนี้

ไม่ต้องใส่ Secrets หรือ API key แอปใช้โมเดลที่แนบมา ไม่ต้องมีเซิร์ฟเวอร์ Python แยก

เอกสารทางการ: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy

## เปิดบนเครื่องตัวเอง (Windows)

เปิด Terminal ในโฟลเดอร์โปรเจกต์ แล้วรัน:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m streamlit run app.py
```

ถ้าติดตั้ง Python 3.12 เวอร์ชันเดียว สามารถใช้ `python` แทน `py -3.12`

## แก้ TypeError ตอน import Altair บน Python 3.14

หาก traceback มี `python3.14`, `StepKwds(TypedDict, closed=True)` และเกิด TypeError ตอน import Altair ให้ทำดังนี้:

1. อัปโหลด requirements.txt จากชุดนี้แทนไฟล์เดิมบน GitHub และ Commit
2. จด repository, branch, Main file path และ subdomain ของแอปเดิม
3. ใน Streamlit Cloud เลือก Delete app **ลบเฉพาะแอปที่ Deploy ไม่ลบ GitHub repository**
4. Create app ใหม่จาก repository เดิม ตั้ง Main file path เป็น app.py
5. เปิด Advanced settings และเลือก Python **3.12** ก่อนกด Deploy

การแก้ requirements.txt หรือ Reboot เพียงอย่างเดียวไม่เปลี่ยน Python ที่แอปใช้ ส่วน runtime.txt ไม่ใช่ตัวกำหนดเวอร์ชัน Python สำหรับ Community Cloud ให้เลือกใน Advanced settings

เวอร์ชันที่ทดสอบ: Python 3.12.14, Streamlit 1.50.0, Altair 5.5.0, pandas 2.2.3, openpyxl 3.1.5 และ typing_extensions 4.16.0 ทดสอบหน้าประเมิน ตัวอย่าง รีเซ็ต หน้ากราฟ 3 ชุด และหน้าผลโมเดลผ่าน ไม่ได้ทดสอบชุดนี้บน Python 3.14

เอกสารเปลี่ยน Python: https://docs.streamlit.io/deploy/streamlit-community-cloud/manage-your-app/upgrade-python

## รายการไฟล์

| ไฟล์ | หน้าที่ |
| --- | --- |
| app.py | หน้าใช้งาน Streamlit |
| style.css | สี ฟอนต์ และการจัดหน้า |
| model_utils.py | ตรวจข้อมูลและคำนวณผลจากต้นไม้จริง |
| model.json | Decision Tree ที่ฝึกและทดสอบไว้ |
| hotel_dataset.xlsx | Dataset ต้นฉบับ สำหรับหน้าสำรวจข้อมูล |
| train_model.py | ทำซ้ำการฝึกโมเดลนี้ |
| requirements.txt | Dependencies สำหรับ Deploy |
| requirements-training.txt | Dependencies เพิ่มเติมสำหรับฝึกใหม่ |
| .streamlit/config.toml | Theme ของแอป |

## โมเดลและการเตรียมข้อมูล

ชุดนี้ใช้โมเดลจากการทดลองล่าสุดในบทสนทนา ไม่ใช่ `hotel_model.pkl` ของโปรเจกต์เดิม ไม่ต้องนำ pickle เดิมมาใส่ทับ

ข้อมูลดิบ 1,062 แถว ลบแถวซ้ำทั้งแถว 12 แถว เหลือ 1,050 แถว ตัด booking_id ออกจาก Features ปรับหมวดหมู่ด้วย strip/lower เปลี่ยนค่าทศนิยมใน nights, guests และ special_requests เป็นค่าว่าง แล้วแบ่ง Train/Test แบบ Stratified 80/20, random_state=42 เติม Median และ Mode จาก Train เท่านั้น แล้ว One-Hot Encoding

Features: lead_days, nights, guests, special_requests, deposit_paid, room_type

Target: cancelled, 0 = ไม่ยกเลิก, 1 = ยกเลิก

Decision Tree: max_depth=3, min_samples_leaf=1, class_weight=balanced, random_state=42

พารามิเตอร์นี้ถูกเลือกจากการทดลอง GridSearchCV แบบ Stratified 5-Fold บน Train โดยใช้ F1 ของกลุ่มยกเลิก ในการวิเคราะห์ก่อนสร้างเว็บไซต์ สคริปต์ train_model.py ทำซ้ำการฝึกพารามิเตอร์ที่เลือกแล้ว ไม่ได้รัน GridSearch ซ้ำ

Test 210 รายการ: Accuracy 62.38%, Precision 34.07%, Recall 62.00%, F1 43.97%; Confusion Matrix [[100,60],[19,31]]

คะแนนความเสี่ยงเป็นคะแนนจากใบของต้นไม้ที่ถ่วงน้ำหนักคลาส ยังไม่ใช่ความน่าจะเป็นที่ผ่านการปรับเทียบ ไม่ควรตีความว่า 82 คะแนนเท่ากับโอกาสยกเลิก 82% ใช้เป็นข้อมูลประกอบการยืนยันการจองเท่านั้น

ไม่ต้องติดตั้ง scikit-learn เพื่อเปิดเว็บ เพราะส่งออกต้นไม้เป็น JSON และใช้ model_utils.py คำนวณแบบเดียวกัน จึงหลีกเลี่ยงปัญหา pickle ต่างเวอร์ชัน โดยตรวจความตรงกันกับผล scikit-learn ครบ 210 รายการทดสอบแล้ว

## ฝึกใหม่ (ทางเลือก)

```powershell
.venv\Scripts\python.exe -m pip install -r requirements-training.txt
.venv\Scripts\python.exe train_model.py
```

อย่าเปลี่ยน Dataset หรือโมเดลโดยไม่อัปเดตสรุปจำนวนข้อมูลและผลการทดลองในหน้าแอป เพราะสรุปบางส่วนแสดงผลจากการทดลองชุดนี้

## แนวทางแก้ปัญหา

- ฉบับแก้ UI: ปรับสีชื่อช่องและปุ่มให้อ่านง่าย เปลี่ยนสถานะมัดจำเป็น dropdown พร้อมคำอธิบาย และแก้ข้อความหน้าผลที่ถูกบีบเป็นวงกลม
- เมื่อต้องการอัปเดตจากฉบับก่อน ให้นำ app.py, style.css และ .streamlit/config.toml ไปแทนบน GitHub แล้ว Commit โดย config.toml ต้องอยู่ในโฟลเดอร์ .streamlit ที่ root ของ repository
- หากยังเห็นหน้าตาเดิม ให้ Reboot app แล้วรีเฟรชเบราว์เซอร์ด้วย Ctrl+F5 การแก้ UI นี้ไม่ต้องลบแอปหรือเปลี่ยน Python อีก ถ้าใช้ Python 3.12 อยู่แล้ว

- `ModuleNotFoundError`: ตรวจว่า requirements.txt อยู่ใน repository และใช้ environment เดียวกับ Streamlit
- โมเดลไม่พร้อม: ตรวจว่ามี model.json และ model_utils.py อยู่ข้าง app.py
- เปิดหน้าข้อมูลไม่ได้: ตรวจว่า hotel_dataset.xlsx มีชีต Raw_Data
- ถ้าใช้ repository เดิม: แทน app.py และ requirements.txt แล้วเพิ่มไฟล์ประกอบทั้งหมดจากชุดนี้
- ไม่ควรอัปโหลด `.venv` ขึ้น GitHub


## UI 4.0 — ปรับการอ่านและระยะหน้าเว็บ
- เว้นพื้นที่ใต้แถบเครื่องมือทั้งหน้าจอใหญ่และมือถือ
- กำหนดสีกราฟเองและปิดการทับสีจากธีม Streamlit
- ตารางตัวอักษรเข้มบนพื้นสว่าง พร้อมเลื่อนแนวนอนบนจอเล็ก
- ปรับสีช่องกรอก ปุ่ม คำอธิบาย และหัวข้อให้ชัดเจน
- อัปเดต app.py, style.css และ .streamlit/config.toml แล้ว Reboot app; ตรวจท้ายหน้าให้ขึ้น UI 4.0


## UI 5.0 — หน้าภาพรวมใหม่
- หัวข้อใหม่: ภาพรวมการจองโรงแรม พร้อมแถบหัวข้อสีน้ำเงินเข้ม
- ไม่ยกเลิก 76.38% สีเขียว / ยกเลิก 23.62% สีแดง พร้อมจำนวนจริง
- อัตรายกเลิกตามมัดจำใช้สีแดงทั้งสองกลุ่ม เพราะวัดสิ่งเดียวกัน
- วันจองล่วงหน้าเฉลี่ยแสดงหน่วยวัน แยกจากเปอร์เซ็นต์อย่างชัดเจน
- รวม CSS ใน app.py แล้ว จึงไม่ต้องรอ style.css เพื่อเห็นดีไซน์ใหม่
- แตก ZIP แล้วนำไฟล์ภายใน staywise_streamlit ไปแทนไฟล์ในโฟลเดอร์เดียวกับ app.py ที่ Streamlit ใช้จริง อย่าอัปโหลด ZIP โดยไม่แตกไฟล์
- ตรวจหัวหน้าว่าเป็นแถบสีน้ำเงินเข้มและป้าย StayWise · V5 / ท้ายหน้า UI 5.0 หากไม่พบ แสดงว่าหน้าเว็บยังไม่ได้รัน app.py รุ่นนี้
- ชุดนี้ยังมี Prompt ทำสไลด์และข้อมูลเดิม ผลโมเดลไม่เปลี่ยน
