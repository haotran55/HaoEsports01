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
    response = requests.get(API_URL, params=params)

    if response.status_code != 200:
        return {"error": "Failed to fetch data from upstream API."}

    data = response.json()

    # Xóa khóa "owner" nếu tồn tại
    if "owner" in data:
        del data["owner"]

    return data
