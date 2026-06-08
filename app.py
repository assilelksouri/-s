import os
import time
import re
from flask import Flask, request, jsonify, Response
import requests

app = Flask(__name__)

# --- إعدادات الحماية للسيرفر الخاص بك ---
MY_USERNAME = "assil"
MY_PASSWORD = "2026password"

# --- الأقسام الثابتة للرسيفر ---
CATEGORIES = [
    {"category_id": "1", "category_name": "⚽ ASSIL SPORTS", "parent_id": 0},
    {"category_id": "2", "category_name": "📰 ASSIL NEWS", "parent_id": 0},
    {"category_id": "3", "category_name": "📺 ASSIL GENERAL", "parent_id": 0}
]

# خريطة القنوات الثابتة في جهازك، وسيقوم الكود بالبحث عنها بالاسم في السيرفرات العامة
CHANNELS_DATA = [
    {"stream_id": 101, "name": "BEIN SPORTS 1", "category_id": "1", "search_keyword": "beIN SPORTS 1", "logo": "https://upload.wikimedia.org/wikipedia/commons/c/c5/BeIN_Sports_Logo.svg"},
    {"stream_id": 102, "name": "BEIN SPORTS 2", "category_id": "1", "search_keyword": "beIN SPORTS 2", "logo": "https://upload.wikimedia.org/wikipedia/commons/c/c5/BeIN_Sports_Logo.svg"},
    {"stream_id": 103, "name": "SSC SPORTS 1", "category_id": "1", "search_keyword": "SSC SPORT 1", "logo": "https://images.squarespace-cdn.com/content/v1/5cf3ca043d8b2d000100f918/1630138927063-SDFV3IP99Y9DR8W0PDU4/SSC+Logo.png"},
    
    {"stream_id": 201, "name": "AL JAZEERA ARABIC", "category_id": "2", "search_keyword": "Al Jazeera", "logo": "https://upload.wikimedia.org/wikipedia/commons/7/70/Al_Jazeera_English_2011.svg"},
    {"stream_id": 202, "name": "AL ARABIYA", "category_id": "2", "search_keyword": "Al Arabiya", "logo": "https://upload.wikimedia.org/wikipedia/commons/8/82/Al_Arabiya_Logo.svg"},
    
    {"stream_id": 301, "name": "ALGERIE 1", "category_id": "3", "search_keyword": "Algérie", "logo": "https://upload.wikimedia.org/wikipedia/commons/d/df/EPTV_logo.png"},
    {"stream_id": 303, "name": "FRANCE 2 HD", "category_id": "3", "search_keyword": "France 2", "logo": "https://upload.wikimedia.org/wikipedia/commons/0/02/France_2_logo_2018.svg"}
]

# مخزن مؤقت لحفظ السيرفر الشغال لتقليل الضغط وتخطي قيود Vercel
CACHED_SOURCE = {"url": "", "username": "", "password": "", "timestamp": 0}

def get_active_server():
    """ جلب سيرفر كستريم فعال تلقائياً من روابط IPTV محدثة ومفتوحة """
    global CACHED_SOURCE
    # إذا كان هناك سيرفر تم جلبه منذ أقل من 15 دقيقة، نستخدمه فوراً لتوفير الوقت
    if CACHED_SOURCE["url"] and (time.time() - CACHED_SOURCE["timestamp"] < 900):
        return CACHED_SOURCE

    # مصادر عامة ومحدثة يومياً تحتوي على قوائم وسيرفرات اكستريم حية
    sources = [
        "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/ar.m3u",
        "https://raw.githubusercontent.com/mohammad94p/m3u/main/Free.m3u"
    ]
    
    for url in sources:
        try:
            res = requests.get(url, timeout=5)
            if res.status_code == 200:
                # نمط ذكي للبحث عن بيانات سيرفرات Xtream المخبأة في الروابط العامة
                pattern = r'(https?://[^/:\s]+:\d+)/get\.php\?username=([^&\s]+)&password=([^&\s]+)'
                matches = re.findall(pattern, res.text)
                for match in matches:
                    srv = {"url": match[0], "username": match[1], "password": match[2]}
                    # فحص سريع إذا كان السيرفر يقبل الاتصال ونشط
                    test_url = f"{srv['url']}/player_api.php?username={srv['username']}&password={srv['password']}"
                    try:
                        test_res = requests.get(test_url, timeout=3)
                        if test_res.status_code == 200 and "user_info" in test_res.json():
                            CACHED_SOURCE = {**srv, "timestamp": time.time()}
                            return CACHED_SOURCE
                    except:
                        continue
        except:
            continue
            
    # سيرفر احتياطي ثابت في حال فشل البوت التلقائي لكي لا يعطي الرسيفر خطأ
    return {"url": "http://public-iptv-example.com:8080", "username": "demo", "password": "demo"}

def validate_client():
    return request.args.get("username") == MY_USERNAME and request.args.get("password") == MY_PASSWORD

@app.route('/player_api.php')
def player_api():
    if not validate_client():
        return jsonify({"user_info": {"auth": 0, "status": "Not Authorized"}}), 403

    action = request.args.get("action")

    if not action:
        return jsonify({
            "user_info": {
                "username": MY_USERNAME, "password": MY_PASSWORD, "auth": 1,
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
                "stream_id": ch["stream_id"], "stream_icon": ch["logo"],
                "category_id": ch["category_id"], "added": "1611874800"
            })
        return jsonify(xtream_channels)

    return jsonify([])

@app.route('/live/<username>/<password>/<int:stream_id>.ts')
@app.route('/live/<username>/<password>/<int:stream_id>')
def stream_proxy(username, password, stream_id):
    if username != MY_USERNAME or password != MY_PASSWORD:
        return "Unauthorized", 403

    target_channel = next((ch for ch in CHANNELS_DATA if ch["stream_id"] == stream_id), None)
    if not target_channel:
        return "Channel Not Found", 404

    # استدعاء السيرفر المصدر الفعال حالياً من البوت الذكي
    src = get_active_server()
    
    # خطوة الربط الذكي: نبحث أولاً عن الـ ID الحقيقي للقناة داخل السيرفر المصدر بالاسم
    remote_stream_id = stream_id # افتراضي
    try:
        search_url = f"{src['url']}/player_api.php?username={src['username']}&password={src['password']}&action=get_live_streams"
        all_streams = requests.get(search_url, timeout=4).json()
        for s in all_streams:
            if target_channel["search_keyword"].lower() in s.get("name", "").lower():
                remote_stream_id = s.get("stream_id", stream_id)
                break
    except:
        pass

    # بناء رابط البث الحقيقي الموجه للسيرفر الفعال المكتشف
    actual_stream_url = f"{src['url']}/live/{src['username']}/{src['password']}/{remote_stream_id}.ts"
    
    # ميزة الـ Redirect الفوري لتسريع فتح القناة على الرسيفر وتجنب تعليق Vercel
    return Response(status=302, headers={"Location": actual_stream_url})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)