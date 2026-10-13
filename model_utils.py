"""Portable inference for the exported, evaluated scikit-learn tree."""
import json
import math
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def load_model():
    return json.loads((ROOT / 'model.json').read_text(encoding='utf-8'))

def traverse(model, vector):
    node, path = 0, []
    while model['left'][node] != -1:
        f, threshold = model['feature'][node], model['threshold'][node]
        value = struct.unpack('f', struct.pack('f', float(vector[f])))[0]
        left = value <= threshold
        path.append({'feature': model['features'][f], 'threshold': threshold, 'value': vector[f], 'left': left})
        node = model['left'][node] if left else model['right'][node]
    no, yes = model['value'][node]
    return {'score': yes / (yes + no), 'cancelled': int(yes > no), 'path': path}

def predict(model, data):
    limits = {'lead_days': (0, 3650), 'nights': (1, 365), 'guests': (1, 100), 'special_requests': (0, 100)}
    for key, (minimum, maximum) in limits.items():
        value = data.get(key)
        if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value) or not minimum <= value <= maximum:
            raise ValueError(f'ค่า {key} อยู่นอกช่วงที่รองรับ')
        if key != 'lead_days' and value != int(value):
            raise ValueError('จำนวนคืน ผู้เข้าพัก และคำขอพิเศษต้องเป็นจำนวนเต็ม')
    if data.get('deposit_paid') not in ('yes', 'no') or data.get('room_type') not in ('standard', 'deluxe', 'family'):
        raise ValueError('สถานะมัดจำหรือประเภทห้องไม่ถูกต้อง')
    vector = [data['lead_days'], data['nights'], data['guests'], data['special_requests'], int(data['deposit_paid'] == 'no'), int(data['deposit_paid'] == 'yes'), int(data['room_type'] == 'deluxe'), int(data['room_type'] == 'family'), int(data['room_type'] == 'standard')]
    result = traverse(model, vector)
    result['outside_training_range'] = data['lead_days'] < 1 or data['lead_days'] > 182.4 or data['nights'] > 7 or data['guests'] > 5 or data['special_requests'] > 5
    return result
