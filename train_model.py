"""Reproduce the evaluated Decision Tree from the supplied workbook."""
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
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

SOURCE = Path(__file__).resolve().parent / 'hotel_dataset.xlsx'
OUT = Path(__file__).resolve().parent
d = pd.read_excel(SOURCE, sheet_name='Raw_Data').drop_duplicates()
num = ['lead_days', 'nights', 'guests', 'special_requests']
cat = ['deposit_paid', 'room_type']
d[cat] = d[cat].apply(lambda s: s.str.strip().str.lower())
for c in num[1:]:
    d.loc[d[c].notna() & (d[c] % 1 != 0), c] = np.nan
xt, xv, yt, yv = train_test_split(d[num + cat], d.cancelled, test_size=.2, stratify=d.cancelled, random_state=42)
prep = ColumnTransformer([
    ('num', SimpleImputer(strategy='median'), num),
    ('cat', Pipeline([('imputer', SimpleImputer(strategy='most_frequent')), ('ohe', OneHotEncoder(handle_unknown='ignore', sparse_output=False))]), cat)
])
model = Pipeline([('prep', prep), ('model', DecisionTreeClassifier(max_depth=3, min_samples_leaf=1, class_weight='balanced', random_state=42))]).fit(xt, yt)
t = model['model'].tree_
pred = model.predict(xv)
payload = {'features': list(prep.get_feature_names_out()), 'left': t.children_left.tolist(), 'right': t.children_right.tolist(), 'feature': t.feature.tolist(), 'threshold': t.threshold.tolist(), 'value': t.value[:, 0, :].tolist(), 'medians': xt[num].median().to_dict(), 'metrics': {'accuracy': accuracy_score(yv, pred), 'precision': precision_score(yv, pred), 'recall': recall_score(yv, pred), 'f1': f1_score(yv, pred), 'confusion': confusion_matrix(yv, pred).tolist()}, 'method': 'DecisionTreeClassifier; class_weight=balanced; max_depth=3; random_state=42; 80/20 stratified split'}
(OUT / 'model.json').write_text(json.dumps(payload), encoding='utf-8')
fixtures = {'rows': prep.transform(xv).tolist(), 'scores': model.predict_proba(xv)[:, 1].tolist(), 'classes': pred.tolist()}
# Test predictions remain in memory; they are not needed for deployment.
print(json.dumps(payload['metrics']))
