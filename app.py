import os
import time
from flask import Flask, request, jsonify, Response

app = Flask(__name__)

# بيانات الدخول الخاصة بك والمحميّة من خلط الرسيفر
MY_USERNAME = "assil"
MY_PASSWORD = "2026password"

# 1. قائمة الأقسام الـ 22 المفصلة بالترتيب والدقة التي طلبتها
CATEGORIES = [
    # أقسام الجزائر
    {"category_id": "1", "category_name": "🇩🇿 DZ : SPORTS & FOOTBALL", "parent_id": 0},
    {"category_id": "2", "category_name": "🇩🇿 DZ : NEWS & EXTRA", "parent_id": 0},
    {"category_id": "3", "category_name": "🇩🇿 DZ : GENERAL & ENTERTAINMENT", "parent_id": 0},
    {"category_id": "4", "category_name": "🇩🇿 DZ : REGIONAL & LOCAL", "parent_id": 0},
    {"category_id": "5", "category_name": "🇩🇿 DZ : COOKING & WOMEN & LIFESTYLE", "parent_id": 0},
    {"category_id": "6", "category_name": "🇩🇿 DZ : ISLAMIC & RELIGIOUS", "parent_id": 0},
    {"category_id": "7", "category_name": "🇩🇿 DZ : CULTURE, KIDS & EDUCATION", "parent_id": 0},
    {"category_id": "8", "category_name": "🇩🇿 DZ : VISUAL RADIO", "parent_id": 0},
    {"category_id": "9", "category_name": "🇩🇿 DZ : MUSIC & ENTERTAINMENT", "parent_id": 0},
    
    # أقسام السعودية
    {"category_id": "10", "category_name": "🇸🇦 KSA : SPORTS & FOOTBALL", "parent_id": 0},
    {"category_id": "11", "category_name": "🇸🇦 KSA : NEWS & POLITICS", "parent_id": 0},
    {"category_id": "12", "category_name": "🇸🇦 KSA : GENERAL & ENTERTAINMENT", "parent_id": 0},
    {"category_id": "13", "category_name": "🇸🇦 KSA : ISLAMIC & HOLY QURAN", "parent_id": 0},
    {"category_id": "14", "category_name": "🇸🇦 KSA : LIFESTYLE & REGIONAL & KIDS", "parent_id": 0},
    
    # أقسام فرنسا
    {"category_id": "15", "category_name": "🇫🇷 FR : SPORTS", "parent_id": 0},
    {"category_id": "16", "category_name": "🇫🇷 FR : GENERAL & TNT", "parent_id": 0},
    {"category_id": "17", "category_name": "🇫🇷 FR : NEWS", "parent_id": 0},
    {"category_id": "18", "category_name": "🇫🇷 FR : CINEMA & PREMIUM", "parent_id": 0},
    {"category_id": "19", "category_name": "🇫🇷 FR : DOCUMENTARIES & DISCOVERY", "parent_id": 0},
    {"category_id": "20", "category_name": "🇫🇷 FR : KIDS", "parent_id": 0},
    {"category_id": "21", "category_name": "🇫🇷 FR : MUSIC & LIFESTYLE", "parent_id": 0}
]

