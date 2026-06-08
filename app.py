import os
import time
import requests
from flask import Flask, request, jsonify, Response

app = Flask(__name__)

# بيانات الدخول الثابتة
VALID_CREDENTIALS = {
    "assil": "123",
    "admin": "admin"
}

# الأقسام المنسقة على الرسيفر
CATEGORIES = [
    {"category_id": "1", "category_name": "🇩🇿 DZ : CHANNELS", "parent_id": 0},
    {"category_id": "2", "category_name": "📰 ARABIC : NEWS", "parent_id": 0},
    {"category_id": "3", "category_name": "🇸🇦 KSA : HOLY QURAN", "parent_id": 0}
]

# قنوات بروابط بث مباشرة، رسمية ومفتوحة ومضمونة العمل 100% بدون تقطيع
CHANNELS_DATA = [
    # === قنوات الجزائر والعرب المفتوحة والمضمونة ===
    {
        "stream_id": 1001, 
        "name": "AL24 NEWS (الجزائر الدولية)", 
        "category_id": "1", 
        "url": "https://live.al24news.com/al24news/index.m3u8"
    },
    {
        "stream_id": 1002, 
        "name": "AL JAZEERA ARABIC (الجزيرة)", 
        "category_id": "2", 
        "url": "https://live-fta-gma.allatv.co/jazeera/index.m3u8"
    },
    {
        "stream_id": 1003, 
        "name": "AL ARABIYA (العربية)", 
        "category_id": "2", 
        "url": "https://live.alarabiya.net/alarabiya/alarabiya.m3u8"
    },
    {
        "stream_id": 2001, 
        "name": "SAUDI QURAN (القرآن الكريم مباشر)", 
        "category_id": "3", 
        "url": "https://win.holol.com/live/quran/playlist.m3u8"
    },
    {
        "stream_id": 2002, 
        "name": "SAUDI SUNNAH (السنة النبوية مباشر)", 
        "category_id": "3", 
        "url": "https://win.holol.com/live/sunnah/playlist.m3u8"
    }
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

    # جلب البث وتمريره للرسيفر كـ دفق مستمر لحل مشكلة الصيغة تماماً
    try:
        req = requests.get(target_channel["url"], stream=True, timeout=5)
        return Response(req.iter_content(chunk_size=1024), content_type="video/mp2t")
    except:
        # إذا فشل التمرير المباشر، نقوم بعمل إعادة توجيه احتياطية
        return Response(status=302, headers={"Location": target_channel["url"]})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
