import requests
from PIL import Image
from io import BytesIO

app = Flask(__name__)

# Base image URL
BASE_IMAGE_URL = "https://iili.io/39iE4rF.jpg"

# Example API keys (you can store these in a database or a config file)
API_KEYS = {
    "tranhao116": True,  # Active key
    "2DAY": True, # Inactive key
    "busy": False   # Active key
}

def is_key_valid(api_key):
    """Check if the provided API key is valid and active."""
    return API_KEYS.get(api_key, False)

def fetch_data(region, uid):
    """Fetch data from the new API based on region and uid."""
    url = f"http://hyper-full-info-api.vercel.app/info?uid={uid}&region={region}"
    
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching data: {response.status_code}, {response.text}")  # Print error details
        return None

def overlay_images(base_image, item_ids):
    """Overlay item images on the base image."""
    # Load the base image
    base = Image.open(BytesIO(requests.get(base_image).content)).convert("RGBA")
    
    # Define positions for each item (x, y)
    positions = [
        (485, 473),   # Position for item 1
        (295, 546),  # Position for item 2
        (290, 40),  # Position for item 3
        (479, 100),   # Position for item 4
        (550, 280),  # Position for item 5
        (100, 470)   # Position for item 6
    ]

    # Define sizes for each item (width, height)
    sizes = [
        (130, 130),   # Size for item 1
        (130, 130),   # Size for item 2
        (130, 130),   # Size for item 3
        (130, 130),   # Size for item 4
        (130, 130),   # Size for item 5
        (130, 130)    # Size for item 6
    ]
    
    for idx, item_id in enumerate(item_ids):
        item_image_url = f"https://pika-ffitmes-api.vercel.app/?item_id={item_id}&watermark=TaitanApi&key=PikaApis"
        item = Image.open(BytesIO(requests.get(item_image_url).content)).convert("RGBA")
        # Resize the item image using LANCZOS for high-quality downsampling
        item = item.resize((sizes[idx][0], sizes[idx][1]), Image.LANCZOS)
        base.paste(item, (positions[idx][0], positions[idx][1]), item)

    return base

@app.route('/api', methods=['GET'])
def api():
    """API endpoint to get the overlaid image."""
    region = request.args.get('region')
    uid = request.args.get('uid')
    api_key = request.args.get('key')  # Get the API key from the request

    if not region or not uid or not api_key:
        return jsonify({"error": "Missing region, uid, or key parameter"}), 400

    if not is_key_valid(api_key):
        return jsonify({"error": "Invalid or inactive API key"}), 403

    data = fetch_data(region, uid)
    if not data or "AccountProfileInfo" not in data or "EquippedOutfit" not in data["AccountProfileInfo"]:
        return jsonify({"error": "Failed to fetch data. Recheck uid and region"}), 500

    item_ids = data["AccountProfileInfo"]["EquippedOutfit"]
    
    # Ensure we only take the first 6 item IDs
    item_ids = item_ids[:6]

    # Overlay images on the base image
    overlaid_image = overlay_images(BASE_IMAGE_URL, item_ids)

    # Save the image to a BytesIO object
    img_io = BytesIO()
    overlaid_image.save(img_io, 'PNG')
    img_io.seek(0)

    return send_file(img_io, mimetype='image/png')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
#this code was made by cutehack
