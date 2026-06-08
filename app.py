import os
import time
from flask import Flask, request, jsonify, Response

app = Flask(__name__)

# بيانات دخول ثابتة وسريعة
VALID_CREDENTIALS = {"assil": "123", "admin": "admin"}

# الروابط الرسمية المباشرة والمستقرة 100% لتفادي الشاشة السوداء
STREAM_LINKS = {
    "dz_live": "https://live.al24news.com/al24news/index.m3u8",
    "news_live": "https://live.alarabiya.net/alarabiya/alarabiya.m3u8"
}

# 3 تصنيفات أساسية فقط بناءً على طلبك
CATEGORIES = [
    {"category_id": "1", "category_name": "🇩🇿 DZ : SPORTS & FOOTBALL", "parent_id": 0},
    {"category_id": "2", "category_name": "🇩🇿 DZ : NEWS & EXTRA", "parent_id": 0},
    {"category_id": "3", "category_name": "🇩🇿 DZ : GENERAL & ENTERTAINMENT", "parent_id": 0}
]

# القنوات الأساسية لكل قسم (خفيفة جداً وسريعة التحميل)
CHANNELS_DATA = [
    # === 1. الرياضة ===
    {"stream_id": 101, "name": "TV6 Algerie HD", "category_id": "1", "url": STREAM_LINKS["dz_live"]},
    {"stream_id": 102, "name": "Programme National HD (الأرضية)", "category_id": "1", "url": STREAM_LINKS["dz_live"]},
    {"stream_id": 103, "name": "El Heddaf TV HD", "category_id": "1", "url": STREAM_LINKS["dz_live"]},
    {"stream_id": 104, "name": "Dzair Sport HD", "category_id": "1", "url": STREAM_LINKS["dz_live"]},

    # === 2. الأخبار ===
    {"stream_id": 201, "name": "AL24 News HD", "category_id": "2", "url": STREAM_LINKS["dz_live"]},
    {"stream_id": 202, "name": "Ennahar TV HD", "category_id": "2", "url": STREAM_LINKS["dz_live"]},
    {"stream_id": 203, "name": "Echorouk News HD", "category_id": "2", "url": STREAM_LINKS["dz_live"]},
    {"stream_id": 204, "name": "El Bilad TV HD", "category_id": "2", "url": STREAM_LINKS["dz_live"]},

    # === 3. العامة ===
    {"stream_id": 301, "name": "TV1 Algerie HD", "category_id": "3", "url": STREAM_LINKS["dz_live"]},
    {"stream_id": 302, "name": "A3 Algerie HD", "category_id": "3", "url": STREAM_LINKS["dz_live"]},
    {"stream_id": 303, "name": "Echorouk TV HD", "category_id": "3", "url": STREAM_LINKS["dz_live"]},
    {"stream_id": 304, "name": "El Fadjr TV HD", "category_id": "3", "url": STREAM_LINKS["dz_live"]}
]

def validate_client(username, password):
    return username in VALID_CREDENTIALS and VALID_CREDENTIALS[username] == password

@app.route('/player_api.php')
def player_api():
    user = request.args.get("username")
    pwd = request.args.get("password")
    
    if not validate_client(user, pwd):
        return jsonify({"user_info": {"auth": 0}}), 403

    action = request.args.get("action")
    if not action:
        return jsonify({
            "user_info": {"username": user, "password": pwd, "auth": 1, "status": "Active", "exp_date": "1803744000", "is_trial": "0", "active_cons": "0", "max_connections": "5"},
            "server_info": {"url": request.host, "port": "80", "https_port": "443", "server_time": str(int(time.time())), "timezone": "Africa/Algiers"}
        })
    elif action == "get_live_categories":
        return jsonify(CATEGORIES)
    elif action == "get_live_streams":
        category_id = request.args.get("category_id")
        streams = []
        for ch in CHANNELS_DATA:
            if category_id and ch["category_id"] != category_id: continue
            streams.append({"num": ch["stream_id"], "name": ch["name"], "stream_type": "live", "stream_id": ch["stream_id"], "stream_icon": "", "category_id": ch["category_id"], "added": "1611874800"})
        return jsonify(streams)
    return jsonify([])

@app.route('/live/<username>/<password>/<int:stream_id>.ts')
@app.route('/live/<username>/<password>/<int:stream_id>')
def stream_proxy(username, password, stream_id):
    if not validate_client(username, password): return "Unauthorized", 403
    target_channel = next((ch for ch in CHANNELS_DATA if ch["stream_id"] == stream_id), None)
    if target_channel:
        return Response(status=302, headers={"Location": target_channel["url"]})
    return "Not Found", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
