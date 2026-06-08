import os
import time
from flask import Flask, request, jsonify, Response

app = Flask(__name__)
handler = app

# بيانات الدخول المعتمدة
VALID_CREDENTIALS = {"assil": "123", "admin": "admin"}

# الأقسام الرسمية بناءً على ملف IPTV_Categories_2026.txt
CATEGORIES = [
    {"category_id": "1", "category_name": "FR | GENERAL", "parent_id": 0},
    {"category_id": "2", "category_name": "FR | NEWS", "parent_id": 0},
    {"category_id": "3", "category_name": "FR | SPORT", "parent_id": 0},
    {"category_id": "4", "category_name": "DZ | NATIONAL", "parent_id": 0},
    {"category_id": "5", "category_name": "AR | NEWS", "parent_id": 0},
    {"category_id": "6", "category_name": "AR | ISLAMIC", "parent_id": 0},
    {"category_id": "7", "category_name": "BEIN | SPORTS", "parent_id": 0},
    {"category_id": "8", "category_name": "SSC | SPORTS", "parent_id": 0},
    {"category_id": "9", "category_name": "AR | SPORT", "parent_id": 0},
    {"category_id": "10", "category_name": "KIDS | INTERNATIONAL", "parent_id": 0},
    {"category_id": "11", "category_name": "DOCUMENTARY | WORLD", "parent_id": 0},
    {"category_id": "12", "category_name": "MUSIC | WORLD", "parent_id": 0},
    {"category_id": "13", "category_name": "MOVIES | CHANNELS", "parent_id": 0}
]

# مصادر البث الحية والمستقرة
STREAM_TS = "http://rt-arabic.rbm.tv/rt-arabic.ts"
STREAM_QURAN = "https://win.holol.com/live/quran/playlist.m3u8"
STREAM_SUNNAH = "https://win.holol.com/live/sunnah/playlist.m3u8"
STREAM_NEWS = "https://live.alarabiya.net/alarabiya/alarabiya.m3u8"

CHANNELS_DATA = [
    # ------ FR | GENERAL ------
    {"stream_id": 1001, "name": "TF1", "category_id": "1", "url": STREAM_TS},
    {"stream_id": 1002, "name": "France 2", "category_id": "1", "url": STREAM_TS},
    {"stream_id": 1003, "name": "France 3", "category_id": "1", "url": STREAM_TS},
    {"stream_id": 1006, "name": "M6", "category_id": "1", "url": STREAM_TS},
    {"stream_id": 1010, "name": "W9", "category_id": "1", "url": STREAM_TS},
    
    # ------ FR | NEWS ------
    {"stream_id": 2001, "name": "BFM TV", "category_id": "2", "url": STREAM_TS},
    {"stream_id": 2002, "name": "CNews", "category_id": "2", "url": STREAM_TS},
    {"stream_id": 2005, "name": "France 24 FR", "category_id": "2", "url": STREAM_NEWS},

    # ------ FR | SPORT ------
    {"stream_id": 3001, "name": "Canal+ Sport", "category_id": "3", "url": STREAM_TS},
    {"stream_id": 3002, "name": "Canal+ Foot", "category_id": "3", "url": STREAM_TS},
    {"stream_id": 3004, "name": "beIN Sports 1 FR", "category_id": "3", "url": STREAM_TS},

    # ------ DZ | NATIONAL ------
    {"stream_id": 4001, "name": "TV1 Algérie", "category_id": "4", "url": STREAM_TS},
    {"stream_id": 4002, "name": "Canal Algérie", "category_id": "4", "url": STREAM_TS},
    {"stream_id": 4003, "name": "Algérie 3", "category_id": "4", "url": STREAM_TS},
    {"stream_id": 4006, "name": "TV6 Jeunesse", "category_id": "4", "url": STREAM_TS},
    {"stream_id": 4011, "name": "Echourouk TV", "category_id": "4", "url": STREAM_TS},
    {"stream_id": 4012, "name": "Echourouk News", "category_id": "4", "url": STREAM_TS},
    {"stream_id": 4013, "name": "Ennahar TV", "category_id": "4", "url": STREAM_TS},
    {"stream_id": 4014, "name": "El Bilad TV", "category_id": "4", "url": STREAM_TS},
    {"stream_id": 4020, "name": "Bahia TV", "category_id": "4", "url": STREAM_TS},
    {"stream_id": 4022, "name": "El Heddaf TV", "category_id": "4", "url": STREAM_TS},

    # ------ AR | NEWS ------
    {"stream_id": 5003, "name": "Al Arabiya", "category_id": "5", "url": STREAM_NEWS},
    {"stream_id": 5004, "name": "Al Hadath", "category_id": "5", "url": STREAM_NEWS},
    {"stream_id": 5009, "name": "RT Arabic", "category_id": "5", "url": STREAM_TS},
    {"stream_id": 5014, "name": "Al Ikhbariya", "category_id": "5", "url": STREAM_SUNNAH},

    # ------ AR | ISLAMIC ------
    {"stream_id": 6001, "name": "Saudi Quran TV", "category_id": "6", "url": STREAM_QURAN},
    {"stream_id": 6002, "name": "Saudi Sunnah TV", "category_id": "6", "url": STREAM_SUNNAH},

    # ------ BEIN | SPORTS ------
    {"stream_id": 7001, "name": "beIN SPORTS 1", "category_id": "7", "url": STREAM_TS},
    {"stream_id": 7002, "name": "beIN SPORTS 2", "category_id": "7", "url": STREAM_TS},
    {"stream_id": 7010, "name": "beIN SPORTS NEWS", "category_id": "7", "url": STREAM_NEWS},

    # ------ SSC | SPORTS ------
    {"stream_id": 8001, "name": "SSC 1", "category_id": "8", "url": STREAM_QURAN},
    {"stream_id": 8002, "name": "SSC 2", "category_id": "8", "url": STREAM_QURAN},

    # ------ AR | SPORT ------
    {"stream_id": 9001, "name": "Abu Dhabi Sports 1", "category_id": "9", "url": STREAM_TS},
    {"stream_id": 9004, "name": "Dubai Sports 1", "category_id": "9", "url": STREAM_TS},

    # ------ KIDS | INTERNATIONAL ------
    {"stream_id": 10001, "name": "Cartoon Network", "category_id": "10", "url": STREAM_TS},
    {"stream_id": 10007, "name": "Gulli", "category_id": "10", "url": STREAM_TS},

    # ------ DOCUMENTARY | WORLD ------
    {"stream_id": 11003, "name": "National Geographic", "category_id": "11", "url": STREAM_TS},

    # ------ MUSIC | WORLD ------
    {"stream_id": 12001, "name": "MTV", "category_id": "12", "url": STREAM_TS},

    # ------ MOVIES | CHANNELS ------
    {"stream_id": 13001, "name": "MOVIES | CHANNEL 1", "category_id": "13", "url": STREAM_NEWS},
    {"stream_id": 13002, "name": "MOVIES | CHANNEL 2", "category_id": "13", "url": STREAM_NEWS},
    {"stream_id": 13003, "name": "MOVIES | CHANNEL 3", "category_id": "13", "url": STREAM_NEWS}
]

