from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import datetime 
from color_analysis import analyze_five_zones


app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 首頁
@app.route("/")
def home():
    return render_template("index.html")

# 歷史頁面
@app.route("/history")
def history():
    return render_template("history.html")

# 上傳圖片並進行五區診斷與主色分析
@app.route("/upload", methods=["POST"])
def upload_image():
    if 'image' not in request.files:
        return "No image uploaded", 400
    image = request.files['image']

    patient_id = request.form.get('patient_id', '').strip()
    if not patient_id:
        return "Missing patient ID", 400

    # 建立資料夾並儲存圖片
    patient_folder = os.path.join(UPLOAD_FOLDER, patient_id)
    os.makedirs(patient_folder, exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{patient_id}_{timestamp}.jpg"
    filepath = os.path.join(patient_folder, filename)
    image.save(filepath)

    # 分析主色（中央區域）
    five_zone_result = analyze_five_zones(filepath)

    # 從五區中選出一個代表主色（例如舌中 / 脾胃區）
    main_zone = "脾胃"
    main_info = five_zone_result.get(main_zone, {})
    main_color = main_info.get("顏色", "未知")
    comment = main_info.get("推論", "無法判斷")
    rgb = main_info.get("RGB", [0, 0, 0])

    return jsonify({
        "filename": filename,
        "主色RGB": rgb,
        "舌苔主色": main_color,
        "中醫推論": comment,
        "五區診斷": five_zone_result
    })
# 列出某病人所有照片
@app.route("/photos", methods=["GET"])
def list_photos():
    patient_id = request.args.get("patient", "").strip()
    if not patient_id:
        return jsonify([])
    folder = os.path.join(UPLOAD_FOLDER, patient_id)
    if not os.path.exists(folder):
        return jsonify([])
    files = sorted(os.listdir(folder), reverse=True)
    urls = [f"/uploads/{patient_id}/{fname}" for fname in files]
    return jsonify(urls)

# 提供上傳圖片
@app.route("/uploads/<patient>/<filename>")
def uploaded_file(patient, filename):
    folder = os.path.join(UPLOAD_FOLDER, patient)
    return send_from_directory(folder, filename)

# 所有病人清單
@app.route("/patients", methods=["GET"])
def list_patients():
    try:
        folders = [
            name for name in os.listdir(UPLOAD_FOLDER)
            if os.path.isdir(os.path.join(UPLOAD_FOLDER, name))
        ]
        return jsonify(sorted(folders))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 啟動應用程式（本機 or Render）
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
