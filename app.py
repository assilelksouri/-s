import os
import time
from flask import Flask, request, jsonify, Response

app = Flask(__name__)

VALID_CREDENTIALS = {"assil": "123", "admin": "admin"}

# الروابط الرسمية المستقرة للبث مجاناً
STREAM_LINKS = {
    "dz_sport": "https://live.al24news.com/al24news/index.m3u8",
    "dz_news": "https://live.al24news.com/al24news/index.m3u8",
    "dz_general": "https://live.al24news.com/al24news/index.m3u8",
    "ksa_news": "https://live.alarabiya.net/alarabiya/alarabiya.m3u8",
    "ksa_quran": "https://win.holol.com/live/quran/playlist.m3u8"
}

# توليد التصنيفات التي طلبتها بالضبط برمجياً لتقليل حجم الملف
CATEGORIES_NAMES = [
    "🇩🇿 DZ : SPORTS & FOOTBALL", "🇩🇿 DZ : NEWS & EXTRA", "🇩🇿 DZ : GENERAL & ENTERTAINMENT",
    "🇩🇿 DZ : REGIONAL & LOCAL", "🇩🇿 DZ : COOKING & WOMEN & LIFESTYLE", "🇩🇿 DZ : ISLAMIC & RELIGIOUS",
    "🇩🇿 DZ : CULTURE, KIDS & EDUCATION", "🇩🇿 DZ : VISUAL RADIO", "🇩🇿 DZ : MUSIC & ENTERTAINMENT",
    "🇸🇦 KSA : SPORTS & FOOTBALL", "🇸🇦 KSA : NEWS & POLITICS", "🇸🇦 KSA : GENERAL & ENTERTAINMENT",
    "🇸🇦 KSA : ISLAMIC & HOLY QURAN", "🇸🇦 KSA : LIFESTYLE & REGIONAL & KIDS",
    "🇫🇷 FR : SPORTS", "🇫🇷 FR : GENERAL & TNT", "🇫🇷 FR : NEWS", "🇫🇷 FR : CINEMA & PREMIUM",
    "🇫🇷 FR : DOCUMENTARIES & DISCOVERY", "🇫🇷 FR : KIDS", "🇫🇷 FR : MUSIC & LIFESTYLE"
]
CATEGORIES = [{"category_id": str(i+1), "category_name": name, "parent_id": 0} for i, name in enumerate(CATEGORIES_NAMES)]

