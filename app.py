from flask import Flask, jsonify, render_template, request

import db
import stats_analysis as sa
from recommender import rank_crops
from soil_report import read_soil_report

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024


@app.errorhandler(413)
def file_too_large(_):
    return jsonify({"error": "File is too large (max 5 MB)."}), 413


def stats_dataframe():
    return sa.build_dataframe(db.fetch_all_crops())


def run_stats(func, *args):
    try:
        return jsonify(func(stats_dataframe(), *args))
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/stats")
def stats_page():
    return render_template("stats.html")


@app.route("/api/options")
def options():
    crops = db.fetch_all_crops()
    return jsonify({
        "soil_types": sorted({c["soil_type"] for c in crops}),
        "locations": sorted({c["location"] for c in crops}),
    })


@app.route("/api/predict", methods=["POST"])
def predict():
    data = request.get_json(force=True) or {}

    def to_float(key):
        value = data.get(key)
        return None if value in (None, "") else float(value)

    try:
        user = {
            "ph": to_float("ph"),
            "moisture": to_float("moisture"),
            "temperature": to_float("temperature"),
            "rainfall": to_float("rainfall"),
            "nitrogen": to_float("nitrogen"),
            "phosphorus": to_float("phosphorus"),
            "potassium": to_float("potassium"),
            "soil_type": (data.get("soil_type") or "").strip(),
            "location": (data.get("location") or "").strip(),
        }
    except (TypeError, ValueError):
        return jsonify({"error": "Please provide valid numeric values."}), 400

    required = ("ph", "moisture", "temperature", "rainfall")
    if any(user[key] is None for key in required):
        return jsonify({"error": "pH, moisture, temperature, and rainfall are required."}), 400

    ranked = rank_crops(user, db.fetch_all_crops())
    return jsonify({"top_match": ranked[0], "alternatives": ranked[1:4]})


@app.route("/api/upload-report", methods=["POST"])
def upload_report():
    file = request.files.get("report")
    if not file or not file.filename:
        return jsonify({"error": "No file uploaded."}), 400
    if not file.filename.lower().endswith(".pdf"):
        return jsonify({"error": "Please upload a PDF file."}), 400
    try:
        return jsonify(read_soil_report(file.stream))
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception:
        return jsonify({"error": "Could not read this PDF."}), 400


@app.route("/api/stats/meta")
def stats_meta():
    df = stats_dataframe()
    return jsonify({
        "targets": sa.TARGETS,
        "variables": sa.NUMERIC_VARS,
        "groups": {col: sorted(df[col].dropna().unique().tolist()) for col in sa.GROUP_COLS},
    })


@app.route("/api/stats/regression")
def stats_regression():
    return run_stats(sa.run_regression, request.args.get("target", "nitrogen"))


@app.route("/api/stats/ttest")
def stats_ttest():
    args = request.args
    return run_stats(
        sa.run_t_test,
        args.get("variable"), args.get("group_col"), args.get("group_a"), args.get("group_b"),
    )


@app.route("/api/stats/anova")
def stats_anova():
    args = request.args
    return run_stats(sa.run_anova, args.get("variable"), args.get("group_col"))


if __name__ == "__main__":
    app.run(debug=True)