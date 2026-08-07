import os
import random
import requests
from flask import Flask, render_template, request, jsonify
import libsql

app = Flask(__name__)

def get_db():
    url = os.getenv("TURSO_URL")
    token = os.getenv("TURSO_TOKEN")
    if not url or not token:
        raise ValueError("Missing TURSO_URL or TURSO_TOKEN environment variables.")
    conn = libsql.connect(url, auth_token=token)
    return conn, conn.cursor()

def upload_to_catbox(file_obj):
    """Uploads a local image file binary directly to Catbox API."""
    catbox_api = "https://catbox.moe/user/api.php"
    files = {
        'fileToUpload': (file_obj.filename, file_obj.stream, file_obj.mimetype)
    }
    data = {
        'reqtype': 'fileupload'
    }
    
    response = requests.post(catbox_api, data=data, files=files, timeout=15)
    result = response.text.strip()
    
    if response.status_code == 200 and result.startswith("https://files.catbox.moe/"):
        return result
    else:
        raise Exception(f"Catbox Upload Error: {result}")

def generate_unique_card_id(cursor):
    """Ensures the 6-digit Card ID does not already exist in the database."""
    while True:
        candidate_id = str(random.randint(100000, 999999))
        cursor.execute("SELECT 1 FROM cards WHERE card_id = ?", (candidate_id,))
        if not cursor.fetchone():
            return candidate_id

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/add-card", methods=["POST"])
def add_card():
    try:
        name = request.form.get("name", "").strip()
        rarity = request.form.get("rarity", "").strip()
        value_str = request.form.get("value", "").strip()
        upload_type = request.form.get("upload_type", "url") # 'file' or 'url'

        # Validations
        if not name or not rarity or not value_str:
            return jsonify({"success": False, "error": "Name, rarity, and value are required fields."}), 400

        try:
            value = int(value_str)
        except ValueError:
            return jsonify({"success": False, "error": "Value must be a valid integer."}), 400

        # Process Image URL
        image_url = ""
        if upload_type == "file":
            if 'image_file' not in request.files or request.files['image_file'].filename == '':
                return jsonify({"success": False, "error": "Please select a file to upload."}), 400
            
            image_file = request.files['image_file']
            image_url = upload_to_catbox(image_file)

        elif upload_type == "url":
            image_url = request.form.get("image_url", "").strip()
            if not image_url:
                return jsonify({"success": False, "error": "Please paste an image URL."}), 400

        # Database operations
        conn, cursor = get_db()

        # Check if card name already exists
        cursor.execute("SELECT 1 FROM cards WHERE name = ?", (name,))
        if cursor.fetchone():
            return jsonify({"success": False, "error": f"A card named '{name}' already exists!"}), 400

        # Generate unique 6-digit ID
        card_id = generate_unique_card_id(cursor)

        # Insert Card
        cursor.execute(
            "INSERT INTO cards (card_id, name, rarity, value, image) VALUES (?, ?, ?, ?, ?)",
            (card_id, name, rarity, value, image_url)
        )
        conn.commit()

        return jsonify({
            "success": True,
            "message": f"Card '{name}' added successfully!",
            "card_id": card_id,
            "image_url": image_url
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)

