import json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, confusion_matrix
)

# กำหนดไฟล์ข้อมูลและโฟลเดอร์บันทึกโมเดล
SOURCE = Path(__file__).resolve().parent / 'hotel_dataset.xlsx'
OUT = Path(__file__).resolve().parent

# อ่านข้อมูลจาก Excel และลบแถวที่ซ้ำกันทุกคอลัมน์
d = pd.read_excel(SOURCE, sheet_name='Raw_Data').drop_duplicates()

# แบ่ง Features เป็นตัวเลขและหมวดหมู่ ไม่ใช้ booking_id
num = ['lead_days', 'nights', 'guests', 'special_requests']
cat = ['deposit_paid', 'room_type']

# ตัดช่องว่างและปรับตัวพิมพ์ เช่น "YES" กับ "yes" ให้เหมือนกัน
d[cat] = d[cat].apply(lambda s: s.str.strip().str.lower())

# จำนวนคืน คน และคำขอควรเป็นจำนวนเต็ม หากมีทศนิยมให้เป็นค่าว่าง
for c in num[1:]:
    d.loc[d[c].notna() & (d[c] % 1 != 0), c] = np.nan

# แบ่ง Train 80% / Test 20% โดยรักษาสัดส่วนกลุ่มยกเลิก
# xt/yt = ข้อมูลฝึก, xv/yv = ข้อมูลทดสอบ
xt, xv, yt, yv = train_test_split(
    d[num + cat],
    d.cancelled,
    test_size=.2,
    stratify=d.cancelled,
    random_state=42
)

# เตรียมข้อมูล: ตัวเลขเติม Median / หมวดหมู่เติม Mode แล้วทำ One-Hot
prep = ColumnTransformer([
    ('num', SimpleImputer(strategy='median'), num),
    ('cat', Pipeline([
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('ohe', OneHotEncoder(
            handle_unknown='ignore',
            sparse_output=False
        ))
    ]), cat)
])

# รวมการเตรียมข้อมูลกับโมเดล และเรียนรู้จาก Train เท่านั้น
# จำกัดความลึก 3 ระดับ และเพิ่มน้ำหนักให้คลาสที่มีข้อมูลน้อย
model = Pipeline([
    ('prep', prep),
    ('model', DecisionTreeClassifier(
        max_depth=3,
        min_samples_leaf=1,
        class_weight='balanced',
        random_state=42
    ))
]).fit(xt, yt)

# ดึงโครงสร้างต้นไม้ และทำนายข้อมูล Test
t = model['model'].tree_
pred = model.predict(xv)

# เตรียมโครงสร้างโมเดลและคะแนนประเมินสำหรับบันทึกเป็น JSON
payload = {
    'features': list(prep.get_feature_names_out()),  # Features หลัง Encoding
    'left': t.children_left.tolist(),              # โหนดลูกด้านซ้าย
    'right': t.children_right.tolist(),            # โหนดลูกด้านขวา
    'feature': t.feature.tolist(),                 # Feature ที่ใช้แบ่งแต่ละโหนด
    'threshold': t.threshold.tolist(),             # ค่าเกณฑ์แบ่ง
    'value': t.value[:, 0, :].tolist(),             # ค่าคลาสในแต่ละโหนด
    'medians': xt[num].median().to_dict(),          # Median จาก Train

    # เปรียบเทียบผลทำนายกับคำตอบจริงของ Test
    'metrics': {
        'accuracy': accuracy_score(yv, pred),
        'precision': precision_score(yv, pred),
        'recall': recall_score(yv, pred),
        'f1': f1_score(yv, pred),
        'confusion': confusion_matrix(yv, pred).tolist()
    },
    'method': (
        'DecisionTreeClassifier; class_weight=balanced; '
        'max_depth=3; random_state=42; 80/20 stratified split'
    )
}

# บันทึกโครงสร้างโมเดลและผลประเมินไว้ใช้ในเว็บ
(OUT / 'model.json').write_text(
    json.dumps(payload),
    encoding='utf-8'
)

# เก็บข้อมูลและผลทำนาย Test ในหน่วยความจำสำหรับตรวจสอบ
# scores เป็นคะแนนโมเดล ยังไม่ใช่โอกาสจริงที่ผ่านการปรับเทียบ
fixtures = {
    'rows': prep.transform(xv).tolist(),
    'scores': model.predict_proba(xv)[:, 1].tolist(),
    'classes': pred.tolist()
}

# แสดงผลประเมินใน Terminal
print(json.dumps(payload['metrics']))
