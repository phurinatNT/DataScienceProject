# Hotel Cancellation Classification

## Files
- `hotel_cancellation_project.ipynb` — Cleaning, EDA, preprocessing, 3 models, evaluation, model selection
- `hotel_model.pkl` — final Random Forest pipeline
- `app.py` — Streamlit deployment
- `hotel_cancellation_cleaned.xlsx` — cleaned dataset
- `requirements.txt` — required packages

## Run
1. Put the original `C09_hotel_cancellation_classification.xlsx` in the same folder as the notebook.
2. Install packages: `pip install -r requirements.txt`
3. Run notebook from top to bottom.
4. Run deployment: `streamlit run app.py`

## Project target
Predict `cancelled`:
- 0 = not cancelled
- 1 = cancelled

Important: the classes are imbalanced, so Accuracy alone is not enough. The project also evaluates Precision, Recall, F1-score, ROC-AUC and Confusion Matrix.
