import os
import random
import requests
from flask import Flask, render_template, request, jsonify

# Fallback mechanism in case Vercel fails to load native C-bindings for libsql
try:
    import libsql
    HAS_LIBSQL = True
except ImportError:
    HAS_LIBSQL = False

app = Flask(__name__)

# Turso DB Configuration (Pulled from Environment Variables)
TURSO_URL = os.getenv("TURSO_URL", "")
TURSO_TOKEN = os.getenv("TURSO_TOKEN", "")

def execute_query_http(sql, params=()):
    """Executes SQL query using Turso REST HTTP API (Pure Python fallback for serverless)."""
    if not TURSO_URL or not TURSO_TOKEN:
        raise Exception("TURSO_URL or TURSO_TOKEN environment variables are missing on Vercel.")

    http_url = TURSO_URL.replace("libsql://", "https://").rstrip("/") + "/v2/pipeline"
    
    args = []
    for param in params:
        if isinstance(param, int):
            args.append({"type": "integer", "value": str(param)})
        elif param is None:
            args.append({"type": "null"})
        else:
            args.append({"type": "text", "value": str(param)})

    payload = {
        "requests": [
            {
                "type": "execute",
                "stmt": {
                    "sql": sql,
                    "args": args
                }
            },
            {"type": "close"}
        ]
    }
    
    headers = {
        "Authorization": f"Bearer {TURSO_TOKEN}",
        "Content-Type": "application/json"
    }
    
    res = requests.post(http_url, json=payload, headers=headers, timeout=10)
    if res.status_code != 200:
        raise Exception(f"Turso HTTP Error ({res.status_code}): {res.text}")
    
    return res.json()

def execute_query(sql, params=()):
    """Executes query using either native libsql driver or HTTP fallback."""
    if HAS_LIBSQL:
        conn = libsql.connect(TURSO_URL, auth_token=TURSO_TOKEN)
        cursor = conn.cursor()
        cursor.execute(sql, params)
        conn.commit()
        conn.close()
    else:
        execute_query_http(sql, params)

def upload_file_to_catbox(file_storage):
    """Uploads local image file directly to Catbox and returns the hosted URL."""
    url = "https://catbox.moe/user/api.php"
    data = {"reqtype": "fileupload"}
    files = {"fileToUpload": (file_storage.filename, file_storage.stream, file_storage.content_type)}
    
    response = requests.post(url, data=data, files=files, timeout=15)
    
    if response.status_code == 200 and response.text.startswith("https://files.catbox.moe/"):
        return response.text.strip()
    else:
        raise Exception(f"Catbox Upload Failed: {response.text}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/add-card', methods=['POST'])
def add_card():
    try:
        name = request.form.get('name', '').strip()
        rarity = request.form.get('rarity', '').strip()
        value = request.form.get('value', type=int)
        image_type = request.form.get('image_type')

        if not name or not rarity or value is None:
            return jsonify({
                "success": False, 
                "message": "All fields (Name, Rarity, Value) are required!",
                "error": "All fields (Name, Rarity, Value) are required!"
            }), 400

        final_image_url = ""

        if image_type == 'file':
            if 'image_file' not in request.files or request.files['image_file'].filename == '':
                return jsonify({
                    "success": False, 
                    "message": "Please attach an image file!",
                    "error": "Please attach an image file!"
                }), 400
            
            image_file = request.files['image_file']
            final_image_url = upload_file_to_catbox(image_file)

        elif image_type == 'url':
            final_image_url = request.form.get('image_url', '').strip()
            if not final_image_url:
                return jsonify({
                    "success": False, 
                    "message": "Please enter an image URL!",
                    "error": "Please enter an image URL!"
                }), 400
        else:
            return jsonify({
                "success": False, 
                "message": "Invalid image submission type.",
                "error": "Invalid image submission type."
            }), 400

        # Generate 6-digit card_id string matching bot logic
        card_id = str(random.randint(100000, 999999))

        # Save to database
        sql = 'INSERT INTO cards (card_id, name, rarity, value, image) VALUES (?, ?, ?, ?, ?)'
        params = (card_id, name, rarity, value, final_image_url)
        execute_query(sql, params)

        return jsonify({
            "success": True, 
            "message": f"Card '{name}' added successfully!",
            "card": {
                "card_id": card_id,
                "name": name,
                "rarity": rarity,
                "value": value,
                "image": final_image_url
            }
        })

    except Exception as e:
        err_msg = str(e)
        return jsonify({
            "success": False, 
            "message": err_msg, 
            "error": err_msg
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
        
