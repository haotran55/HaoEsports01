from fastapi import FastAPI, Query
import requests

app = FastAPI()

API_KEY = "qqwweerrb"
API_URL = "https://freefirelike-api.onrender.com/like"

@app.get("/like")
def like_player(uid: str = Query(...), region: str = Query(...)):
    params = {
        "uid": uid,
        "server_name": region,
        "key": API_KEY
    }
    
    try:
        response = requests.get(API_URL, params=params)
        response.raise_for_status()  # Gây lỗi nếu mã trạng thái không phải 200

        data = response.json()
        
        # Xóa trường "owner" nếu có
        if isinstance(data, dict) and "owner" in data:
            del data["owner"]

        return data

    except requests.exceptions.RequestException as e:
        return {"error": "Failed to fetch from API", "detail": str(e)}

    except ValueError:
        return {"error": "Invalid JSON returned from API"}
