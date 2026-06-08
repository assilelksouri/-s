import os
import time
from flask import Flask, request, jsonify, Response

app = Flask(__name__)

# أضف هذا السطر هنا ليتعرف عليه Vercel كـ handler رئيسي ومباشر
handler = app

# بيانات الدخول الثابتة والسريعة
VALID_CREDENTIALS = {"assil": "123", "admin": "admin"}

# الأقسام الـ 9 المنظمة بالترتيب للدول الثلاث
CATEGORIES = [
    # أقسام الجزائر
    {"category_id": "1", "category_name": "🇩🇿 DZ : SPORTS & FOOTBALL", "parent_id": 0},
    {"category_id": "2", "category_name": "🇩🇿 DZ : NEWS & EXTRA", "parent_id": 0},
    {"category_id": "3", "category_name": "🇩🇿 DZ : GENERAL & ENTERTAINMENT", "parent_id": 0},
    
    # أقسام السعودية
    {"category_id": "4", "category_name": "🇸🇦 KSA : SPORTS", "parent_id": 0},
    {"category_id": "5", "category_name": "🇸🇦 KSA : NEWS", "parent_id": 0},
    {"category_id": "6", "category_name": "🇸🇦 KSA : GENERAL & ENTERTAINMENT", "parent_id": 0},
    
    # أقسام فرنسا
    {"category_id": "7", "category_name": "🇫🇷 FR : SPORTS", "parent_id": 0},
    {"category_id": "8", "category_name": "🇫🇷 FR : NEWS", "parent_id": 0},
    {"category_id": "9", "category_name": "🇫🇷 FR : GENERAL & ENTERTAINMENT", "parent_id": 0}
]

# روابط البث الحية المباشرة والصافية لضمان عمل مشغل الرسيفر فوراً
TS_STREAM = "http://rt-arabic.rbm.tv/rt-arabic.ts"

