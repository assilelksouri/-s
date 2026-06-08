import os
import time
from flask import Flask, request, jsonify, Response

app = Flask(__name__)

# بيانات دخول متعددة لضمان الدخول تحت أي ظرف وبدون أخطاء
VALID_CREDENTIALS = {
    "assil": "2026password",
    "80": "assil",
    "admin": "admin"
}

# الأقسام الأساسية المنظمة
CATEGORIES = [
    {"category_id": "1", "category_name": "🇩🇿 DZ : SPORTS", "parent_id": 0},
    {"category_id": "2", "category_name": "🇩🇿 DZ : NEWS & GENERAL", "parent_id": 0},
    {"category_id": "3", "category_name": "🇸🇦 KSA : ALL CHANNELS", "parent_id": 0},
    {"category_id": "4", "category_name": "🇫🇷 FRANCE : ALL CHANNELS", "parent_id": 0}
]

# القنوات الحية والمستقرة بصيغة .ts
CHANNELS_DATA = [
    {"stream_id": 101, "name": "TV6 Algerie HD", "category_id": "1", "url": "http://193.124.186.208:8000/play/a01h"},
    {"stream_id": 102, "name": "El Heddaf TV HD", "category_id": "1", "url": "http://193.124.186.208:8000/play/a01h"},
    {"stream_id": 201, "name": "AL24 News HD", "category_id": "2", "url": "http://tv-live.dw.com/hls/dw_arabic_ts.ts"},
    {"stream_id": 202, "name": "TV1 Algerie HD", "category_id": "2", "url": "http://rt-arabic.rbm.tv/rt-arabic.ts"},
    {"stream_id": 203, "name": "A3 Algerie HD", "category_id": "2", "url": "http://193.124.186.208:8000/play/a03b"},
    {"stream_id": 204, "name": "Ennahar TV HD", "category_id": "2", "url": "http://193.124.186.208:8000/play/a01i"},
    {"stream_id": 205, "name": "Echorouk TV HD", "category_id": "2", "url": "http://193.124.186.208:8000/play/a01h"},
    {"stream_id": 301, "name": "Saudi TV 1 HD", "category_id": "3", "url": "http://193.124.186.208:8000/play/a03b"},
    {"stream_id": 302, "name": "Saudi Quran TV HD", "category_id": "3", "url": "http://193.124.186.208:8000/play/a03b"},
    {"stream_id": 401, "name": "France 24 Français HD", "category_id": "4", "url": "http://rt-arabic.rbm.tv/rt-arabic.ts"}
]

def validate_client(username, password):
    if username in VALID_CREDENTIALS and VALID_CREDENTIALS[username] == password:
        return True
    return False

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