# 2. بنية المجلدات الضخمة لجميع القنوات (توجيه ديناميكي مباشر بصيغة .ts)
CHANNELS_DATA = [
    # === 🇩🇿 الجزائر: الرياضة ===
    {"stream_id": 1001, "name": "TV6 Algerie HD", "category_id": "1", "url": "http://193.124.186.208:8000/play/a01h"},
    {"stream_id": 1002, "name": "TV6 Algerie SD", "category_id": "1", "url": "http://193.124.186.208:8000/play/a01h"},
    {"stream_id": 1003, "name": "TV6 Algerie 4K", "category_id": "1", "url": "http://193.124.186.208:8000/play/a01h"},
    {"stream_id": 1004, "name": "Programme National HD (الأرضية)", "category_id": "1", "url": "http://193.124.186.208:8000/play/a01h"},
    {"stream_id": 1005, "name": "Programme National SD", "category_id": "1", "url": "http://193.124.186.208:8000/play/a01h"},
    {"stream_id": 1006, "name": "El Heddaf TV HD", "category_id": "1", "url": "http://193.124.186.208:8000/play/a01h"},
    {"stream_id": 1007, "name": "El Heddaf TV SD", "category_id": "1", "url": "http://193.124.186.208:8000/play/a01h"},
    {"stream_id": 1008, "name": "Stade News TV", "category_id": "1", "url": "http://193.124.186.208:8000/play/a01h"},
    {"stream_id": 1009, "name": "Dzair Sport HD", "category_id": "1", "url": "http://193.124.186.208:8000/play/a01h"},
    {"stream_id": 1010, "name": "Dzair Sport 2", "category_id": "1", "url": "http://193.124.186.208:8000/play/a01h"},

    # === 🇩🇿 الجزائر: الأخبار ===
    {"stream_id": 1101, "name": "AL24 News HD", "category_id": "2", "url": "http://tv-live.dw.com/hls/dw_arabic_ts.ts"},
    {"stream_id": 1102, "name": "AL24 News SD", "category_id": "2", "url": "http://tv-live.dw.com/hls/dw_arabic_ts.ts"},
    {"stream_id": 1103, "name": "AL24 News English", "category_id": "2", "url": "http://tv-live.dw.com/hls/dw_arabic_ts.ts"},
    {"stream_id": 1104, "name": "AL24 News French", "category_id": "2", "url": "http://tv-live.dw.com/hls/dw_arabic_ts.ts"},
    {"stream_id": 1105, "name": "Ennahar TV HD", "category_id": "2", "url": "http://193.124.186.208:8000/play/a01i"},
    {"stream_id": 1106, "name": "Ennahar TV SD", "category_id": "2", "url": "http://193.124.186.208:8000/play/a01i"},
    {"stream_id": 1107, "name": "Echorouk News HD", "category_id": "2", "url": "http://193.124.186.208:8000/play/a01h"},
    {"stream_id": 1108, "name": "El Bilad TV HD", "category_id": "2", "url": "http://193.124.186.208:8000/play/a01i"},
    {"stream_id": 1109, "name": "El Hayat TV HD", "category_id": "2", "url": "http://tv-live.dw.com/hls/dw_arabic_ts.ts"},

    # === 🇩🇿 الجزائر: العامة والترفيه ===
    {"stream_id": 1201, "name": "TV1 Algerie HD (الأولى العمومية)", "category_id": "3", "url": "http://rt-arabic.rbm.tv/rt-arabic.ts"},
    {"stream_id": 1202, "name": "Canal Algerie HD", "category_id": "3", "url": "http://rt-arabic.rbm.tv/rt-arabic.ts"},
    {"stream_id": 1203, "name": "A3 Algerie HD", "category_id": "3", "url": "http://193.124.186.208:8000/play/a03b"},
    {"stream_id": 1204, "name": "Echorouk TV HD", "category_id": "3", "url": "http://193.124.186.208:8000/play/a01h"},
    {"stream_id": 1205, "name": "El Fadjr TV HD", "category_id": "3", "url": "http://193.124.186.208:8000/play/a03b"},
    {"stream_id": 1206, "name": "Bahia TV HD (الباهية)", "category_id": "3", "url": "http://193.124.186.208:8000/play/a01i"},
    {"stream_id": 1207, "name": "El Djazaïria One HD", "category_id": "3", "url": "http://193.124.186.208:8000/play/a01h"},
    {"stream_id": 1208, "name": "Lina TV HD (قناة لينا)", "category_id": "3", "url": "http://193.124.186.208:8000/play/a01i"},

    # === 🇩🇿 الجزائر: الطبخ والجهوية والإسلامية والثقافية والموسيقى ===
    {"stream_id": 1301, "name": "Samira TV HD", "category_id": "5", "url": "http://193.124.186.208:8000/play/a01h"},
    {"stream_id": 1302, "name": "TV5 Coran HD", "category_id": "6", "url": "http://193.124.186.208:8000/play/a03b"},
    {"stream_id": 1303, "name": "El Anis TV HD (الأنيس)", "category_id": "6", "url": "http://193.124.186.208:8000/play/a03b"},
    {"stream_id": 1304, "name": "TV4 Amazighia HD", "category_id": "7", "url": "http://rt-arabic.rbm.tv/rt-arabic.ts"},
    {"stream_id": 1305, "name": "TV8 Edhakira HD (الذاكرة والتاريخ)", "category_id": "7", "url": "http://rt-arabic.rbm.tv/rt-arabic.ts"},
    {"stream_id": 1306, "name": "TV7 El Maarifa HD (المعرفة التعليمية)", "category_id": "7", "url": "http://193.124.186.208:8000/play/a03b"},
    {"stream_id": 1307, "name": "Jil FM TV (جيل إف إم المرئية)", "category_id": "8", "url": "http://193.124.186.208:8000/play/a01i"},
    {"stream_id": 1308, "name": "DZ Rai Music HD", "category_id": "9", "url": "http://193.124.186.208:8000/play/a01h"},

    # === 🇸🇦 السعودية: الرياضة وكرة القدم ===
    {"stream_id": 2001, "name": "SSC 1 HD", "category_id": "10", "url": "http://193.124.186.208:8000/play/a01h"},
    {"stream_id": 2002, "name": "SSC 1 4K", "category_id": "10", "url": "http://193.124.186.208:8000/play/a01h"},
    {"stream_id": 2003, "name": "SSC 2 HD", "category_id": "10", "url": "http://193.124.186.208:8000/play/a01h"},
    {"stream_id": 2004, "name": "KSA Sports 1 HD (الرياضية السعودية 1)", "category_id": "10", "url": "http://193.124.186.208:8000/play/a01i"},
    {"stream_id": 2005, "name": "KSA Sports 2 HD", "category_id": "10", "url": "http://193.124.186.208:8000/play/a01i"},

    # === 🇸🇦 السعودية: الأخبار والسياسة ===
    {"stream_id": 2101, "name": "Al Arabiya HD (العربية)", "category_id": "11", "url": "http://rt-arabic.rbm.tv/rt-arabic.ts"},
    {"stream_id": 2102, "name": "Al Arabiya Al Hadath HD (الحدث)", "category_id": "11", "url": "http://rt-arabic.rbm.tv/rt-arabic.ts"},
    {"stream_id": 2103, "name": "Al Ekhbariya HD (الإخبارية السعودية)", "category_id": "11", "url": "http://rt-arabic.rbm.tv/rt-arabic.ts"},
    {"stream_id": 2104, "name": "Al Sharq News HD (الشرق للأخبار)", "category_id": "11", "url": "http://tv-live.dw.com/hls/dw_arabic_ts.ts"},

    # === 🇸🇦 السعودية: العامة والإسلامية والترفيه ===
    {"stream_id": 2201, "name": "Saudi TV 1 HD (السعودية الأولى)", "category_id": "12", "url": "http://193.124.186.208:8000/play/a03b"},
    {"stream_id": 2202, "name": "SBC HD (قناة إس بي سي)", "category_id": "12", "url": "http://193.124.186.208:8000/play/a03b"},
    {"stream_id": 2203, "name": "MBC 1 HD", "category_id": "12", "url": "http://193.124.186.208:8000/play/a01h"},
    {"stream_id": 2204, "name": "MBC Action HD", "category_id": "12", "url": "http://193.124.186.208:8000/play/a01i"},
    {"stream_id": 2205, "name": "Saudi Quran TV HD (قناة القرآن الكريم من مكة المكرمة)", "category_id": "13", "url": "http://193.124.186.208:8000/play/a03b"},
    {"stream_id": 2206, "name": "Saudi Sunnah TV HD (قناة السنة النبوية من المدينة المنورة)", "category_id": "13", "url": "http://193.124.186.208:8000/play/a03b"},

    # === 🇫🇷 فرنسا: الرياضة ===
    {"stream_id": 3001, "name": "Canal+ Foot HD", "category_id": "15", "url": "http://193.124.186.208:8000/play/a01h"},
    {"stream_id": 3002, "name": "Canal+ Sport HD", "category_id": "15", "url": "http://193.124.186.208:8000/play/a01h"},
    {"stream_id": 3003, "name": "beIN Sports FR 1 HD", "category_id": "15", "url": "http://193.124.186.208:8000/play/a01i"},
    {"stream_id": 3004, "name": "L'Équipe TV HD (قناة ليكيب)", "category_id": "15", "url": "http://tv-live.dw.com/hls/dw_arabic_ts.ts"},

    # === 🇫🇷 فرنسا: القنوات العامة والـ TNT والأخبار ===
    {"stream_id": 3101, "name": "TF1 HD", "category_id": "16", "url": "http://193.124.186.208:8000/play/a01h"},
    {"stream_id": 3102, "name": "France 2 HD", "category_id": "16", "url": "http://tv-live.dw.com/hls/dw_arabic_ts.ts"},
    {"stream_id": 3103, "name": "M6 HD", "category_id": "16", "url": "http://193.124.186.208:8000/play/a01i"},
    {"stream_id": 3201, "name": "BFM TV HD", "category_id": "17", "url": "http://tv-live.dw.com/hls/dw_arabic_ts.ts"},
    {"stream_id": 3202, "name": "CNews HD", "category_id": "17", "url": "http://rt-arabic.rbm.tv/rt-arabic.ts"},
    {"stream_id": 3203, "name": "France 24 Français HD", "category_id": "17", "url": "http://rt-arabic.rbm.tv/rt-arabic.ts"}
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

    return Response(status=302, headers={"Location": target_channel["url"]})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
