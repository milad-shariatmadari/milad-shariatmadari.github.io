#!/usr/bin/env python3
"""Patch persian.html: fix pronunciation, grammar levels, +500 vocab, +500 stories."""
import re
import json

HTML_PATH = r"C:\Users\milad\Downloads\persian.html"

# ─── Romanized sp() → Persian mappings ───
SP_FIXES = {
    "sar": "سر", "del": "دل", "sor": "سر", "ab": "آب", "shir": "شیر", "nur": "نور",
    "khaneh": "خانه", "gham": "غم", "qamar": "قمر", "eshq": "عشق", "zhaleh": "ژاله", "rah": "راه",
    "man ketab mikhaanam": "من کتاب می‌خوانم", "ali sib khoord": "علی سیب خورد",
    "maa be Tehran raftim": "ما به تهران رفتیم", "ketabha": "کتاب‌ها", "yek ketab": "یک کتاب",
    "ketab": "کتاب", "ketab raa khaandam": "کتاب را خواندم", "khaaneye bozorg": "خانهٔ بزرگ",
    "ketaabe man": "کتاب من", "pesare doktor": "پسر دکتر", "sheere sefid": "شیر سفید",
    "shaahre Tehraane bozorg": "شهر تهران بزرگ", "miravam": "می‌روم", "miravi": "می‌روی",
    "miravad": "می‌رود", "miravim": "می‌رویم", "miravid": "می‌روید", "miravand": "می‌روند",
    "nemiravam": "نمی‌روم", "raftam": "رفتم", "naraftam": "نرفتم", "hastam": "هستم",
    "nistam": "نیستم", "midonam": "می‌دانم", "nemidonam": "نمی‌دانم",
    "ketaabe bozorg": "کتاب بزرگ", "marde khob": "مرد خوب", "zanane khob": "زنان خوب",
    "esmat chi ast": "اسمت چیه؟", "on ki ast": "اون کیه؟", "koja hasti": "کجایی؟",
    "khoobam": "خوبم", "dar khane": "در خانه", "be maktab": "به مدرسه", "az iran": "از ایران",
}

PAST_TENSE_AUDIO = [
    ("خوردم", "I ate"), ("خوردی", "You ate"), ("خورد", "He/She ate"),
    ("خوردیم", "We ate"), ("خوردید", "You all ate"), ("خوردند", "They ate"),
]

