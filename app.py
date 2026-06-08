import os
import time
from flask import Flask, request, jsonify, Response

app = Flask(__name__)

# بيانات دخول بسيطة وقوية جداً
MY_USERNAME = "assil"
MY_PASSWORD = "123"

# الأقسام الأساسية فقط لتجنب أي ثقل
CATEGORIES = [
    {"category_id": "1", "category_name": "🇩🇿 ALGERIA", "parent_id": 0},
    {"category_id": "2", "category_name": "🇸🇦 SAUDI & NEWS", "parent_id": 0}
]

# قنوات رسمية ومباشرة وخفيفة جداً من سيرفرات عالمية موثوقة
CHANNELS_DATA = [
    {"stream_id": 101, "name": "TV1 ALGERIE", "category_id": "1", "url": "https://rt-arabic.rbm.tv/rt-arabic.ts"},
    {"stream_id": 102, "name": "AL24 NEWS", "category_id": "1", "url": "https://tv-live.dw.com/hls/dw_arabic_ts.ts"},
    {"stream_id": 201, "name": "SAUDI QURAN", "category_id": "2", "url": "https://rt-arabic.rbm.tv/rt-arabic.ts"},
    {"stream_id": 202, "name": "RT ARABIC", "category_id": "2", "url": "https://rt-arabic.rbm.tv/rt-arabic.ts"}
]

def validate_client(username, password):
    return username == MY_USERNAME and password == MY_PASSWORD

@app.route('/player_api.php')
def player_api():
    user = request.args.get("username")
    pwd = request.args.get("password")
    
    if not validate_client(user, pwd):
        return jsonify({"user_info": {"auth": 0, "status": "Not Authorized"}}), 403

    action = request.args.get("action")

    if not action:
        return jsonify({
            "user_info": {
                "username": user, "password": pwd, "auth": 1,
                "status": "Active", "exp_date": "1803744000", "is_trial": "0",
                "active_cons": "0", "max_connections": "5"
            },
            "server_info": {
                "url": request.host, "port": "80", "https_port": "443",
                "server_time": str(int(time.time())), "timezone": "Africa/Algiers"
            }
        })

    elif action == "get_live_categories":
        return jsonify(CATEGORIES)

    elif action == "get_live_streams":
        category_id = request.args.get("category_id")
        xtream_channels = []
        for ch in CHANNELS_DATA:
            if category_id and ch["category_id"] != category_id:
                continue
            xtream_channels.append({
                "num": ch["stream_id"], "name": ch["name"], "stream_type": "live",
                "stream_id": ch["stream_id"], "stream_icon": "",
                "category_id": ch["category_id"], "added": "1611874800"
            })
        return jsonify(xtream_channels)

    return jsonify([])

@app.route('/live/<username>/<password>/<int:stream_id>.ts')
@app.route('/live/<username>/<password>/<int:stream_id>')
def stream_proxy(username, password, stream_id):
    if not validate_client(username, password):
        return "Unauthorized", 403
    target_channel = next((ch for ch in CHANNELS_DATA if ch["stream_id"] == stream_id), None)
    if not target_channel:
        return "Channel Not Found", 404
    return Response(status=302, headers={"Location": target_channel["url"]})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