def validate_client(username, password):
    return username in VALID_CREDENTIALS and VALID_CREDENTIALS[username] == password

@app.route('/player_api.php')
def player_api():
    user = request.args.get("username")
    pwd = request.args.get("password")
    
    if not user or not pwd or not validate_client(user, pwd):
        return jsonify({"user_info": {"auth": 0}}), 200

    action = request.args.get("action")
    
    if not action:
        return jsonify({
            "user_info": {
                "username": user,
                "password": pwd,
                "auth": 1,
                "status": "Active",
                "exp_date": 1803744000,
                "is_trial": 0,
                "active_cons": 0,
                "max_connections": 5
            },
            "server_info": {
                "url": request.host,
                "port": 80,
                "https_port": 443,
                "server_time": int(time.time()),
                "timezone": "Africa/Algiers"
            }
        })
        
    elif action == "get_live_categories":
        return jsonify(CATEGORIES)
        
    elif action == "get_live_streams":
        category_id = request.args.get("category_id")
        streams = []
        for ch in CHANNELS_DATA:
            if category_id and ch["category_id"] != category_id: 
                continue
            streams.append({
                "num": int(ch["stream_id"]),
                "name": ch["name"],
                "stream_type": "live",
                "stream_id": int(ch["stream_id"]),
                "stream_icon": "",
                "category_id": ch["category_id"],
                "added": 1611874800
            })
        return jsonify(streams)
        
    return jsonify([])

@app.route('/live/<username>/<password>/<int:stream_id>.ts')
@app.route('/live/<username>/<password>/<int:stream_id>')
def stream_proxy(username, password, stream_id):
    if not validate_client(username, password): 
        return "Unauthorized", 401
        
    target_channel = next((ch for ch in CHANNELS_DATA if ch["stream_id"] == stream_id), None)
    if target_channel:
        base_url = target_channel["url"]
        # توجيه 302 فوري: يرفع الضغط تماماً عن Vercel ويمنع انطفاءه
        separator = "&" if "?" in base_url else "?"
        final_url = f"{base_url}{separator}ts={int(time.time())}"
        return Response(status=302, headers={"Location": final_url})
        
    return "Not Found", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