# توليد القنوات التي طلبتها حرفياً وبسرعة فائقة
RAW_CHANNELS = {
    "1": ["TV6 Algerie HD", "TV6 Algerie SD", "TV6 Algerie 4K", "Programme National HD (الأرضية)", "Programme National SD", "El Heddaf TV HD", "El Heddaf TV SD", "Stade News TV", "Dzair Sport HD", "Dzair Sport 2", "El Adjwaa Sport", "JSK TV", "MCA TV", "USMA TV", "CRB TV", "ESS TV", "CSC TV", "MCO TV", "Setif Sport TV", "Algeria Sports Live 1", "Algeria Sports Live 2", "Kooora DZ TV"],
    "2": ["AL24 News HD", "AL24 News SD", "AL24 News English", "AL24 News French", "AL24 News Spanish", "Ennahar TV HD", "Ennahar TV SD", "Ennahar +", "Echorouk News HD", "Echorouk News SD", "Echorouk News 4K", "El Bilad TV HD", "El Bilad TV SD", "El Bilad +", "El Hayat TV HD", "El Hayat TV SD", "El Adjwaa TV HD", "El Adjwaa TV SD", "Numidia News HD", "Numidia TV", "Dzair News", "KBC News", "Hoggar News", "Lindex News", "Kawaliss News", "Algeria 24/7", "DZ News Live", "Al Magharibia HD", "Al Magharibia SD", "Al Magharibia 2", "Rachad TV", "Amel TV", "Free Algeria TV", "Sawt Al Djazair", "El Hiwar DZ", "El Badil TV"],
    "3": ["TV1 Algerie HD", "TV1 Algerie SD", "Canal Algerie HD", "Canal Algerie SD", "A3 Algerie HD", "A3 Algerie SD", "Echorouk TV HD", "Echorouk TV SD", "Echorouk +", "El Fadjr TV HD", "El Fadjr TV SD", "El Fadjr TV 2", "Bahia TV HD", "Bahia TV SD", "El Djazaïria One HD", "El Djazaïria One SD", "Beur TV HD", "Beur TV SD", "Hoggar TV", "Lindex TV", "Kawaliss TV", "Dzair TV", "Lina TV HD", "Wiam TV", "DTV Algerie HD", "DTV Anime", "DTV Movies", "Atlas TV", "El Adjwaa Drama", "El Adjwaa Cinema", "Ennahar Laki", "Al Asr TV", "El Rihab TV", "Al Makam TV", "GO TV Algeria", "El Djazaïr TV", "Seybouse TV", "Numidia Drama", "El Fadjr Cinema", "El Fadjr Drama", "Bahia Drama", "Jil TV", "Master TV Algeria", "Flame TV Algeria", "One TV Algeria", "Sweet TV DZ"],
    "4": ["TV Constantine", "TV Oran", "TV Ouargla", "TV Bechar", "TV Tlemcen", "TV Annaba", "Edough TV", "Cirta TV", "Djurdjura TV", "Hoggar Local", "Bahia TV Oran", "Soummam TV", "Aurès TV", "Hodna TV", "Tassili TV", "Sahara TV Algeria", "Medea TV", "Blida TV Local", "Setif TV Regional"],
    "5": ["Samira TV HD", "Samira TV SD", "Samira TV Kitchen", "Samira TV Extra", "CBC Benna", "Ennahar Cuisine", "Echorouk Cuisine", "El Fadjr Cuisine", "Bahia Cuisine", "Lalla TV", "Kiuki TV Algeria", "Madame DZ TV"],
    "6": ["TV5 Coran HD", "TV5 Coran SD", "El Anis TV HD", "El Anis TV SD", "Ennahar Anamil", "El Bilad Holy Quran", "Echorouk Holy Quran", "Al Huda DZ", "Zad DZ TV", "Sunnah DZ TV", "El Fadjr Holy Quran", "Ayat Algeria"],
    "7": ["TV4 Amazighia HD", "TV4 Amazighia SD", "TV8 Edhakira HD", "TV8 Edhakira SD", "TV7 El Maarifa HD", "TV7 El Maarifa SD", "Berbere TV", "Berbere Jeunesse", "Berbere Musique", "Berbere Radio TV", "Educa TV", "Echorouk Kids", "Ennahar Kids", "El Fadjr Kids", "DTV Kids", "Algeria School 1", "Algeria School 2", "Algeria School 3", "Thaqafia TV"],
    "8": ["Chain 1 Radio", "Chain 2 Radio", "Chain 3 Radio", "Radio Algerie Internationale", "Jil FM TV", "Radio El Bahid Oran", "Radio Cirta Constantine", "Radio Mitidja", "Radio Saoura", "Radio Oasis"],
    "9": ["DZ Rai Music HD", "DZ Chaabi Music", "DZ Kabyle Music", "Algeria Music Hits", "Rai Top TV", "El Ghafra TV", "Djazaïrna TV", "Jil Music TV"],
    "10": ["SSC 1 HD", "SSC 1 SD", "SSC 1 4K", "SSC 2 HD", "SSC 2 SD", "SSC 3 HD", "SSC 4 HD", "SSC 5 HD", "SSC EXTRA 1 HD", "SSC EXTRA 2 HD", "SSC EXTRA 3 HD", "Al Kass Saudi 1 HD", "KSA Sports 1 HD", "KSA Sports 1 SD", "KSA Sports 2 HD", "KSA Sports 3 HD", "Al Nassr TV", "Al Hilal TV", "Al Ittihad TV", "Al Ahli TV", "Saudi Sport Live 1", "Saudi Sport Live 2", "Dawri Plus HD", "Riyadh Sport TV"],
    "11": ["Al Arabiya HD", "Al Arabiya SD", "Al Arabiya 4K", "Al Arabiya Al Hadath HD", "Al Arabiya Al Hadath SD", "Al Ekhbariya HD", "Al Ekhbariya SD", "Saudi 24 News", "Al Sharq News HD", "Al Sharq News 4K", "Al Sharq Business", "Asharq Discovery HD", "Saudia 24 Direct", "KSA Politics Live"],
    "12": ["Saudi TV 1 HD", "Saudi TV 1 SD", "SBC HD", "SBC SD", "MBC 1 HD", "MBC 1 SD", "MBC 1 4K", "MBC 2 HD", "MBC 3 HD", "MBC 4 HD", "MBC Action HD", "MBC Max HD", "MBC Drama HD", "MBC Drama +", "MBC Bollywood HD", "MBC Masr HD", "MBC Masr 2 HD", "MBC Iraq HD", "MBC Maghreb HD", "Wanasah TV HD", "Al Danah TV", "Al Sahan TV", "Al Merqab TV", "Bedaya TV", "Al Waha TV", "Diwan Jeddah TV", "Shada TV", "Saudia 24 General", "Al Shamil TV", "KSA One", "Thaqafia TV HD"],
    "13": ["Saudi Quran TV HD", "Saudi Quran TV SD", "Saudi Quran TV 4K", "Saudi Sunnah TV HD", "Saudi Sunnah TV SD", "Saudi Sunnah TV 4K", "Al Majd Holy Quran", "Al Majd Hadith", "Al Majd Prophet Biography", "Al Majd Al Ilmiya", "Al Majd General", "Al Majd Kids", "Al Majd Basma", "Al Majd Rawdah", "Al Majd Massah", "Al Majd Documentaries", "Al Majd Natural", "Al Majd News", "Ayat KSA TV", "Al Insan KSA", "Risalah TV"],
    "14": ["SBC Cuisine", "Sayidaty TV", "Rotana Khalijia HD", "Rotana Cinema KSA HD", "Al Riyadh Local TV", "Makkah Region TV", "Madinah Region TV", "Eastern Province TV", "MBC 3 Kids HD", "Spacetoon KSA"],
    "15": ["Canal+ Foot HD", "Canal+ Foot 4K", "Canal+ Sport HD", "Canal+ Sport 4K", "Canal+ Sport 360 HD", "beIN Sports FR 1 HD", "beIN Sports FR 1 4K", "beIN Sports FR 2 HD", "beIN Sports FR 3 HD", "beIN Sports FR MAX 4 HD", "beIN Sports FR MAX 5 HD", "beIN Sports FR MAX 6 HD", "beIN Sports FR MAX 7 HD", "beIN Sports FR MAX 8 HD", "beIN Sports FR MAX 9 HD", "beIN Sports FR MAX 10 HD", "Eurosport 1 France HD", "Eurosport 2 France HD", "Eurosport 4K France", "RMC Sport 1 HD", "RMC Sport Live 2", "RMC Sport Live 3", "RMC Sport Live 4", "L'Équipe TV HD", "L'Équipe TV SD", "Automoto TV HD", "Golf Channel France HD", "Equidia HD", "OL Play", "OM Play", "PSG TV"],
    "16": ["TF1 HD", "TF1 SD", "TF1 4K", "TF1 Séries Films HD", "France 2 HD", "France 2 SD", "France 2 4K", "France 3 National HD", "France 4 HD", "France 5 HD", "M6 HD", "M6 SD", "M6 4K", "Arte France HD", "Arte France 4K", "C8 France HD", "W9 HD", "TMC France HD", "TFX HD", "NRJ 12 HD", "Gulli HD", "Culturebox HD", "TF1 +", "M6 +"],
    "17": ["BFM TV HD", "BFM TV 4K", "BFM Business", "BFM Paris Île-de-France", "BFM Lyon", "BFM Grand Lille", "BFM Marseille Provence", "CNews HD", "LCI HD", "France Info TV HD", "France 24 Français HD", "France 24 Français SD", "Euronews Français HD", "Public Sénat HD", "LCP HD"],
    "18": ["Canal+ France HD", "Canal+ France 4K", "Canal+ Cinéma(s) HD", "Canal+ Grand Écran HD", "Canal+ Box Office HD", "Canal+ Box Office 4K", "Canal+ Séries HD", "Canal+ Docs HD", "Canal+ Kids HD", "Ciné+ Premier HD", "Ciné+ Frisson HD", "Ciné+ Émotion HD", "Ciné+ Famiz HD", "Ciné+ Club HD", "Ciné+ Classic HD", "OCS Max HD", "OCS Pulp HD", "OCS Géants HD", "Warner TV France HD", "Altice Studio HD", "Paramount Channel France HD", "Paramount Channel Décalé HD", "Action TV France HD", "TCM Cinéma France HD", "Polar+ HD", "Novelas TV France HD", "Serieclub HD", "TV Breizh HD"],
    "19": ["National Geographic France HD", "National Geographic Wild France HD", "Discovery Channel France HD", "Discovery Science France HD", "Planète+ France HD", "Planète+ Crime+Investigation HD", "Planète+ Aventure+Expérience HD", "Voyage TV", "Ushuaïa TV HD", "Histoire TV HD", "Toute l'Histoire HD", "Science & Vie TV HD", "Animaux TV HD", "Chasse & Pêche HD", "Trek TV France"],
    "20": ["Disney Channel France HD", "Disney Channel +1 France HD", "Disney Junior France HD", "Nickelodeon France HD", "Nickelodeon Junior France HD", "Nickelodeon Teen France HD", "Cartoon Network France HD", "Cartoonito France HD", "Boomerang France HD", "Boomerang +1 France HD", "Canal J HD", "TiJi HD", "Piwi+ HD", "Teletoon+ HD", "Teletoon+ 1 HD"],
    "21": ["NRJ Hits HD", "MTV France HD", "MTV Hits France HD", "MCM France HD", "MCM Top HD", "M6 Music HD", "RFM TV HD", "Melody TV HD", "Trace Urban France HD", "Trace Latina France HD", "Mezzo HD", "Mezzo Live HD", "Stingray Classica HD", "MyZen TV HD", "Fashion TV France HD", "Game One HD", "Mangas TV HD", "J-One HD"]
}

