import json
from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.model_selection import (
    train_test_split,
    StratifiedKFold,
    GridSearchCV
)
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)


# ==================================================
# 1. อ่านและทำความสะอาดข้อมูล
# ==================================================

def load_data(source):
    # อ่าน Excel และลบแถวซ้ำ
    d = pd.read_excel(
        source,
        sheet_name='Raw_Data'
    ).drop_duplicates().copy()

    num = ['lead_days', 'nights', 'guests', 'special_requests']
    cat = ['deposit_paid', 'room_type']

    # ปรับตัวพิมพ์และช่องว่างของหมวดหมู่
    d[cat] = d[cat].apply(
        lambda s: s.str.strip().str.lower()
    )

    # จำนวนคืน คน และคำขอต้องเป็นจำนวนเต็ม
    for column in num[1:]:
        d.loc[
            d[column].notna() & (d[column] % 1 != 0),
            column
        ] = np.nan

    # ใช้ Features 6 ตัว ไม่ใช้ booking_id
    X = d[num + cat]
    y = d['cancelled']

    return X, y, num, cat


# ==================================================
# 2. สร้างขั้นตอนเตรียมข้อมูล
# ==================================================

def make_preprocessor(num, cat, scaling=False):
    # ตัวเลขเติมค่าว่างด้วย Median
    numeric_steps = [
        ('imputer', SimpleImputer(strategy='median'))
    ]

    # เพิ่ม Scaling เฉพาะ KNN
    if scaling:
        numeric_steps.append(
            ('scaler', StandardScaler())
        )

    return ColumnTransformer([
        ('num', Pipeline(numeric_steps), num),

        # หมวดหมู่เติม Mode แล้วทำ One-Hot Encoding
        ('cat', Pipeline([
            ('imputer', SimpleImputer(
                strategy='most_frequent'
            )),
            ('ohe', OneHotEncoder(
                handle_unknown='ignore',
                sparse_output=False
            ))
        ]), cat)
    ])


# ==================================================
# 3. ฟังก์ชันประเมินผล
# ==================================================

def evaluate(actual, predicted):
    # Precision, Recall และ F1 วัดกลุ่มยกเลิก (คลาส 1)
    return {
        'accuracy': float(
            accuracy_score(actual, predicted)
        ),
        'precision': float(
            precision_score(
                actual, predicted, zero_division=0
            )
        ),
        'recall': float(
            recall_score(
                actual, predicted, zero_division=0
            )
        ),
        'f1': float(
            f1_score(
                actual, predicted, zero_division=0
            )
        ),

        # แถว = จริง / คอลัมน์ = ทำนาย
        # เรียงเป็น [[TN, FP], [FN, TP]]
        'confusion': confusion_matrix(
            actual, predicted, labels=[0, 1]
        ).tolist()
    }


# ==================================================
# 4. ขั้นตอนหลัก
# ==================================================

def main():
    root = Path(__file__).resolve().parent
    source = root / 'hotel_dataset.xlsx'

    X, y, num, cat = load_data(source)

    # แบ่ง Train 80% / Test 20% โดยรักษาสัดส่วนคลาส
    xt, xv, yt, yv = train_test_split(
        X,
        y,
        test_size=0.2,
        stratify=y,
        random_state=42
    )

    print(f'Train: {len(xt)} รายการ')
    print(f'Test : {len(xv)} รายการ')

    # แบ่ง Train เป็น 5 ส่วน สลับส่วนตรวจสอบ
    cv = StratifiedKFold(
        n_splits=5,
        shuffle=True,
        random_state=42
    )

    # ==============================================
    # 5. Pipeline และ Grid ของ Decision Tree
    # ==============================================

    tree_pipeline = Pipeline([
        ('prep', make_preprocessor(num, cat)),
        ('model', DecisionTreeClassifier(
            random_state=42
        ))
    ])

    # ทดลองทุกชุดค่าที่เกิดจากการจับคู่พารามิเตอร์
    tree_grid = {
        'model__max_depth': [2, 3, 4, 5, None],
        'model__min_samples_leaf': [1, 5, 10],
        'model__class_weight': [None, 'balanced']
    }

    # ==============================================
    # 6. Pipeline และ Grid ของ KNN
    # ==============================================

    knn_pipeline = Pipeline([
        ('prep', make_preprocessor(
            num, cat, scaling=True
        )),
        ('model', KNeighborsClassifier())
    ])

    knn_grid = {
        'model__n_neighbors': [3, 5, 7, 9, 11],
        'model__weights': ['uniform', 'distance'],

        # p=1 คือ Manhattan / p=2 คือ Euclidean
        'model__p': [1, 2]
    }

    # ==============================================
    # 7. Grid Search เฉพาะข้อมูล Train
    # ==============================================

    searches = {}

    for name, pipeline, grid in [
        ('Decision Tree', tree_pipeline, tree_grid),
        ('KNN', knn_pipeline, knn_grid)
    ]:
        search = GridSearchCV(
            estimator=pipeline,
            param_grid=grid,
            scoring='f1',       # เลือกตาม F1 ของกลุ่มยกเลิก
            cv=cv,
            refit=True,         # ฝึกค่าที่ดีที่สุดด้วย Train ทั้งหมด
            n_jobs=1,
            error_score='raise'
        )

        # Pipeline ถูก fit ใหม่ภายในแต่ละ Training Fold
        # จึงไม่ใช้ Validation/Test เรียนรู้ค่าเติมหรือ Scaling
        search.fit(xt, yt)
        searches[name] = search

        print(f'\n{name}')
        print('พารามิเตอร์ที่ดีที่สุด:', search.best_params_)
        print(
            f'CV F1 เฉลี่ย: {search.best_score_ * 100:.2f}%'
        )

    # เลือกโมเดลจาก CV ก่อนดูผล Test
    selected_name = max(
        searches,
        key=lambda name: searches[name].best_score_
    )

    print(f'\nโมเดลที่เลือกจาก CV: {selected_name}')

    # ==============================================
    # 8. ประเมินโมเดลที่ปรับแล้วบน Test
    # ==============================================

    results = {}

    for name, search in searches.items():
        predicted = search.predict(xv)
        metrics = evaluate(yv, predicted)

        results[name] = {
            'best_params': search.best_params_,
            'cv_mean_f1': float(search.best_score_),
            'test': metrics
        }

        print(f'\nผล Test ของ {name}')
        print(f"Accuracy : {metrics['accuracy'] * 100:.2f}%")
        print(f"Precision: {metrics['precision'] * 100:.2f}%")
        print(f"Recall   : {metrics['recall'] * 100:.2f}%")
        print(f"F1       : {metrics['f1'] * 100:.2f}%")
        print('Confusion Matrix:', metrics['confusion'])

    # ==============================================
    # 9. บันทึกผลแยกจากโมเดลที่เว็บใช้
    # ==============================================

    report = {
        'train_rows': len(xt),
        'test_rows': len(xv),
        'selection_metric': 'Mean CV F1 for cancelled=1',
        'selected_by_cv': selected_name,
        'models': results
    }

    output = root / 'gridsearch_results.json'
    output.write_text(
        json.dumps(
            report,
            ensure_ascii=False,
            indent=2
        ),
        encoding='utf-8'
    )

    print(f'\nบันทึกผลที่ {output.name}')
    print('model.json ของเว็บไม่ได้ถูกเขียนทับ')


# ฝึกเมื่อรันไฟล์นี้โดยตรงเท่านั้น
if __name__ == '__main__':
    main()
