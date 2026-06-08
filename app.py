import os
import time
from flask import Flask, request, jsonify, Response

app = Flask(__name__)

# الحسابات المقبولة (العادية والمقلوبة من الرسيفر)
MY_USERNAME = "assil"
MY_PASSWORD = "2026password"

# الأقسام الثابتة التي تظهر في الرسيفر فوراً
CATEGORIES = [
    {"category_id": "1", "category_name": "⚽ ASSIL SPORTS", "parent_id": 0},
    {"category_id": "2", "category_name": "📰 ASSIL NEWS", "parent_id": 0},
    {"category_id": "3", "category_name": "📺 ASSIL GENERAL", "parent_id": 0}
]

# القنوات بروابط بث مباشرة رسمية ومفتوحة 24 ساعة (تشتغل فوراً وبدون بحث أو تعليق)
CHANNELS_DATA = [
    {
        "stream_id": 101, 
        "name": "BEIN SPORTS NEWS", 
        "category_id": "1", 
        "url": "https://beinsports.akamaized.net/ps/g_news/index.m3u8",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/c/c5/BeIN_Sports_Logo.svg"
    },
    {
        "stream_id": 102, 
        "name": "AD SPORTS 1 - أبوظبي الرياضية", 
        "category_id": "1", 
        "url": "https://adsports1.akamaized.net/hls/live/2018223/adsports1/master.m3u8",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/2/28/Abu_Dhabi_Sports_logo.svg"
    },
    {
        "stream_id": 201, 
        "name": "AL JAZEERA ARABIC - الجزيرة", 
        "category_id": "2", 
        "url": "https://live-fta-gma.allatv.co/jazeera/index.m3u8",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/7/70/Al_Jazeera_English_2011.svg"
    },
    {
        "stream_id": 202, 
        "name": "AL ARABIYA - العربية", 
        "category_id": "2", 
        "url": "https://live.alarabiya.net/alarabiya/alarabiya.m3u8",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/8/82/Al_Arabiya_Logo.svg"
    },
    {
        "stream_id": 301, 
        "name": "القرآن الكريم بث مباشر", 
        "category_id": "3", 
        "url": "https://win.holol.com/live/quran/playlist.m3u8",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/7/7b/Saudi_Quran_TV_logo.svg"
    },
    {
        "stream_id": 302, 
        "name": "السنة النبوية بث مباشر", 
        "category_id": "3", 
        "url": "https://win.holol.com/live/sunnah/playlist.m3u8",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/e/e4/Saudi_Sunnah_TV_logo.svg"
    }
]

def validate_client(username, password):
    if username == MY_USERNAME and password == MY_PASSWORD:
        return True
    if username == "80" and password == "assil":
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
                "num": ch["stream_id"], 
                "name": ch["name"], 
                "stream_type": "live",
                "stream_id": ch["stream_id"], 
                "stream_icon": ch["logo"],
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

    # إعادة التوجيه الفورية للبث لحماية السيرفر من التعليق
    return Response(status=302, headers={"Location": target_channel["url"]})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
