from flask import Flask, request, jsonify
import requests
import base64
import json

app = Flask(__name__)

# === CONFIG ===
GITHUB_TOKEN = "HANOICITYTOKEN"
REPO = "iNeedFreedom"  # e.g. phongdang/MyGameRepo
FILE_PATH = "HaNoiCity_DuLieu"  # path inside repo

API_URL = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

# === ROUTE ===
@app.route("/decrease", methods=["POST"])
def decrease_value():
    try:
        # 1. Read how much to decrease (default = 1)
        body = request.json or {}
        dec = body.get("decrease", 1)

        # 2. GET the current file
        r = requests.get(API_URL, headers=HEADERS)
        if r.status_code != 200:
            return jsonify({"error": "Failed to fetch file", "details": r.text}), 400
        file_data = r.json()

        # Decode base64 → JSON
        decoded = base64.b64decode(file_data["content"]).decode("utf-8")
        data = json.loads(decoded)

        # 3. Modify
        if "HNCTCAR left" not in data:
            return jsonify({"error": "'HNCTCAR left' not found in file"}), 400
        data["HNCTCAR left"] = max(0, data["HNCTCAR left"] - dec)

        # 4. Encode new content
        new_content = json.dumps(data, indent=2)
        encoded = base64.b64encode(new_content.encode("utf-8")).decode("utf-8")

        # 5. PUT update back
        payload = {
            "message": f"Decrease HNCTCAR left by {dec}",
            "content": encoded,
            "sha": file_data["sha"]
        }
        r = requests.put(API_URL, headers=HEADERS, data=json.dumps(payload))
        if r.status_code not in [200, 201]:
            return jsonify({"error": "Failed to update file", "details": r.text}), 400

        return jsonify({"success": True, "new_value": data["HNCTCAR left"]})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
