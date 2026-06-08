import os
import time
from flask import Flask, request, jsonify, Response

app = Flask(__name__)
handler = app

# بيانات الدخول (جرب استخدام حساب admin لتجنب أي مشاكل كاش قديمة بالرسيفر)
VALID_CREDENTIALS = {"assil": "123", "admin": "admin"}

CATEGORIES = [
    {"category_id": "1", "category_name": "🇩🇿 DZ : SPORTS & FOOTBALL", "parent_id": 0},
    {"category_id": "2", "category_name": "🇩🇿 DZ : NEWS & EXTRA", "parent_id": 0},
    {"category_id": "3", "category_name": "🇩🇿 DZ : GENERAL & ENTERTAINMENT", "parent_id": 0},
    {"category_id": "4", "category_name": "🇸🇦 KSA : SPORTS", "parent_id": 0},
    {"category_id": "5", "category_name": "🇸🇦 KSA : NEWS", "parent_id": 0},
    {"category_id": "6", "category_name": "🇸🇦 KSA : GENERAL & ENTERTAINMENT", "parent_id": 0},
    {"category_id": "7", "category_name": "🇫🇷 FR : SPORTS", "parent_id": 0},
    {"category_id": "8", "category_name": "🇫🇷 FR : NEWS", "parent_id": 0},
    {"category_id": "9", "category_name": "🇫🇷 FR : GENERAL & ENTERTAINMENT", "parent_id": 0}
]

TS_STREAM = "http://rt-arabic.rbm.tv/rt-arabic.ts"
KSA_QURAN = "https://win.holol.com/live/quran/playlist.m3u8"
KSA_SUNNAH = "https://win.holol.com/live/sunnah/playlist.m3u8"
ALARABIYA = "https://live.alarabiya.net/alarabiya/alarabiya.m3u8"

CHANNELS_DATA = [
    # الجزائر
    {"stream_id": 101, "name": "TV6 Algerie HD", "category_id": "1", "url": TS_STREAM},
    {"stream_id": 104, "name": "Programme National HD", "category_id": "1", "url": TS_STREAM},
    {"stream_id": 106, "name": "El Heddaf TV HD", "category_id": "1", "url": TS_STREAM},
    {"stream_id": 131, "name": "AL24 News HD", "category_id": "2", "url": TS_STREAM},
    {"stream_id": 136, "name": "Ennahar TV HD", "category_id": "2", "url": TS_STREAM},
    {"stream_id": 139, "name": "Echorouk News HD", "category_id": "2", "url": TS_STREAM},
    {"stream_id": 181, "name": "TV1 Algerie HD", "category_id": "3", "url": TS_STREAM},
    {"stream_id": 187, "name": "Echorouk TV HD", "category_id": "3", "url": TS_STREAM},
    {"stream_id": 190, "name": "El Fadjr TV HD", "category_id": "3", "url": TS_STREAM},
    # السعودية
    {"stream_id": 401, "name": "SSC 1 HD", "category_id": "4", "url": KSA_QURAN},
    {"stream_id": 413, "name": "KSA Sports 1 HD", "category_id": "4", "url": KSA_SUNNAH},
    {"stream_id": 501, "name": "Al Arabiya HD", "category_id": "5", "url": ALARABIYA},
    {"stream_id": 506, "name": "Al Ekhbariya HD", "category_id": "5", "url": KSA_SUNNAH},
    {"stream_id": 601, "name": "Saudi TV 1 HD", "category_id": "6", "url": KSA_QURAN},
    {"stream_id": 605, "name": "MBC 1 HD", "category_id": "6", "url": ALARABIYA},
    # فرنسا
    {"stream_id": 701, "name": "Canal+ Foot HD", "category_id": "7", "url": TS_STREAM},
    {"stream_id": 706, "name": "beIN Sports FR 1 HD", "category_id": "7", "url": TS_STREAM},
    {"stream_id": 801, "name": "BFM TV HD", "category_id": "8", "url": TS_STREAM},
    {"stream_id": 811, "name": "France 24 Français HD", "category_id": "8", "url": ALARABIYA},
    {"stream_id": 901, "name": "TF1 HD", "category_id": "9", "url": TS_STREAM},
    {"stream_id": 917, "name": "M6 HD", "category_id": "9", "url": TS_STREAM}
]

def validate_client(username, password):
    return username in VALID_CREDENTIALS and VALID_CREDENTIALS[username] == password

@app.route('/player_api.php')
def player_api():
    user = request.args.get("username")
    pwd = request.args.get("password")
    
    if not user or not pwd or not validate_client(user, pwd):
        return jsonify({"user_info": {"auth": 0}}), 200  # إرجاع 200 بدلاً من 403 لأن بعض الرسيفرات تعتبر 403 خطأ شبكة

    action = request.args.get("action")
    
    # الطلب الأول: التحقق من الحساب والدخول
    if not action:
        response_data = {
            "user_info": {
                "username": user,
                "password": pwd,
                "auth": 1,
                "status": "Active",
                "exp_date": "1803744000",  # تاريخ بعيد جداً سنة 2027
                "is_trial": "0",
                "active_cons": "0",
                "max_connections": "5"
            },
            "server_info": {
                "url": request.host,
                "port": "80",
                "https_port": "443",
                "server_time": str(int(time.time())),
                "timezone": "Africa/Algiers"
            }
        }
        return jsonify(response_data)
        
    # الطلب الثاني: جلب الأقسام
    elif action == "get_live_categories":
        return jsonify(CATEGORIES)
        
    # الطلب الثالث: جلب القنوات
    elif action == "get_live_streams":
        category_id = request.args.get("category_id")
        streams = []
        for ch in CHANNELS_DATA:
            if category_id and ch["category_id"] != category_id: 
                continue
            streams.append({
                "num": ch["stream_id"],
                "name": ch["name"],
                "stream_type": "live",
                "stream_id": ch["stream_id"],
                "stream_icon": "",
                "category_id": ch["category_id"],
                "added": "1611874800"
            })
        return jsonify(streams)
        
    return jsonify([])

# مسار تشغيل البث المباشر
@app.route('/live/<username>/<password>/<int:stream_id>.ts')
@app.route('/live/<username>/<password>/<int:stream_id>')
def stream_proxy(username, password, stream_id):
    if not validate_client(username, password): 
        return "Unauthorized", 401
        
    target_channel = next((ch for ch in CHANNELS_DATA if ch["stream_id"] == stream_id), None)
    if target_channel:
        base_url = target_channel["url"]
        # كسر الكاش لضمان عدم تكرار القناة عند التنقل
        separator = "&" if "?" in base_url else "?"
        final_url = f"{base_url}{separator}ts={int(time.time())}"
        return Response(status=302, headers={"Location": final_url})
        
    return "Not Found", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