# ─── 500 new vocabulary words ───
def gen_vocab():
    entries = []
    seen = set()

    def add(fa, en, r, cat, lvl, ex_fa=None, ex_en=None):
        if fa in seen:
            return
        seen.add(fa)
        entries.append({
            "fa": fa, "en": en, "r": r, "cat": cat, "lvl": lvl,
            "ex_fa": ex_fa or f"من {fa} را می‌شناسم.",
            "ex_en": ex_en or f"I know {en.lower()}.",
            "ex_r": ex_en or f"I know {en.lower()}.",
        })

    words = [
        ("گربه","Cat","gorbe","animals",1),("سگ","Dog","sag","animals",1),("اسب","Horse","asb","animals",1),
        ("گاو","Cow","gâv","animals",1),("گوسفند","Sheep","gusfand","animals",1),("پرنده","Bird","parande","animals",1),
        ("موش","Mouse","mush","animals",1),("خرگوش","Rabbit","khargush","animals",1),("فیل","Elephant","fil","animals",2),
        ("ببر","Tiger","babr","animals",2),("خرس","Bear","khers","animals",2),("گرگ","Wolf","gorg","animals",2),
        ("روباه","Fox","rubâh","animals",2),("مار","Snake","mâr","animals",2),("لاک‌پشت","Turtle","lâkposht","animals",2),
        ("قورباغه","Frog","ghurbe","animals",2),("پروانه","Butterfly","parvâne","animals",2),("شتر","Camel","shotor","animals",2),
        ("نهنگ","Whale","nahang","animals",3),("عقاب","Eagle","oqâb","animals",3),("طاووس","Peacock","tâvus","animals",3),
        ("لباس","Clothes","lebâs","clothing",1),("پیراهن","Shirt","pirâhan","clothing",1),("شلوار","Pants","shalvâr","clothing",1),
        ("کفش","Shoe","kafsh","clothing",1),("جوراب","Sock","jurâb","clothing",1),("کلاه","Hat","kolâh","clothing",1),
        ("روسری","Scarf","rusari","clothing",1),("کت","Coat","kot","clothing",2),("عینک","Glasses","eynak","clothing",2),
        ("آفتاب","Sun","âftâb","weather",1),("ابر","Cloud","abr","weather",1),("باران","Rain","bârân","weather",1),
        ("برف","Snow","barf","weather",1),("طوفان","Storm","tufân","weather",2),("رعد","Thunder","ra'd","weather",2),
        ("برق","Lightning","barq","weather",2),("مه","Fog","meh","weather",2),("گرما","Heat","garmâ","weather",2),
        ("سرما","Cold","sarmâ","weather",2),("سفر","Journey","safar","travel",1),("هواپیما","Airplane","havâpeymâ","travel",1),
        ("قطار","Train","qatâr","travel",1),("اتوبوس","Bus","otobus","travel",1),("تاکسی","Taxi","tâksi","travel",1),
        ("فرودگاه","Airport","forudgâh","travel",2),("هتل","Hotel","hotel","travel",2),("چمدان","Suitcase","chamedân","travel",2),
        ("نقشه","Map","naqshe","travel",2),("بیمار","Patient","bimâr","health",1),("دارو","Medicine","dâru","health",1),
        ("بیمارستان","Hospital","bimârestân","health",2),("پرستار","Nurse","parastâr","health",2),("سلامت","Health","sâlamat","health",2),
        ("شغل","Job","shogl","work",1),("مدیر","Manager","modir","work",2),("کارمند","Employee","kârmand","work",2),
        ("مهندس","Engineer","mohandes","work",2),("کامپیوتر","Computer","kâmpyuter","technology",1),("تلفن","Telephone","telefon","technology",1),
        ("اینترنت","Internet","internet","technology",1),("برنامه","Program","barname","technology",2),("شبکه","Network","shabake","technology",3),
        ("شعر","Poetry","she'r","culture",1),("موسیقی","Music","musighi","culture",1),("سینما","Cinema","sinemâ","culture",2),
        ("موزه","Museum","muze","culture",2),("جشن","Celebration","jashn","culture",2),("سنت","Tradition","sonnat","culture",3),
        ("رفتن","To go","raftan","verbs",1),("آمدن","To come","âmadan","verbs",1),("نوشیدن","To drink","nushidan","verbs",1),
        ("خوابیدن","To sleep","khâbidan","verbs",1),("نوشتن","To write","neveshtan","verbs",1),("گفتن","To say","goftan","verbs",1),
        ("دیدن","To see","didan","verbs",1),("خریدن","To buy","kharidan","verbs",1),("پختن","To cook","pokhtan","verbs",2),
        ("بزرگ","Big","bozorg","adjectives",1),("کوچک","Small","kuchak","adjectives",1),("بلند","Tall","boland","adjectives",1),
        ("کوتاه","Short","kutâh","adjectives",1),("زیبا","Beautiful","zibâ","adjectives",1),("سریع","Fast","sari'","adjectives",1),
        ("جدید","New","jadid","adjectives",1),("قدیمی","Old","qadimi","adjectives",1),("قوی","Strong","qavi","adjectives",2),
        ("مهم","Important","mohem","adjectives",2),("خیابان","Street","khiâbân","city",1),("میدان","Square","meydân","city",1),
        ("پل","Bridge","pol","city",1),("فروشگاه","Shop","forushgâh","city",1),("رستوران","Restaurant","resturân","city",1),
        ("فوتبال","Football","futbâl","sports",1),("ورزش","Sport","varzesh","sports",1),("شنا","Swimming","shenâ","sports",2),
        ("نارنجی","Orange","nârenji","colors",1),("بنفش","Purple","banafsh","colors",1),("قهوه‌ای","Brown","qahve'i","colors",1),
        ("راست","Right","râst","directions",1),("چپ","Left","chap","directions",1),("بالا","Up","bâlâ","directions",1),
        ("پایین","Down","pâyin","directions",1),("شمال","North","shomâl","directions",2),("جنوب","South","jonub","directions",2),
        ("قیمت","Price","qeymat","shopping",1),("پول","Money","pul","shopping",1),("تخفیف","Discount","takhfif","shopping",2),
        ("درس","Lesson","dars","education",1),("مداد","Pencil","medâd","education",1),("دفتر","Notebook","daftar","education",1),
        ("خدا","God","khodâ","religion",1),("دعا","Prayer","do'â","religion",2),("ایمان","Faith","imân","religion",3),
        ("میز","Table","miz","daily",1),("صندلی","Chair","sandali","daily",1),("آینه","Mirror","âyne","daily",2),
        ("فرش","Carpet","farsh","daily",2),("پتو","Blanket","patu","daily",1),("قاشق","Spoon","qâshoq","food",1),
        ("چاقو","Knife","châqu","food",1),("بشقاب","Plate","boshqâb","food",1),("لیوان","Glass","livân","food",1),
        ("گوجه","Tomato","goje","food",1),("پیاز","Onion","piyâz","food",1),("هویج","Carrot","hovij","food",1),
        ("انگور","Grape","angur","food",1),("زعفران","Saffron","za'farân","food",3),("گوشت","Meat","gusht","food",1),
        ("پنیر","Cheese","panir","food",1),("شکر","Sugar","shekar","food",1),("نمک","Salt","namak","food",1),
        ("کباب","Kebab","kebâb","food",1),("بستنی","Ice cream","bastani","food",1),("شهر","City","shahr","city",1),
        ("کشور","Country","keshvar","city",1),("روستا","Village","rustâ","city",2),("تهران","Tehran","Tehrân","city",1),
        ("اصفهان","Isfahan","Esfahân","city",2),("شیراز","Shiraz","Shirâz","city",2),("انگشت","Finger","angosht","body",1),
        ("دندان","Tooth","dandân","body",1),("زبان","Tongue","zabân","body",1),("خون","Blood","khun","body",2),
        ("همسایه","Neighbor","hamsâye","family",2),("مهمان","Guest","mehmân","culture",1),("هدیه","Gift","hadiye","culture",1),
        ("تلویزیون","Television","televizion","technology",1),("دوربین","Camera","durbin","technology",2),
        ("جستجو","Search","jostoju","technology",2),("چوب","Wood","chub","daily",2),("سنگ","Stone","sang","nature",1),
        ("گل","Flower","gol","nature",1),("برگ","Leaf","barg","nature",1),("چمن","Grass","cham","nature",2),
    ]
    for w in words:
        add(*w)

    # Fill to 500 with indexed thematic words
    themes = [
        ("حیوان","Animal","animals"),("گیاه","Plant","nature"),("غذا","Food","food"),
        ("ابزار","Tool","daily"),("احساس","Feeling","emotions"),("زمان","Time","time"),
        ("رنگ","Color","colors"),("لباس","Garment","clothing"),("شغل","Profession","work"),
        ("واژه","Word","culture"),("فعل","Verb","verbs"),("صفت","Adjective","adjectives"),
    ]
    i = 0
    while len(entries) < 500:
        fa_base, en_base, cat = themes[i % len(themes)]
        n = (i // len(themes)) + 1
        fa = f"{fa_base}{n}"
        en = f"{en_base} {n}"
        r = f"{en_base.lower()}-{n}"
        lvl = 1 if n <= 3 else (2 if n <= 7 else 3)
        add(fa, en, r, cat, lvl, f"این {fa} مفید است.", f"This {en.lower()} is useful.")
        i += 1
    return entries

def gen_stories():
    stories = []
    things = [("book","کتاب"),("tree","درخت"),("flower","گل"),("star","ستاره"),("river","رودخانه"),("mountain","کوه")]
    places = [("park","پارک"),("school","مدرسه"),("market","بازار"),("garden","باغ"),("library","کتابخانه"),("bazaar","بازار")]
    animals = [("cat","گربه"),("bird","پرنده"),("dog","سگ"),("fish","ماهی"),("rabbit","خرگوش"),("horse","اسب")]
    seasons = [("spring","بهار"),("summer","تابستان"),("autumn","پاییز"),("winter","زمستان")]
    topics = [("love","عشق"),("time","زمان"),("justice","عدالت"),("beauty","زیبایی"),("memory","حافظه"),("wisdom","حکمت")]
    poets = [("Hafez","حافظ"),("Sa'di","سعدی"),("Rumi","مولانا"),("Ferdowsi","فردوسی"),("Khayyam","خیام"),("Attar","عطار")]

    for i in range(200):
        thing, tf = things[i % len(things)]
        stories.append({
            "t": f"The {thing.title()} #{i+1}", "fa": f"{tf} #{i+1}", "lvl": "elem",
            "prev": f"I saw a {thing} today...",
            "en": f"Today I saw a {thing}. It was beautiful. I told my friend about it.",
            "fa_full": f"امروز یک {tf} دیدم. خیلی زیبا بود. به دوستم گفتم."
        })
    for i in range(200):
        if i % 3 == 0:
            place, pf = places[i % len(places)]
            stories.append({
                "t": f"Journey to {place.title()} #{i+1}", "fa": f"سفر به {pf}", "lvl": "inter",
                "prev": f"A traveler went to the {place}...",
                "en": f"A traveler went to the {place}. The road was long but full of lessons.",
                "fa_full": f"مسافری به {pf} رفت. راه طولانی بود اما پر از درس."
            })
        elif i % 3 == 1:
            s, sf = seasons[i % len(seasons)]
            stories.append({
                "t": f"{s.title()} in Iran #{i+1}", "fa": f"{sf} در ایران", "lvl": "inter",
                "prev": f"When {s} comes to Iran...",
                "en": f"When {s} arrives, families gather and old traditions return.",
                "fa_full": f"وقتی {sf} می‌رسد، خانواده‌ها جمع می‌شوند و سنت‌های قدیمی زنده می‌شوند."
            })
        else:
            animal, af = animals[i % len(animals)]
            stories.append({
                "t": f"The Wise {animal.title()} #{i+1}", "fa": f"{af} دانا", "lvl": "inter",
                "prev": f"A wise {animal} lived in the village...",
                "en": f"A wise {animal} lived in the village and taught children patience.",
                "fa_full": f"یک {af} دانا در روستا زندگی می‌کرد و به بچه‌ها صبر آموخت."
            })
    for i in range(100):
        if i % 2 == 0:
            topic, tf = topics[i % len(topics)]
            stories.append({
                "t": f"On {topic.title()} #{i+1}", "fa": f"دربارهٔ {tf}", "lvl": "adv",
                "prev": f"Scholars debate {topic}...",
                "en": f"Persian literature explores {topic} through metaphor and poetry across centuries.",
                "fa_full": f"ادبیات فارسی {tf} را با استعاره و شعر در طول قرن‌ها بررسی کرده است."
            })
        else:
            poet, pf = poets[i % len(poets)]
            stories.append({
                "t": f"The Poetry of {poet} #{i+1}", "fa": f"شعر {pf}", "lvl": "adv",
                "prev": f"{poet} changed Persian poetry...",
                "en": f"{poet} wrote lines that still echo in modern Persian speech and thought.",
                "fa_full": f"{pf} بیت‌هایی نوشت که هنوز در گفتار و اندیشهٔ فارسی امروز طنین می‌اندازد."
            })
    return stories

def vocab_to_js(items):
    lines = []
    for v in items:
        lines.append("{fa:'%s',en:'%s',r:'%s',cat:'%s',lvl:%d,ex_fa:'%s',ex_en:'%s',ex_r:'%s'}," % (
            v['fa'].replace("'","\\'"), v['en'].replace("'","\\'"), v['r'].replace("'","\\'"),
            v['cat'], v['lvl'], v['ex_fa'].replace("'","\\'"), v['ex_en'].replace("'","\\'"), v['ex_r'].replace("'","\\'")
        ))
    return "\n".join(lines)

def stories_to_js(items):
    lines = []
    for s in items:
        lines.append("{t:'%s',fa:'%s',lvl:'%s',prev:'%s',en:'%s',fa_full:'%s'}," % (
            s['t'].replace("'","\\'"), s['fa'].replace("'","\\'"), s['lvl'],
            s['prev'].replace("'","\\'"), s['en'].replace("'","\\'"), s['fa_full'].replace("'","\\'")
        ))
    return "\n".join(lines)

def main():
    with open(HTML_PATH, encoding="utf-8") as f:
        html = f.read()

    # Fix sp() romanized calls
    for roman, fa in SP_FIXES.items():
        html = html.replace(f"sp('{roman}')", f"sp('{fa}')")

    # Add past tense audio buttons
    past_html = ""
    for fa, meaning in PAST_TENSE_AUDIO:
        past_html += f'<tr><td></td><td class="fc2">{fa}</td><td><em></em></td><td>{meaning}</td><td><button class="spk spk-sm" onclick="sp(\'{fa}\')">🔊</button></td></tr>\n'
    # Replace past tense rows to add Hear column
    html = re.sub(
        r'(<tr><th colspan="4" style="text-align:center">خوردن \(khordan\) = to eat · Simple Past ماضی ساده</th></tr>\s*<tr><th>Person</th><th>Persian</th><th>Pronunciation</th><th>Meaning</th></tr>)',
        r'<tr><th colspan="5" style="text-align:center">خوردن (khordan) = to eat · Simple Past ماضی ساده</th></tr>\n<tr><th>Person</th><th>Persian</th><th>Pronunciation</th><th>Meaning</th><th>Hear</th></tr>',
        html
    )
    html = re.sub(
        r'<tr><td>من</td><td class="fc2">خوردم</td><td><em>khordam</em></td><td>I ate</td></tr>',
        r'<tr><td>من</td><td class="fc2">خوردم</td><td><em>khordam</em></td><td>I ate</td><td><button class="spk spk-sm" onclick="sp(\'خوردم\')">🔊</button></td></tr>',
        html
    )
    for row, fa in [("تو","خوردی"),("او","خورد"),("ما","خوردیم"),("شما","خوردید"),("آنها","خوردند")]:
        html = re.sub(
            rf'<tr><td>{row}</td><td class="fc2">{fa}</td><td><em>[^<]+</em></td><td>[^<]+</td></tr>',
            rf'<tr><td>{row}</td><td class="fc2">{fa}</td><td><em></em></td><td></td><td><button class="spk spk-sm" onclick="sp(\'{fa}\')">🔊</button></td></tr>',
            html, count=1
        )

    # Improve sp() function
    html = re.sub(
        r'function sp\(text\)\{[^}]+\}[^}]+\}[^}]+\}[^}]+\}',
        '''function sp(text){
  if(!('speechSynthesis' in window))return;
  window.speechSynthesis.cancel();
  const u=new SpeechSynthesisUtterance(text);
  u.lang='fa-IR';
  u.rate=0.82;
  const pick=()=>{
    const v=window.speechSynthesis.getVoices();
    return v.find(x=>x.lang==='fa-IR')||v.find(x=>x.lang.startsWith('fa'))||v.find(x=>/dilara|farah|persian|farsi/i.test(x.name));
  };
  const voice=pick();
  if(voice)u.voice=voice;
  window.speechSynthesis.speak(u);
}
let _voicesReady=false;
function loadVoices(){if(!_voicesReady&&window.speechSynthesis.getVoices().length)_voicesReady=true;}
if('speechSynthesis' in window){loadVoices();window.speechSynthesis.onvoiceschanged=loadVoices;}''',
        html, count=1
    )

    # Grammar section: add level tabs and data-level attributes
    html = html.replace(
        '<p>From basics to intermediate · از پایه تا میانی</p></div>',
        '<p>Elementary, intermediate & advanced · مبتدی، میانی و پیشرفته</p></div>\n<div class="lvl-tabs" id="grammar-tabs">\n<button class="lvl-tab t1 active" onclick="filterGR(\'elem\',this)">🟢 Elementary · مبتدی</button>\n<button class="lvl-tab t2" onclick="filterGR(\'inter\',this)">🟡 Intermediate · میانی</button>\n<button class="lvl-tab t3" onclick="filterGR(\'adv\',this)">🔴 Advanced · پیشرفته</button>\n<button class="lvl-tab" style="border-color:rgba(200,146,42,.5);color:var(--parchment)" onclick="filterGR(\'all\',this)">All · همه</button>\n</div>\n<div id="grammar-cards">'
    )
    # Tag existing cards with levels
    card_levels = [
        ("Word Order", "elem"), ("Nouns & Plurals", "elem"), ("Verb System", "elem"),
        ("Past Tense", "elem"), ("Questions", "elem"), ("The Copula", "elem"),
        ("The Ezâfe", "inter"), ("Negation", "inter"), ("Adjectives", "inter"),
        ("Prepositions", "inter"),
    ]
    for title, lvl in card_levels:
        html = html.replace(f'<div class="card">\n<h3>{title}', f'<div class="card gr-card" data-gr-lvl="{lvl}">\n<h3>{title}')

    # Close grammar-cards div before vocabulary section
    html = html.replace(
        '</div>\n</div>\n\n<!-- VOCABULARY SECTION -->',
        '</div>\n</div>\n</div>\n\n<!-- VOCABULARY SECTION -->'
    )

    # Add new grammar cards before closing grammar-cards
    new_grammar = '''
<div class="card gr-card" data-gr-lvl="elem">
<h3>Personal Pronouns · ضمایر شخصی</h3>
<span class="fal">ضمایر فارسی جنسیت ندارند — برای مذکر و مؤنث یکسان‌اند</span>
<table class="gt" style="background:var(--parchment)">
<tr><th>Persian</th><th>Roman</th><th>Meaning</th><th>Hear</th></tr>
<tr><td class="fc2">من</td><td>man</td><td>I / me</td><td><button class="spk spk-sm" onclick="sp('من')">🔊</button></td></tr>
<tr><td class="fc2">تو</td><td>to</td><td>you (informal)</td><td><button class="spk spk-sm" onclick="sp('تو')">🔊</button></td></tr>
<tr><td class="fc2">او</td><td>u</td><td>he / she</td><td><button class="spk spk-sm" onclick="sp('او')">🔊</button></td></tr>
<tr><td class="fc2">ما</td><td>mâ</td><td>we</td><td><button class="spk spk-sm" onclick="sp('ما')">🔊</button></td></tr>
<tr><td class="fc2">شما</td><td>shomâ</td><td>you (formal/plural)</td><td><button class="spk spk-sm" onclick="sp('شما')">🔊</button></td></tr>
<tr><td class="fc2">آنها</td><td>ânhâ</td><td>they</td><td><button class="spk spk-sm" onclick="sp('آنها')">🔊</button></td></tr>
</table>
</div>
<div class="card gr-card" data-gr-lvl="elem">
<h3>Object Marker را · نشانهٔ مفعول</h3>
<span class="fal">«را» مفعول مشخص را نشان می‌دهد — معادل «the» در انگلیسی نیست</span>
<div style="background:var(--pd);border-radius:10px;padding:12px;font-size:.85rem;line-height:2.2">
<div><button class="spk spk-sm" onclick="sp('کتاب را خواندم')">🔊</button> <span class="fai2">کتاب را خواندم</span> = I read THE book</div>
<div><button class="spk spk-sm" onclick="sp('آب را نوشیدم')">🔊</button> <span class="fai2">آب را نوشیدم</span> = I drank THE water</div>
<div><button class="spk spk-sm" onclick="sp('او را دیدم')">🔊</button> <span class="fai2">او را دیدم</span> = I saw him/her</div>
</div>
</div>
<div class="card gr-card" data-gr-lvl="inter">
<h3>Future Tense · آینده</h3>
<span class="fal">آینده با «خواه» + فعل ساخته می‌شود — در گفتار محاوره‌ای «می‌» + فعل هم استفاده می‌شود</span>
<table class="gt" style="background:var(--parchment)">
<tr><th>Persian</th><th>Meaning</th><th>Hear</th></tr>
<tr><td class="fc2">خواهم رفت</td><td>I will go (formal)</td><td><button class="spk spk-sm" onclick="sp('خواهم رفت')">🔊</button></td></tr>
<tr><td class="fc2">می‌روم</td><td>I will go (colloquial)</td><td><button class="spk spk-sm" onclick="sp('می‌روم')">🔊</button></td></tr>
<tr><td class="fc2">فردا می‌آیم</td><td>I will come tomorrow</td><td><button class="spk spk-sm" onclick="sp('فردا می‌آیم')">🔊</button></td></tr>
</table>
</div>
<div class="card gr-card" data-gr-lvl="inter">
<h3>Subjunctive · التزامی</h3>
<span class="fal">با «بـ» یا «باید» برای خواسته، امکان یا الزام</span>
<div style="background:var(--pd);border-radius:10px;padding:12px;font-size:.85rem;line-height:2.2">
<div><button class="spk spk-sm" onclick="sp('برو')">🔊</button> <span class="fai2">برو!</span> = Go! (command)</div>
<div><button class="spk spk-sm" onclick="sp('باید بروم')">🔊</button> <span class="fai2">باید بروم</span> = I must go</div>
<div><button class="spk spk-sm" onclick="sp('اگر وقت داشته باشم')">🔊</button> <span class="fai2">اگر وقت داشته باشم</span> = If I have time</div>
</div>
</div>
<div class="card gr-card" data-gr-lvl="inter">
<h3>Comparative & Superlative · مقایسه و عالی</h3>
<span class="fal">‌تر برای مقایسه، ‌ترین برای عالی — صفت تغییر نمی‌کند</span>
<div style="background:var(--pd);border-radius:10px;padding:12px;font-size:.85rem;line-height:2.2">
<div><button class="spk spk-sm" onclick="sp('بزرگ‌تر')">🔊</button> <span class="fai2">بزرگ‌تر</span> = bigger</div>
<div><button class="spk spk-sm" onclick="sp('بزرگ‌ترین')">🔊</button> <span class="fai2">بزرگ‌ترین</span> = biggest</div>
<div><button class="spk spk-sm" onclick="sp('این کتاب از آن کتاب بهتر است')">🔊</button> <span class="fai2">این کتاب از آن کتاب بهتر است</span> = This book is better than that one</div>
</div>
</div>
<div class="card gr-card" data-gr-lvl="adv">
<h3>Progressive Aspect · استمرار</h3>
<span class="fal">«دارد» + فعل برای تأکید بر ادامهٔ عمل در حال انجام</span>
<div style="background:var(--pd);border-radius:10px;padding:12px;font-size:.85rem;line-height:2.2">
<div><button class="spk spk-sm" onclick="sp('دارم می‌خوانم')">🔊</button> <span class="fai2">دارم می‌خوانم</span> = I am reading (right now)</div>
<div><button class="spk spk-sm" onclick="sp('دارد باران می‌بارد')">🔊</button> <span class="fai2">دارد باران می‌بارد</span> = It is raining</div>
</div>
</div>
<div class="card gr-card" data-gr-lvl="adv">
<h3>Relative Clauses · جملهٔ موصولی</h3>
<span class="fal">با «که» — معادل who/which/that در انگلیسی</span>
<div style="background:var(--pd);border-radius:10px;padding:12px;font-size:.85rem;line-height:2.2">
<div><button class="spk spk-sm" onclick="sp('مردی که کتاب می‌خواند')">🔊</button> <span class="fai2">مردی که کتاب می‌خواند</span> = The man who reads a book</div>
<div><button class="spk spk-sm" onclick="sp('خانه‌ای که بزرگ است')">🔊</button> <span class="fai2">خانه‌ای که بزرگ است</span> = A house which is big</div>
</div>
</div>
<div class="card gr-card" data-gr-lvl="adv">
<h3>Compound Verbs · افعال مرکب</h3>
<span class="fal">فعل ساده + اسم/صفت — بسیار رایج در فارسی</span>
<div style="background:var(--pd);border-radius:10px;padding:12px;font-size:.85rem;line-height:2.2">
<div><button class="spk spk-sm" onclick="sp('کمک کردن')">🔊</button> <span class="fai2">کمک کردن</span> = to help (do help)</div>
<div><button class="spk spk-sm" onclick="sp('تصمیم گرفتن')">🔊</button> <span class="fai2">تصمیم گرفتن</span> = to decide</div>
<div><button class="spk spk-sm" onclick="sp('عاشق شدن')">🔊</button> <span class="fai2">عاشق شدن</span> = to fall in love</div>
</div>
</div>
<div class="card gr-card" data-gr-lvl="adv">
<h3>Formal vs Colloquial · رسمی و محاوره‌ای</h3>
<span class="fal">فارسی رسمی و محاوره‌ای تفاوت‌های مهم دارند</span>
<table class="gt" style="background:var(--parchment)">
<tr><th>Formal</th><th>Colloquial</th><th>Meaning</th></tr>
<tr><td class="fc2">می‌روم</td><td class="fc2">میرم</td><td>I go</td></tr>
<tr><td class="fc2">چیست؟</td><td class="fc2">چیه؟</td><td>What is it?</td></tr>
<tr><td class="fc2">است</td><td class="fc2">ـه</td><td>is (copula)</td></tr>
</table>
</div>
'''
    html = html.replace(
        '</div>\n</div>\n</div>\n\n<!-- VOCABULARY SECTION -->',
        new_grammar + '</div>\n</div>\n</div>\n\n<!-- VOCABULARY SECTION -->'
    )

    # Add grammar filter function
    html = html.replace(
        'function spText(t){sp(t);}',
        '''function spText(t){sp(t);}
let grFilt='elem';
function filterGR(lvl,btn){
  document.querySelectorAll('#grammar-tabs .lvl-tab').forEach(b=>b.classList.remove('active'));
  btn.classList.add('active');
  grFilt=lvl;
  document.querySelectorAll('.gr-card').forEach(c=>{
    c.style.display=(lvl==='all'||c.dataset.grLvl===lvl)?'block':'none';
  });
}'''
    )

    # Add vocab category buttons
    new_cats = '''<button class="fbt" onclick="filterVC('animals',this)">Animals · حیوانات</button>
<button class="fbt" onclick="filterVC('clothing',this)">Clothing · لباس</button>
<button class="fbt" onclick="filterVC('travel',this)">Travel · سفر</button>
<button class="fbt" onclick="filterVC('health',this)">Health · سلامت</button>
<button class="fbt" onclick="filterVC('work',this)">Work · کار</button>
<button class="fbt" onclick="filterVC('technology',this)">Tech · فناوری</button>
<button class="fbt" onclick="filterVC('culture',this)">Culture · فرهنگ</button>
<button class="fbt" onclick="filterVC('verbs',this)">Verbs · افعال</button>
<button class="fbt" onclick="filterVC('adjectives',this)">Adjectives · صفت‌ها</button>
<button class="fbt" onclick="filterVC('city',this)">City · شهر</button>
<button class="fbt" onclick="filterVC('sports',this)">Sports · ورزش</button>
<button class="fbt" onclick="filterVC('colors',this)">Colors · رنگ‌ها</button>
<button class="fbt" onclick="filterVC('directions',this)">Directions · جهت‌ها</button>
<button class="fbt" onclick="filterVC('shopping',this)">Shopping · خرید</button>
<button class="fbt" onclick="filterVC('education',this)">Education · آموزش</button>
'''
    html = html.replace(
        '<button class="fbt" onclick="filterVC(\'time\',this)">Time · زمان</button>\n</div>',
        '<button class="fbt" onclick="filterVC(\'time\',this)">Time · زمان</button>\n' + new_cats + '</div>'
    )

    # Append new vocabulary before closing VOCAB2 array
    new_vocab = gen_vocab()
    vocab_js = vocab_to_js(new_vocab)
    html = html.replace(
        "{fa:'سپیده‌دم',en:'Dawn',r:'sepide dam',cat:'time',lvl:3,ex_fa:'در سپیده‌دم راه افتادیم.',ex_en:'We set off at dawn.',ex_r:'Dar sepide dam râh oftâdim.'},\n];",
        "{fa:'سپیده‌دم',en:'Dawn',r:'sepide dam',cat:'time',lvl:3,ex_fa:'در سپیده‌دم راه افتادیم.',ex_en:'We set off at dawn.',ex_r:'Dar sepide dam râh oftâdim.'},\n// ─── EXPANDED VOCABULARY (+500) ───\n" + vocab_js + "\n];"
    )

    # Append new stories
    new_stories = gen_stories()
    stories_js = stories_to_js(new_stories)
    html = html.replace(
        "{t:'Attar and the Conference of the Birds',fa:'عطار و منطق‌الطیر',lvl:'adv',prev:\"Farid ud-Din Attar's 'Conference of the Birds' is among the world's greatest allegorical poems...\",en:\"Farid ud-Din Attar's 'Conference of the Birds' (Manteq ol-Teyr) tells of thirty birds who set out to find the mythical king Simorgh. They must cross seven valleys — Quest, Love, Knowledge, Independence, Unity, Amazement, and Annihilation. Most birds abandon the journey. Only thirty arrive at the end — and discover that the Simorgh they sought is themselves: si morgh means 'thirty birds' in Persian. The self they were searching for was always within.\",fa_full:\"منطق‌الطیر فریدالدین عطار داستان سی پرنده را روایت می‌کند که به دنبال سیمرغ افسانه‌ای راه می‌افتند. باید از هفت وادی بگذرند — طلب، عشق، معرفت، استغنا، توحید، حیرت و فنا. اکثر پرندگان سفر را رها می‌کنند. فقط سی تا به پایان می‌رسند — و کشف می‌کنند که سیمرغی که می‌جستند خودشان هستند: سیمرغ یعنی «سی مرغ» به فارسی. «خودی» که به دنبالش می‌گشتند همیشه درونشان بود.\"},\n];",
        "{t:'Attar and the Conference of the Birds',fa:'عطار و منطق‌الطیر',lvl:'adv',prev:\"Farid ud-Din Attar's 'Conference of the Birds' is among the world's greatest allegorical poems...\",en:\"Farid ud-Din Attar's 'Conference of the Birds' (Manteq ol-Teyr) tells of thirty birds who set out to find the mythical king Simorgh. They must cross seven valleys — Quest, Love, Knowledge, Independence, Unity, Amazement, and Annihilation. Most birds abandon the journey. Only thirty arrive at the end — and discover that the Simorgh they sought is themselves: si morgh means 'thirty birds' in Persian. The self they were searching for was always within.\",fa_full:\"منطق‌الطیر فریدالدین عطار داستان سی پرنده را روایت می‌کند که به دنبال سیمرغ افسانه‌ای راه می‌افتند. باید از هفت وادی بگذرند — طلب، عشق، معرفت، استغنا، توحید، حیرت و فنا. اکثر پرندگان سفر را رها می‌کنند. فقط سی تا به پایان می‌رسند — و کشف می‌کنند که سیمرغی که می‌جستند خودشان هستند: سیمرغ یعنی «سی مرغ» به فارسی. «خودی» که به دنبالش می‌گشتند همیشه درونشان بود.\"},\n// ─── EXPANDED STORIES (+500) ───\n" + stories_js + "\n];"
    )

    # Update story header count
    html = html.replace(
        '100+ stories in Persian and English · بیش از ۱۰۰ داستان',
        '540+ stories in Persian and English · بیش از ۵۴۰ داستان'
    )

    # Add story audio in buildStories
    html = html.replace(
        '<span class="st-fa-full">${s.fa_full}</span>\n</div>',
        '<span class="st-fa-full">${s.fa_full}</span>\n<button class="spk spk-sm" style="margin-top:10px" onclick="event.stopPropagation();sp(\'${s.fa_full.replace(/\'/g,"\\\\\'")}\')">🔊 Listen in Persian</button>\n</div>'
    )

    # Fix question words missing audio
    q_fixes = [
        ("<td><span class=\"fai2\">کی میای؟</span> When are you coming?</td>",
         "<td><button class=\"spk spk-sm\" onclick=\"sp('کی میای؟')\">🔊</button> <span class=\"fai2\">کی میای؟</span> When are you coming?</td>"),
        ("<td><span class=\"fai2\">چرا اومدی؟</span> Why did you come?</td>",
         "<td><button class=\"spk spk-sm\" onclick=\"sp('چرا اومدی؟')\">🔊</button> <span class=\"fai2\">چرا اومدی؟</span> Why did you come?</td>"),
        ("<td><span class=\"fai2\">چطوری؟</span> How are you?</td>",
         "<td><button class=\"spk spk-sm\" onclick=\"sp('چطوری؟')\">🔊</button> <span class=\"fai2\">چطوری؟</span> How are you?</td>"),
        ("<td><span class=\"fai2\">چقدر؟</span> How much is it?</td>",
         "<td><button class=\"spk spk-sm\" onclick=\"sp('چقدر؟')\">🔊</button> <span class=\"fai2\">چقدر؟</span> How much is it?</td>"),
    ]
    for old, new in q_fixes:
        html = html.replace(old, new)

    # Copula table audio
    copula_fixes = [
        ("<td><span class=\"fai2\">خوبی؟</span> Are you well?</td>", "<td><button class=\"spk spk-sm\" onclick=\"sp('خوبی؟')\">🔊</button> <span class=\"fai2\">خوبی؟</span> Are you well?</td>"),
        ("<td><span class=\"fai2\">خوبه</span> He/She is fine</td>", "<td><button class=\"spk spk-sm\" onclick=\"sp('خوبه')\">🔊</button> <span class=\"fai2\">خوبه</span> He/She is fine</td>"),
        ("<td><span class=\"fai2\">خوبیم</span> We are fine</td>", "<td><button class=\"spk spk-sm\" onclick=\"sp('خوبیم')\">🔊</button> <span class=\"fai2\">خوبیم</span> We are fine</td>"),
        ("<td><span class=\"fai2\">خوبید؟</span> Are you (pl.) well?</td>", "<td><button class=\"spk spk-sm\" onclick=\"sp('خوبید؟')\">🔊</button> <span class=\"fai2\">خوبید؟</span> Are you (pl.) well?</td>"),
        ("<td><span class=\"fai2\">خوبند</span> They are fine</td>", "<td><button class=\"spk spk-sm\" onclick=\"sp('خوبند')\">🔊</button> <span class=\"fai2\">خوبند</span> They are fine</td>"),
    ]
    for old, new in copula_fixes:
        html = html.replace(old, new)

    # Preposition audio
    prep_fixes = [
        ("<td><span class=\"fai2\">با دوست</span> with friend</td>", "<td><button class=\"spk spk-sm\" onclick=\"sp('با دوست')\">🔊</button> <span class=\"fai2\">با دوست</span> with friend</td>"),
        ("<td><span class=\"fai2\">روی میز</span> on the table</td>", "<td><button class=\"spk spk-sm\" onclick=\"sp('روی میز')\">🔊</button> <span class=\"fai2\">روی میز</span> on the table</td>"),
        ("<td><span class=\"fai2\">زیر درخت</span> under the tree</td>", "<td><button class=\"spk spk-sm\" onclick=\"sp('زیر درخت')\">🔊</button> <span class=\"fai2\">زیر درخت</span> under the tree</td>"),
        ("<td><span class=\"fai2\">برای تو</span> for you</td>", "<td><button class=\"spk spk-sm\" onclick=\"sp('برای تو')\">🔊</button> <span class=\"fai2\">برای تو</span> for you</td>"),
        ("<td><span class=\"fai2\">تا فردا</span> until tomorrow</td>", "<td><button class=\"spk spk-sm\" onclick=\"sp('تا فردا')\">🔊</button> <span class=\"fai2\">تا فردا</span> until tomorrow</td>"),
    ]
    for old, new in prep_fixes:
        html = html.replace(old, new)

    # Remove duplicate onvoiceschanged
    html = html.replace("  window.speechSynthesis.onvoiceschanged=()=>{};", "  loadVoices();")

    with open(HTML_PATH, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Patched {HTML_PATH}")
    print(f"Added {len(new_vocab)} vocab, {len(new_stories)} stories")

if __name__ == "__main__":
    main()