CHANNELS_MAP = {}
global_id = 1
for cat_id, names in RAW_CHANNELS.items():
    for name in names:
        url = STREAM_LINKS["dz_sport"]
        if "Quran" in name or "القرآن" in name or "المجد" in name: url = STREAM_LINKS["ksa_quran"]
        elif "Arabiya" in name or "العربية" in name or "Hadath" in name: url = STREAM_LINKS["ksa_news"]
        CHANNELS_MAP[global_id] = {"name": name, "category_id": cat_id, "url": url}
        global_id += 1

def validate_client(username, password):
    return username in VALID_CREDENTIALS and VALID_CREDENTIALS[username] == password

@app.route('/player_api.php')
def player_api():
    user, pwd = request.args.get("username"), request.args.get("password")
    if not validate_client(user, pwd): return jsonify({"user_info": {"auth": 0}}), 403
    
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
        for s_id, ch in CHANNELS_MAP.items():
            if category_id and ch["category_id"] != category_id: continue
            streams.append({"num": s_id, "name": ch["name"], "stream_type": "live", "stream_id": s_id, "stream_icon": "", "category_id": ch["category_id"], "added": "1611874800"})
        return jsonify(streams)
    return jsonify([])

@app.route('/live/<username>/<password>/<int:stream_id>.ts')
@app.route('/live/<username>/<password>/<int:stream_id>')
def stream_proxy(username, password, stream_id):
    if not validate_client(username, password): return "Unauthorized", 403
    if stream_id in CHANNELS_MAP:
        return Response(status=302, headers={"Location": CHANNELS_MAP[stream_id]["url"]})
    return "Not Found", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