CHANNELS_DATA = [
    # ==================== الجزائر (DZ) ====================
    # === 1. DZ : SPORTS ===
    {"stream_id": 101, "name": "TV6 Algerie HD", "category_id": "1", "url": TS_STREAM},
    {"stream_id": 102, "name": "TV6 Algerie SD", "category_id": "1", "url": TS_STREAM},
    {"stream_id": 103, "name": "TV6 Algerie 4K", "category_id": "1", "url": TS_STREAM},
    {"stream_id": 104, "name": "Programme National HD (الأرضية)", "category_id": "1", "url": TS_STREAM},
    {"stream_id": 105, "name": "Programme National SD", "category_id": "1", "url": TS_STREAM},
    {"stream_id": 106, "name": "El Heddaf TV HD", "category_id": "1", "url": TS_STREAM},
    {"stream_id": 107, "name": "El Heddaf TV SD", "category_id": "1", "url": TS_STREAM},
    {"stream_id": 108, "name": "Stade News TV", "category_id": "1", "url": TS_STREAM},
    {"stream_id": 109, "name": "Dzair Sport HD", "category_id": "1", "url": TS_STREAM},
    {"stream_id": 110, "name": "Dzair Sport 2", "category_id": "1", "url": TS_STREAM},
    {"stream_id": 111, "name": "El Adjwaa Sport", "category_id": "1", "url": TS_STREAM},
    {"stream_id": 112, "name": "JSK TV", "category_id": "1", "url": TS_STREAM},
    {"stream_id": 113, "name": "MCA TV", "category_id": "1", "url": TS_STREAM},
    {"stream_id": 114, "name": "USMA TV", "category_id": "1", "url": TS_STREAM},
    {"stream_id": 115, "name": "CRB TV", "category_id": "1", "url": TS_STREAM},
    {"stream_id": 116, "name": "ESS TV", "category_id": "1", "url": TS_STREAM},
    {"stream_id": 117, "name": "CSC TV", "category_id": "1", "url": TS_STREAM},
    {"stream_id": 118, "name": "MCO TV", "category_id": "1", "url": TS_STREAM},
    {"stream_id": 119, "name": "Setif Sport TV", "category_id": "1", "url": TS_STREAM},
    {"stream_id": 120, "name": "Algeria Sports Live 1", "category_id": "1", "url": TS_STREAM},
    {"stream_id": 121, "name": "Algeria Sports Live 2", "category_id": "1", "url": TS_STREAM},
    {"stream_id": 122, "name": "Kooora DZ TV", "category_id": "1", "url": TS_STREAM},

    # === 2. DZ : NEWS ===
    {"stream_id": 131, "name": "AL24 News HD", "category_id": "2", "url": TS_STREAM},
    {"stream_id": 132, "name": "AL24 News SD", "category_id": "2", "url": TS_STREAM},
    {"stream_id": 133, "name": "AL24 News English", "category_id": "2", "url": TS_STREAM},
    {"stream_id": 134, "name": "AL24 News French", "category_id": "2", "url": TS_STREAM},
    {"stream_id": 135, "name": "AL24 News Spanish", "category_id": "2", "url": TS_STREAM},
    {"stream_id": 136, "name": "Ennahar TV HD", "category_id": "2", "url": TS_STREAM},
    {"stream_id": 137, "name": "Ennahar TV SD", "category_id": "2", "url": TS_STREAM},
    {"stream_id": 138, "name": "Ennahar +", "category_id": "2", "url": TS_STREAM},
    {"stream_id": 139, "name": "Echorouk News HD", "category_id": "2", "url": TS_STREAM},
    {"stream_id": 140, "name": "Echorouk News SD", "category_id": "2", "url": TS_STREAM},
    {"stream_id": 141, "name": "Echorouk News 4K", "category_id": "2", "url": TS_STREAM},
    {"stream_id": 142, "name": "El Bilad TV HD", "category_id": "2", "url": TS_STREAM},
    {"stream_id": 143, "name": "El Bilad TV SD", "category_id": "2", "url": TS_STREAM},
    {"stream_id": 144, "name": "El Bilad +", "category_id": "2", "url": TS_STREAM},
    {"stream_id": 145, "name": "El Hayat TV HD", "category_id": "2", "url": TS_STREAM},
    {"stream_id": 146, "name": "El Hayat TV SD", "category_id": "2", "url": TS_STREAM},
    {"stream_id": 147, "name": "El Adjwaa TV HD", "category_id": "2", "url": TS_STREAM},
    {"stream_id": 148, "name": "El Adjwaa TV SD", "category_id": "2", "url": TS_STREAM},
    {"stream_id": 149, "name": "Numidia News HD", "category_id": "2", "url": TS_STREAM},
    {"stream_id": 150, "name": "Numidia TV", "category_id": "2", "url": TS_STREAM},
    {"stream_id": 151, "name": "Dzair News", "category_id": "2", "url": TS_STREAM},
    {"stream_id": 152, "name": "KBC News", "category_id": "2", "url": TS_STREAM},
    {"stream_id": 153, "name": "Hoggar News", "category_id": "2", "url": TS_STREAM},
    {"stream_id": 154, "name": "Lindex News", "category_id": "2", "url": TS_STREAM},
    {"stream_id": 155, "name": "Kawaliss News", "category_id": "2", "url": TS_STREAM},
    {"stream_id": 156, "name": "Algeria 24/7", "category_id": "2", "url": TS_STREAM},
    {"stream_id": 157, "name": "DZ News Live", "category_id": "2", "url": TS_STREAM},
    {"stream_id": 158, "name": "Al Magharibia HD", "category_id": "2", "url": TS_STREAM},
    {"stream_id": 159, "name": "Al Magharibia SD", "category_id": "2", "url": TS_STREAM},
    {"stream_id": 160, "name": "Al Magharibia 2", "category_id": "2", "url": TS_STREAM},
    {"stream_id": 161, "name": "Rachad TV", "category_id": "2", "url": TS_STREAM},
    {"stream_id": 162, "name": "Amel TV", "category_id": "2", "url": TS_STREAM},
    {"stream_id": 163, "name": "Free Algeria TV", "category_id": "2", "url": TS_STREAM},
    {"stream_id": 164, "name": "Sawt Al Djazair", "category_id": "2", "url": TS_STREAM},
    {"stream_id": 165, "name": "El Hiwar DZ", "category_id": "2", "url": TS_STREAM},
    {"stream_id": 166, "name": "El Badil TV", "category_id": "2", "url": TS_STREAM},

    # === 3. DZ : GENERAL ===
    {"stream_id": 181, "name": "TV1 Algerie HD", "category_id": "3", "url": TS_STREAM},
    {"stream_id": 182, "name": "TV1 Algerie SD", "category_id": "3", "url": TS_STREAM},
    {"stream_id": 183, "name": "Canal Algerie HD", "category_id": "3", "url": TS_STREAM},
    {"stream_id": 184, "name": "Canal Algerie SD", "category_id": "3", "url": TS_STREAM},
    {"stream_id": 185, "name": "A3 Algerie HD", "category_id": "3", "url": TS_STREAM},
    {"stream_id": 186, "name": "A3 Algerie SD", "category_id": "3", "url": TS_STREAM},
    {"stream_id": 187, "name": "Echorouk TV HD", "category_id": "3", "url": TS_STREAM},
    {"stream_id": 188, "name": "Echorouk TV SD", "category_id": "3", "url": TS_STREAM},
    {"stream_id": 189, "name": "Echorouk +", "category_id": "3", "url": TS_STREAM},
    {"stream_id": 190, "name": "El Fadjr TV HD", "category_id": "3", "url": TS_STREAM},
    {"stream_id": 191, "name": "El Fadjr TV SD", "category_id": "3", "url": TS_STREAM},
    {"stream_id": 192, "name": "El Fadjr TV 2 (الدراما)", "category_id": "3", "url": TS_STREAM},
    {"stream_id": 193, "name": "Bahia TV HD (الباهية)", "category_id": "3", "url": TS_STREAM},
    {"stream_id": 194, "name": "Bahia TV SD", "category_id": "3", "url": TS_STREAM},
    {"stream_id": 195, "name": "El Djazaïria One HD", "category_id": "3", "url": TS_STREAM},
    {"stream_id": 196, "name": "El Djazaïria One SD", "category_id": "3", "url": TS_STREAM},
    {"stream_id": 197, "name": "El Djazaïria TV", "category_id": "3", "url": TS_STREAM},
    {"stream_id": 198, "name": "Beur TV HD", "category_id": "3", "url": TS_STREAM},
    {"stream_id": 199, "name": "Beur TV SD", "category_id": "3", "url": TS_STREAM},
    {"stream_id": 200, "name": "Hoggar TV", "category_id": "3", "url": TS_STREAM},
    {"stream_id": 2011, "name": "Lindex TV", "category_id": "3", "url": TS_STREAM},
    {"stream_id": 2012, "name": "Kawaliss TV", "category_id": "3", "url": TS_STREAM},
    {"stream_id": 2013, "name": "Dzair TV", "category_id": "3", "url": TS_STREAM},
    {"stream_id": 2014, "name": "Lina TV HD", "category_id": "3", "url": TS_STREAM},
    {"stream_id": 2015, "name": "Lina TV SD", "category_id": "3", "url": TS_STREAM},
    {"stream_id": 2016, "name": "Wiam TV", "category_id": "3", "url": TS_STREAM},
    {"stream_id": 2017, "name": "DTV Algerie HD", "category_id": "3", "url": TS_STREAM},
    {"stream_id": 2018, "name": "DTV Anime", "category_id": "3", "url": TS_STREAM},
    {"stream_id": 2019, "name": "DTV Movies", "category_id": "3", "url": TS_STREAM},
    {"stream_id": 2020, "name": "Atlas TV", "category_id": "3", "url": TS_STREAM},
    {"stream_id": 2021, "name": "El Adjwaa Drama", "category_id": "3", "url": TS_STREAM},
    {"stream_id": 2022, "name": "El Adjwaa Cinema", "category_id": "3", "url": TS_STREAM},
    {"stream_id": 2023, "name": "Ennahar Laki", "category_id": "3", "url": TS_STREAM},
    {"stream_id": 2024, "name": "Al Asr TV", "category_id": "3", "url": TS_STREAM},
    {"stream_id": 2025, "name": "El Rihab TV", "category_id": "3", "url": TS_STREAM},
    {"stream_id": 2026, "name": "Al Makam TV", "category_id": "3", "url": TS_STREAM},
    {"stream_id": 2027, "name": "GO TV Algeria", "category_id": "3", "url": TS_STREAM},
    {"stream_id": 2028, "name": "El Djazaïr TV", "category_id": "3", "url": TS_STREAM},
    {"stream_id": 2029, "name": "Seybouse TV", "category_id": "3", "url": TS_STREAM},
    {"stream_id": 2030, "name": "Numidia Drama", "category_id": "3", "url": TS_STREAM},
    {"stream_id": 2031, "name": "El Fadjr Cinema", "category_id": "3", "url": TS_STREAM},
    {"stream_id": 2032, "name": "El Fadjr Drama", "category_id": "3", "url": TS_STREAM},
    {"stream_id": 2033, "name": "Bahia Drama", "category_id": "3", "url": TS_STREAM},
    {"stream_id": 2034, "name": "Jil TV", "category_id": "3", "url": TS_STREAM},
    {"stream_id": 2035, "name": "Master TV Algeria", "category_id": "3", "url": TS_STREAM},
    {"stream_id": 2036, "name": "Flame TV Algeria", "category_id": "3", "url": TS_STREAM},
    {"stream_id": 2037, "name": "One TV Algeria", "category_id": "3", "url": TS_STREAM},
    {"stream_id": 2038, "name": "Sweet TV DZ", "category_id": "3", "url": TS_STREAM},


    # ==================== المملكة العربية السعودية (KSA) ====================
    # === 4. KSA : SPORTS ===
    {"stream_id": 401, "name": "SSC 1 HD", "category_id": "4", "url": "https://win.holol.com/live/quran/playlist.m3u8"},
    {"stream_id": 402, "name": "SSC 1 SD", "category_id": "4", "url": "https://win.holol.com/live/quran/playlist.m3u8"},
    {"stream_id": 403, "name": "SSC 1 4K", "category_id": "4", "url": "https://win.holol.com/live/quran/playlist.m3u8"},
    {"stream_id": 404, "name": "SSC 2 HD", "category_id": "4", "url": "https://win.holol.com/live/quran/playlist.m3u8"},
    {"stream_id": 405, "name": "SSC 2 SD", "category_id": "4", "url": "https://win.holol.com/live/quran/playlist.m3u8"},
    {"stream_id": 406, "name": "SSC 3 HD", "category_id": "4", "url": "https://win.holol.com/live/quran/playlist.m3u8"},
    {"stream_id": 407, "name": "SSC 4 HD", "category_id": "4", "url": "https://win.holol.com/live/quran/playlist.m3u8"},
    {"stream_id": 408, "name": "SSC 5 HD", "category_id": "4", "url": "https://win.holol.com/live/quran/playlist.m3u8"},
    {"stream_id": 409, "name": "SSC EXTRA 1 HD", "category_id": "4", "url": "https://win.holol.com/live/quran/playlist.m3u8"},
    {"stream_id": 410, "name": "SSC EXTRA 2 HD", "category_id": "4", "url": "https://win.holol.com/live/quran/playlist.m3u8"},
    {"stream_id": 411, "name": "SSC EXTRA 3 HD", "category_id": "4", "url": "https://win.holol.com/live/quran/playlist.m3u8"},
    {"stream_id": 412, "name": "Al Kass Saudi 1 HD", "category_id": "4", "url": "https://win.holol.com/live/quran/playlist.m3u8"},
    {"stream_id": 413, "name": "KSA Sports 1 HD", "category_id": "4", "url": "https://win.holol.com/live/sunnah/playlist.m3u8"},
    {"stream_id": 414, "name": "KSA Sports 1 SD", "category_id": "4", "url": "https://win.holol.com/live/sunnah/playlist.m3u8"},
    {"stream_id": 415, "name": "KSA Sports 2 HD", "category_id": "4", "url": "https://win.holol.com/live/sunnah/playlist.m3u8"},
    {"stream_id": 416, "name": "KSA Sports 3 HD", "category_id": "4", "url": "https://win.holol.com/live/sunnah/playlist.m3u8"},
    {"stream_id": 417, "name": "Al Nassr TV", "category_id": "4", "url": "https://win.holol.com/live/quran/playlist.m3u8"},
    {"stream_id": 418, "name": "Al Hilal TV", "category_id": "4", "url": "https://win.holol.com/live/quran/playlist.m3u8"},
    {"stream_id": 419, "name": "Al Ittihad TV", "category_id": "4", "url": "https://win.holol.com/live/quran/playlist.m3u8"},
    {"stream_id": 420, "name": "Al Ahli TV", "category_id": "4", "url": "https://win.holol.com/live/quran/playlist.m3u8"},
    {"stream_id": 421, "name": "Saudi Sport Live 1", "category_id": "4", "url": "https://win.holol.com/live/sunnah/playlist.m3u8"},
    {"stream_id": 422, "name": "Saudi Sport Live 2", "category_id": "4", "url": "https://win.holol.com/live/sunnah/playlist.m3u8"},
    {"stream_id": 423, "name": "Dawri Plus HD", "category_id": "4", "url": "https://win.holol.com/live/quran/playlist.m3u8"},
    {"stream_id": 424, "name": "Riyadh Sport TV", "category_id": "4", "url": "https://win.holol.com/live/quran/playlist.m3u8"},

    # === 5. KSA : NEWS ===
    {"stream_id": 501, "name": "Al Arabiya HD", "category_id": "5", "url": "https://live.alarabiya.net/alarabiya/alarabiya.m3u8"},
    {"stream_id": 502, "name": "Al Arabiya SD", "category_id": "5", "url": "https://live.alarabiya.net/alarabiya/alarabiya.m3u8"},
    {"stream_id": 503, "name": "Al Arabiya 4K", "category_id": "5", "url": "https://live.alarabiya.net/alarabiya/alarabiya.m3u8"},
    {"stream_id": 504, "name": "Al Arabiya Al Hadath HD", "category_id": "5", "url": "https://live.alarabiya.net/alarabiya/alarabiya.m3u8"},
    {"stream_id": 505, "name": "Al Arabiya Al Hadath SD", "category_id": "5", "url": "https://live.alarabiya.net/alarabiya/alarabiya.m3u8"},
    {"stream_id": 506, "name": "Al Ekhbariya HD", "category_id": "5", "url": "https://win.holol.com/live/sunnah/playlist.m3u8"},
    {"stream_id": 507, "name": "Al Ekhbariya SD", "category_id": "5", "url": "https://win.holol.com/live/sunnah/playlist.m3u8"},
    {"stream_id": 508, "name": "Saudi 24 News", "category_id": "5", "url": "https://win.holol.com/live/quran/playlist.m3u8"},
    {"stream_id": 509, "name": "Al Sharq News HD", "category_id": "5", "url": "https://live.alarabiya.net/alarabiya/alarabiya.m3u8"},
    {"stream_id": 510, "name": "Al Sharq News 4K", "category_id": "5", "url": "https://live.alarabiya.net/alarabiya/alarabiya.m3u8"},
    {"stream_id": 511, "name": "Al Sharq Business", "category_id": "5", "url": "https://live.alarabiya.net/alarabiya/alarabiya.m3u8"},
    {"stream_id": 512, "name": "Asharq Discovery HD", "category_id": "5", "url": "https://live.alarabiya.net/alarabiya/alarabiya.m3u8"},
    {"stream_id": 513, "name": "Saudia 24 Direct", "category_id": "5", "url": "https://win.holol.com/live/quran/playlist.m3u8"},
    {"stream_id": 514, "name": "KSA Politics Live", "category_id": "5", "url": "https://win.holol.com/live/sunnah/playlist.m3u8"},

    # === 6. KSA : GENERAL ===
    {"stream_id": 601, "name": "Saudi TV 1 HD", "category_id": "6", "url": "https://win.holol.com/live/quran/playlist.m3u8"},
    {"stream_id": 602, "name": "Saudi TV 1 SD", "category_id": "6", "url": "https://win.holol.com/live/quran/playlist.m3u8"},
    {"stream_id": 603, "name": "SBC HD", "category_id": "6", "url": "https://win.holol.com/live/sunnah/playlist.m3u8"},
    {"stream_id": 604, "name": "SBC SD", "category_id": "6", "url": "https://win.holol.com/live/sunnah/playlist.m3u8"},
    {"stream_id": 605, "name": "MBC 1 HD", "category_id": "6", "url": "https://live.alarabiya.net/alarabiya/alarabiya.m3u8"},
    {"stream_id": 606, "name": "MBC 1 SD", "category_id": "6", "url": "https://live.alarabiya.net/alarabiya/alarabiya.m3u8"},
    {"stream_id": 607, "name": "MBC 1 4K", "category_id": "6", "url": "https://live.alarabiya.net/alarabiya/alarabiya.m3u8"},
    {"stream_id": 608, "name": "MBC 2 HD", "category_id": "6", "url": "https://live.alarabiya.net/alarabiya/alarabiya.m3u8"},
    {"stream_id": 609, "name": "MBC 4 HD", "category_id": "6", "url": "https://live.alarabiya.net/alarabiya/alarabiya.m3u8"},
    {"stream_id": 610, "name": "MBC Action HD", "category_id": "6", "url": "https://live.alarabiya.net/alarabiya/alarabiya.m3u8"},
    {"stream_id": 611, "name": "MBC Max HD", "category_id": "6", "url": "https://live.alarabiya.net/alarabiya/alarabiya.m3u8"},
    {"stream_id": 612, "name": "MBC Drama HD", "category_id": "6", "url": "https://live.alarabiya.net/alarabiya/alarabiya.m3u8"},
    {"stream_id": 613, "name": "MBC Drama +", "category_id": "6", "url": "https://live.alarabiya.net/alarabiya/alarabiya.m3u8"},
    {"stream_id": 614, "name": "MBC Bollywood HD", "category_id": "6", "url": "https://live.alarabiya.net/alarabiya/alarabiya.m3u8"},
    {"stream_id": 615, "name": "MBC Masr HD", "category_id": "6", "url": "https://live.alarabiya.net/alarabiya/alarabiya.m3u8"},
    {"stream_id": 616, "name": "MBC Masr 2 HD", "category_id": "6", "url": "https://live.alarabiya.net/alarabiya/alarabiya.m3u8"},
    {"stream_id": 617, "name": "MBC Iraq HD", "category_id": "6", "url": "https://live.alarabiya.net/alarabiya/alarabiya.m3u8"},
    {"stream_id": 618, "name": "MBC Maghreb HD", "category_id": "6", "url": "https://live.alarabiya.net/alarabiya/alarabiya.m3u8"},
    {"stream_id": 619, "name": "Wanasah TV HD", "category_id": "6", "url": "https://live.alarabiya.net/alarabiya/alarabiya.m3u8"},
    {"stream_id": 620, "name": "Al Danah TV", "category_id": "6", "url": "https://win.holol.com/live/quran/playlist.m3u8"},
    {"stream_id": 621, "name": "Al Sahan TV", "category_id": "6", "url": "https://win.holol.com/live/quran/playlist.m3u8"},
    {"stream_id": 622, "name": "Al Merqab TV", "category_id": "6", "url": "https://win.holol.com/live/quran/playlist.m3u8"},
    {"stream_id": 623, "name": "Bedaya TV", "category_id": "6", "url": "https://win.holol.com/live/sunnah/playlist.m3u8"},
    {"stream_id": 624, "name": "Al Waha TV", "category_id": "6", "url": "https://win.holol.com/live/quran/playlist.m3u8"},
    {"stream_id": 625, "name": "Diwan Jeddah TV", "category_id": "6", "url": "https://win.holol.com/live/quran/playlist.m3u8"},
    {"stream_id": 626, "name": "Shada TV", "category_id": "6", "url": "https://win.holol.com/live/quran/playlist.m3u8"},
    {"stream_id": 627, "name": "Saudia 24 General", "category_id": "6", "url": "https://win.holol.com/live/quran/playlist.m3u8"},
    {"stream_id": 628, "name": "Al Shamil TV", "category_id": "6", "url": "https://win.holol.com/live/quran/playlist.m3u8"},
    {"stream_id": 629, "name": "KSA One", "category_id": "6", "url": "https://win.holol.com/live/sunnah/playlist.m3u8"},
    {"stream_id": 630, "name": "Thaqafia TV HD", "category_id": "6", "url": "https://win.holol.com/live/quran/playlist.m3u8"},
    {"stream_id": 631, "name": "Rotana Khalijia HD", "category_id": "6", "url": "https://live.alarabiya.net/alarabiya/alarabiya.m3u8"},
    {"stream_id": 632, "name": "Rotana Cinema KSA HD", "category_id": "6", "url": "https://live.alarabiya.net/alarabiya/alarabiya.m3u8"},


    # ==================== فرنسا (FRANCE) ====================
    # === 7. FR : SPORTS ===
    {"stream_id": 701, "name": "Canal+ Foot HD", "category_id": "7", "url": TS_STREAM},
    {"stream_id": 702, "name": "Canal+ Foot 4K", "category_id": "7", "url": TS_STREAM},
    {"stream_id": 703, "name": "Canal+ Sport HD", "category_id": "7", "url": TS_STREAM},
    {"stream_id": 704, "name": "Canal+ Sport 4K", "category_id": "7", "url": TS_STREAM},
    {"stream_id": 705, "name": "Canal+ Sport 360 HD", "category_id": "7", "url": TS_STREAM},
    {"stream_id": 706, "name": "beIN Sports FR 1 HD", "category_id": "7", "url": TS_STREAM},
    {"stream_id": 707, "name": "beIN Sports FR 1 4K", "category_id": "7", "url": TS_STREAM},
    {"stream_id": 708, "name": "beIN Sports FR 2 HD", "category_id": "7", "url": TS_STREAM},
    {"stream_id": 709, "name": "beIN Sports FR 3 HD", "category_id": "7", "url": TS_STREAM},
    {"stream_id": 710, "name": "beIN Sports FR MAX 4 HD", "category_id": "7", "url": TS_STREAM},
    {"stream_id": 711, "name": "beIN Sports FR MAX 5 HD", "category_id": "7", "url": TS_STREAM},
    {"stream_id": 712, "name": "beIN Sports FR MAX 6 HD", "category_id": "7", "url": TS_STREAM},
    {"stream_id": 713, "name": "beIN Sports FR MAX 7 HD", "category_id": "7", "url": TS_STREAM},
    {"stream_id": 714, "name": "beIN Sports FR MAX 8 HD", "category_id": "7", "url": TS_STREAM},
    {"stream_id": 715, "name": "beIN Sports FR MAX 9 HD", "category_id": "7", "url": TS_STREAM},
    {"stream_id": 716, "name": "beIN Sports FR MAX 10 HD", "category_id": "7", "url": TS_STREAM},
    {"stream_id": 717, "name": "Eurosport 1 France HD", "category_id": "7", "url": TS_STREAM},
    {"stream_id": 718, "name": "Eurosport 2 France HD", "category_id": "7", "url": TS_STREAM},
    {"stream_id": 719, "name": "Eurosport 4K France", "category_id": "7", "url": TS_STREAM},
    {"stream_id": 720, "name": "RMC Sport Live 2", "category_id": "7", "url": TS_STREAM},
    {"stream_id": 721, "name": "RMC Sport Live 3", "category_id": "7", "url": TS_STREAM},
    {"stream_id": 722, "name": "RMC Sport Live 4", "category_id": "7", "url": TS_STREAM},
    {"stream_id": 723, "name": "L'Équipe TV HD", "category_id": "7", "url": TS_STREAM},
    {"stream_id": 724, "name": "L'Équipe TV SD", "category_id": "7", "url": TS_STREAM},
    {"stream_id": 725, "name": "Automoto TV HD", "category_id": "7", "url": TS_STREAM},
    {"stream_id": 726, "name": "Equidia HD", "category_id": "7", "url": TS_STREAM},
    {"stream_id": 727, "name": "OL Play", "category_id": "7", "url": TS_STREAM},
    {"stream_id": 728, "name": "OM Play", "category_id": "7", "url": TS_STREAM},
    {"stream_id": 729, "name": "PSG TV", "category_id": "7", "url": TS_STREAM},

    # === 8. FR : NEWS ===
    {"stream_id": 801, "name": "BFM TV HD", "category_id": "8", "url": TS_STREAM},
    {"stream_id": 802, "name": "BFM TV 4K", "category_id": "8", "url": TS_STREAM},
    {"stream_id": 803, "name": "BFM Business", "category_id": "8", "url": TS_STREAM},
    {"stream_id": 804, "name": "BFM Paris Île-de-France", "category_id": "8", "url": TS_STREAM},
    {"stream_id": 805, "name": "BFM Lyon", "category_id": "8", "url": TS_STREAM},
    {"stream_id": 806, "name": "BFM Grand Lille", "category_id": "8", "url": TS_STREAM},
    {"stream_id": 807, "name": "BFM Marseille Provence", "category_id": "8", "url": TS_STREAM},
    {"stream_id": 808, "name": "CNews HD", "category_id": "8", "url": TS_STREAM},
    {"stream_id": 809, "name": "LCI HD", "category_id": "8", "url": TS_STREAM},
    {"stream_id": 810, "name": "France Info TV HD", "category_id": "8", "url": TS_STREAM},
    {"stream_id": 811, "name": "France 24 Français HD", "category_id": "8", "url": "https://live.alarabiya.net/alarabiya/alarabiya.m3u8"},
    {"stream_id": 812, "name": "France 24 Français SD", "category_id": "8", "url": "https://live.alarabiya.net/alarabiya/alarabiya.m3u8"},
    {"stream_id": 813, "name": "Euronews Français HD", "category_id": "8", "url": TS_STREAM},
    {"stream_id": 814, "name": "Public Sénat HD", "category_id": "8", "url": TS_STREAM},
    {"stream_id": 815, "name": "LCP HD", "category_id": "8", "url": TS_STREAM},

    # === 9. FR : GENERAL ===
    {"stream_id": 901, "name": "TF1 HD", "category_id": "9", "url": TS_STREAM},
    {"stream_id": 902, "name": "TF1 SD", "category_id": "9", "url": TS_STREAM},
    {"stream_id": 903, "name": "TF1 4K", "category_id": "9", "url": TS_STREAM},
    {"stream_id": 904, "name": "TF1 +", "category_id": "9", "url": TS_STREAM},
    {"stream_id": 905, "name": "TF1 Séries Films HD", "category_id": "9", "url": TS_STREAM},
    {"stream_id": 906, "name": "France 2 HD", "category_id": "9", "url": TS_STREAM},
    {"stream_id": 907, "name": "France 2 SD", "category_id": "9", "url": TS_STREAM},
    {"stream_id": 908, "name": "France 2 4K", "category_id": "9", "url": TS_STREAM},
    {"stream_id": 909, "name": "France 3 National HD", "category_id": "9", "url": TS_STREAM},
    {"stream_id": 910, "name": "France 3 Paris Île-de-France", "category_id": "9", "url": TS_STREAM},
    {"stream_id": 911, "name": "France 3 Aquitaine", "category_id": "9", "url": TS_STREAM},
    {"stream_id": 912, "name": "France 3 Provence-Alpes", "category_id": "9", "url": TS_STREAM},
    {"stream_id": 913, "name": "France 3 Alpes", "category_id": "9", "url": TS_STREAM},
    {"stream_id": 914, "name": "France 3 Alsace", "category_id": "9", "url": TS_STREAM},
    {"stream_id": 915, "name": "France 4 HD", "category_id": "9", "url": TS_STREAM},
    {"stream_id": 916, "name": "France 5 HD", "category_id": "9", "url": TS_STREAM},
    {"stream_id": 917, "name": "M6 HD", "category_id": "9", "url": TS_STREAM},
    {"stream_id": 918, "name": "M6 SD", "category_id": "9", "url": TS_STREAM},
    {"stream_id": 919, "name": "M6 4K", "category_id": "9", "url": TS_STREAM},
    {"stream_id": 920, "name": "M6 +", "category_id": "9", "url": TS_STREAM},
    {"stream_id": 921, "name": "Arte France HD", "category_id": "9", "url": TS_STREAM},
    {"stream_id": 922, "name": "Arte France 4K", "category_id": "9", "url": TS_STREAM},
    {"stream_id": 923, "name": "C8 France HD", "category_id": "9", "url": TS_STREAM},
    {"stream_id": 924, "name": "W9 HD", "category_id": "9", "url": TS_STREAM},
    {"stream_id": 925, "name": "TMC France HD", "category_id": "9", "url": TS_STREAM},
    {"stream_id": 926, "name": "TFX HD", "category_id": "9", "url": TS_STREAM},
    {"stream_id": 927, "name": "NRJ 12 HD", "category_id": "9", "url": TS_STREAM},
    {"stream_id": 928, "name": "Culturebox HD", "category_id": "9", "url": TS_STREAM},
    {"stream_id": 929, "name": "Canal+ France HD", "category_id": "9", "url": TS_STREAM},
    {"stream_id": 930, "name": "Canal+ France 4K", "category_id": "9", "url": TS_STREAM},
    {"stream_id": 931, "name": "Canal+ Cinéma(s) HD", "category_id": "9", "url": TS_STREAM},
    {"stream_id": 932, "name": "Canal+ Grand Écran HD", "category_id": "9", "url": TS_STREAM},
    {"stream_id": 933, "name": "Canal+ Box Office HD", "category_id": "9", "url": TS_STREAM},
    {"stream_id": 934, "name": "Canal+ Box Office 4K", "category_id": "9", "url": TS_STREAM},
    {"stream_id": 935, "name": "Canal+ Séries HD", "category_id": "9", "url": TS_STREAM},
    {"stream_id": 936, "name": "Warner TV France HD", "category_id": "9", "url": TS_STREAM},
    {"stream_id": 937, "name": "Paramount Channel France HD", "category_id": "9", "url": TS_STREAM},
    {"stream_id": 938, "name": "Action TV France HD", "category_id": "9", "url": TS_STREAM},
    {"stream_id": 939, "name": "TCM Cinéma France HD", "category_id": "9", "url": TS_STREAM},
    {"stream_id": 940, "name": "Polar+ HD", "category_id": "9", "url": TS_STREAM},
    {"stream_id": 941, "name": "Novelas TV France HD", "category_id": "9", "url": TS_STREAM},
    {"stream_id": 942, "name": "Serieclub HD", "category_id": "9", "url": TS_STREAM},
    {"stream_id": 943, "name": "TV Breizh HD", "category_id": "9", "url": TS_STREAM}
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
            streams.append({
                "num": ch["stream_id"], "name": ch["name"], "stream_type": "live",
                "stream_id": ch["stream_id"], "stream_icon": "",
                "category_id": ch["category_id"], "added": "1611874800"
            })
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
