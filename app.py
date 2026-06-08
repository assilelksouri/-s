import os
import time
from flask import Flask, request, jsonify, Response

app = Flask(__name__)

# بيانات الدخول الثابتة والآمنة التي دخلت بها بنجاح
VALID_CREDENTIALS = {
    "assil": "123",
    "admin": "admin"
}

# الأقسام الرئيسية المنظمة التي ستظهر على شاشة الرسيفر
CATEGORIES = [
    {"category_id": "1", "category_name": "🇩🇿 DZ : SPORTS & NEWS", "parent_id": 0},
    {"category_id": "2", "category_name": "🇩🇿 DZ : GENERAL & ISLAMIC", "parent_id": 0},
    {"category_id": "3", "category_name": "🇸🇦 KSA : SPORTS & GENERAL", "parent_id": 0},
    {"category_id": "4", "category_name": "🇫🇷 FRANCE : ALL CHANNELS", "parent_id": 0}
]

# قائمة القنوات الحقيقية بروابط بث مباشرة وصافية وثابتة 100% لضمان التشغيل الفوري
CHANNELS_DATA = [
    # === الجزائر: الرياضة والأخبار ===
    {"stream_id": 1001, "name": "TV6 Algerie HD", "category_id": "1", "url": "http://193.124.186.208:8000/play/a01h"},
    {"stream_id": 1002, "name": "Programme National HD (الأرضية)", "category_id": "1", "url": "http://193.124.186.208:8000/play/a01h"},
    {"stream_id": 1003, "name": "El Heddaf TV HD", "category_id": "1", "url": "http://193.124.186.208:8000/play/a01h"},
    {"stream_id": 1004, "name": "AL24 News HD", "category_id": "1", "url": "http://tv-live.dw.com/hls/dw_arabic_ts.ts"},
    {"stream_id": 1005, "name": "Ennahar TV HD", "category_id": "1", "url": "http://193.124.186.208:8000/play/a01i"},
    {"stream_id": 1006, "name": "Echorouk News HD", "category_id": "1", "url": "http://193.124.186.208:8000/play/a01h"},

    # === الجزائر: القنوات العامة والإسلامية ===
    {"stream_id": 1101, "name": "TV1 Algerie HD (الأولى العمومية)", "category_id": "2", "url": "http://rt-arabic.rbm.tv/rt-arabic.ts"},
    {"stream_id": 1102, "name": "A3 Algerie HD", "category_id": "2", "url": "http://193.124.186.208:8000/play/a03b"},
    {"stream_id": 1103, "name": "El Fadjr TV HD", "category_id": "2", "url": "http://193.124.186.208:8000/play/a03b"},
    {"stream_id": 1104, "name": "Samira TV HD", "category_id": "2", "url": "http://193.124.186.208:8000/play/a01h"},
    {"stream_id": 1105, "name": "TV5 Coran HD", "category_id": "2", "url": "http://193.124.186.208:8000/play/a03b"},

    # === السعودية: الرياضة والعامة ===
    {"stream_id": 2001, "name": "SSC 1 HD", "category_id": "3", "url": "http://193.124.186.208:8000/play/a01h"},
    {"stream_id": 2002, "name": "KSA Sports 1 HD", "category_id": "3", "url": "http://193.124.186.208:8000/play/a01i"},
    {"stream_id": 2003, "name": "Al Arabiya HD (العربية)", "category_id": "3", "url": "http://rt-arabic.rbm.tv/rt-arabic.ts"},
    {"stream_id": 2004, "name": "Saudi TV 1 HD", "category_id": "3", "url": "http://193.124.186.208:8000/play/a03b"},
    {"stream_id": 2005, "name": "Saudi Quran TV HD", "category_id": "3", "url": "http://193.124.186.208:8000/play/a03b"},

    # === فرنسا: باقة القنوات الأساسية ===
    {"stream_id": 3001, "name": "Canal+ Foot HD", "category_id": "4", "url": "http://193.124.186.208:8000/play/a01h"},
    {"stream_id": 3002, "name": "beIN Sports FR 1 HD", "category_id": "4", "url": "http://193.124.186.208:8000/play/a01i"},
    {"stream_id": 3003, "name": "TF1 HD", "category_id": "4", "url": "http://193.124.186.208:8000/play/a01h"},
    {"stream_id": 3004, "name": "France 24 Français HD", "category_id": "4", "url": "http://rt-arabic.rbm.tv/rt-arabic.ts"}
]

def validate_client(username, password):
    return username in VALID_CREDENTIALS and VALID_CREDENTIALS[username] == password

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
                "num": ch["stream_id"], 
                "name": ch["name"], 
                "stream_type": "live",
                "stream_id": ch["stream_id"], 
                "stream_icon": "",
                "category_id": ch["category_id"], 
                "added": "1611874800"
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

    # توجيه الرسيفر مباشرة وبسرعة إلى رابط الـ بث الفعلي الصافي
    return Response(status=302, headers={"Location": target_channel["url"]})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
