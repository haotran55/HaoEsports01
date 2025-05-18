from fastapi import FastAPI, Query
import requests

app = FastAPI()

API_KEY = "qqwweerrb"
API_URL = "160.250.137.144:5001/like"

@app.get("/haoesports")
def like_player(uid: str = Query(...), region: str = Query(...)):
    params = {
        "uid": uid,
        "server_name": region,
        "key": API_KEY
    }

    try:
        response = requests.get(API_URL, params=params)
        response.raise_for_status()

        try:
            data = response.json()
        except ValueError:
            return {"error": "API phụ trả về dữ liệu không hợp lệ (không phải JSON)."}

        # Kiểm tra dữ liệu trả về có hợp lệ hay không
        if not data.get("UID") or not data.get("PlayerNickname"):
            return {
                "error": "API phụ trả về lỗi.",
                "message": data.get("message", "UID không hợp lệ hoặc server đang lỗi."),
                "raw_data": data
            }

        # Xóa trường 'owner' nếu có
        data.pop("owner", None)

        return data

    except requests.exceptions.HTTPError:
        if response.status_code == 500:
            return {"error": "Lỗi máy chủ từ API phụ. Vui lòng thử lại sau."}
        elif response.status_code == 404:
            return {"error": "Không tìm thấy UID hoặc vùng máy chủ không hợp lệ."}
        else:
            return {"error": f"Lỗi HTTP từ API phụ ({response.status_code})."}

    except requests.exceptions.RequestException:
        return {"error": "Không thể kết nối tới API phụ. Kiểm tra mạng hoặc thử lại sau."}
