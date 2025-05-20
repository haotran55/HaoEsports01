from flask import Flask, request, jsonify, send_file
import requests
from PIL import Image
from io import BytesIO

app = Flask(__name__)

# Base image URL (ảnh vòng tròn 8 ô)
BASE_IMAGE_URL = "https://iili.io/3iSrn5u.jpg"

# API Key whitelist
API_KEYS = {
    "tranhao116": True,
    "2DAY": False,
    "busy": False
}

def is_key_valid(api_key):
    return API_KEYS.get(api_key, False)

def fetch_data(region, uid):
    """Lấy dữ liệu từ API Free Fire."""
    url = f"https://ffwlxd-info.vercel.app/player-info?region={region}&uid={uid}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def overlay_images(base_image_url, item_ids):
    """Chồng item lên ảnh gốc theo bố cục vòng tròn."""
    try:
        base = Image.open(BytesIO(requests.get(base_image_url).content)).convert("RGBA")
    except Exception as e:
        print(f"Error loading base image: {e}")
        return None

    # Tọa độ các vị trí theo hình tròn (720x720)
    positions = [
        (360, 90),    # Top
        (515, 145),   # Top-right
        (615, 265),   # Right
        (610, 420),   # Bottom-right
        (495, 540),   # Bottom
        (225, 540),   # Bottom-left
        (110, 420),   # Left
        (105, 265)    # Top-left
    ]
    size = (110, 110)

    for idx in range(min(8, len(item_ids))):
        item_id = item_ids[idx]
        item_url = f"https://pika-ffitmes-api.vercel.app/?item_id={item_id}&watermark=TaitanApi&key=PikaApis"

        try:
            item_img = Image.open(BytesIO(requests.get(item_url).content)).convert("RGBA")
            item_img = item_img.resize(size, Image.LANCZOS)

            # Canh giữa hình khi dán vào base image
            pos_x = positions[idx][0] - size[0] // 2
            pos_y = positions[idx][1] - size[1] // 2

            base.paste(item_img, (pos_x, pos_y), item_img)
        except Exception as e:
            print(f"Error processing item {item_id}: {e}")
            continue

    return base

@app.route('/api/image', methods=['GET'])
def generate_image():
    region = request.args.get('region')
    uid = request.args.get('uid')
    api_key = request.args.get('key')

    if not all([region, uid, api_key]):
        return jsonify({"error": "Missing region, uid, or key parameter"}), 400

    if not is_key_valid(api_key):
        return jsonify({"error": "Invalid or inactive API key"}), 403

    data = fetch_data(region, uid)
    if not data or "AccountProfileInfo" not in data or "EquippedOutfit" not in data["AccountProfileInfo"]:
        return jsonify({"error": "Failed to fetch data. Recheck uid and region"}), 500

    item_ids = data["AccountProfileInfo"]["EquippedOutfit"][:8]

    final_image = overlay_images(BASE_IMAGE_URL, item_ids)
    if final_image is None:
        return jsonify({"error": "Failed to generate image"}), 500

    img_io = BytesIO()
    final_image.save(img_io, 'PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
