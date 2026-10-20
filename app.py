from pathlib import Path

import joblib
from flask import Flask, request, jsonify, render_template

from preprocess import clean_model2

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent

model_a = joblib.load(BASE_DIR / "models" / "email_classifier.joblib")
model_b = joblib.load(BASE_DIR / "models" / "maejor" / "maejor_tfidf_logreg.joblib")

SAFE_MAX = 0.30      # starting guess, not a tuned value
PHISH_MIN = 0.70
MAX_SUBJECT = 300
MAX_BODY = 20000

LABELS = {
    "safe": "Likely safe",
    "uncertain": "Uncertain",
    "phishing": "Likely phishing",
}


def get_band(p):
    if p <= SAFE_MAX:
        return "safe"
    if p >= PHISH_MIN:
        return "phishing"
    return "uncertain"


def predict_email(model, text):
    probabilities = model.predict_proba([text])[0]
    phishing_index = list(model.classes_).index(1)
    p = float(probabilities[phishing_index])
    band = get_band(p)
    return {
        "band": band,
        "label": LABELS[band],
        "phishing_score": round(p * 100, 1),
    }


@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json(silent=True) or {}

    subject = str(data.get("subject", "")).strip()[:MAX_SUBJECT]
    body = str(data.get("body", "")).strip()[:MAX_BODY]

    if not subject and not body:
        return jsonify({"error": "Please enter an email subject or body."}), 400

    text = clean_model2(subject, body)
    if len(text) < 20:
        return jsonify({
            "error": "The text is too short to judge reliably. Please add more."
        }), 400

    result_a = predict_email(model_a, text)
    result_b = predict_email(model_b, text)

    return jsonify({
        "model_a": result_a,
        "model_b": result_b,
        "agree": result_a["band"] == result_b["band"],
    })


@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)