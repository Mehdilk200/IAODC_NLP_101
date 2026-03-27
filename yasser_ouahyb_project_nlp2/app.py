from flask import Flask, render_template, request, jsonify
import joblib
import json
import re
import os
import numpy as np

app = Flask(__name__)

# Base directory = folder where app.py lives
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# ─────────────────────────────────────────────
# Load Model & Data
# ─────────────────────────────────────────────
try:
    model = joblib.load(os.path.join(BASE_DIR, 'model.joblib'))
    print("✅ Model loaded.")
except Exception as e:
    print(f"❌ model.joblib not found: {e}")
    print("   → Run: python train_model.py first!")
    model = None

try:
    with open(os.path.join(BASE_DIR, 'responses.json'), 'r', encoding='utf-8') as f:
        responses_dict = json.load(f)
except Exception as e:
    print(f"❌ responses.json not found: {e}")
    responses_dict = {}

try:
    formations_path = os.path.join(BASE_DIR, 'static', 'formations.json')
    with open(formations_path, 'r', encoding='utf-8') as f:
        formations_data = json.load(f)
except Exception as e:
    print(f"Warning: formations.json not loaded → {e}")
    formations_data = []


# ─────────────────────────────────────────────
# Language Detection
# ─────────────────────────────────────────────
def detect_language(text):
    """Detect: 'ar' (Arabic/Darija), 'fr' (French), 'en' (English)."""

    # 1. Arabic unicode → always Arabic/Darija
    if re.search(r'[\u0600-\u06FF]', text):
        return 'ar'

    text_lower = text.lower()
    words = re.findall(r"[\w']+", text_lower)

    # 2. Darija written in Latin/Franco-Arab
    darija_keywords = {
        'salam', 'mrhba', 'marhba', 'labas', 'lbas', 'kidayr', 'kidayer',
        'wach', 'wash', 'kifach', 'kifash', 'fach', 'fash', 'mnin', 'fin',
        'imta', 'emta', 'chhal', 'chkon', 'chkoun', 'chno', 'chnoo', 'chnou',
        'bghit', 'bgha', 'nkdr', 'nqdr',
        'kayn', 'kayna', 'makaynch', 'dyal', 'dial', 'dyali',
        'zwina', 'mzyan', 'bzzaf', 'bezaf', 'mashi', 'wakha', 'iyeh',
        'rani', 'raho', 'rah', 'had', 'hado',
        'cmc', 'takwin', 'tkowin', 'ntsajal', 'nsjl', 'tsajal',
        'nwsal', 'nzid', 'nchof', 'nchouf',
        'chokran', 'choukran', 'bslama', 'beslama',
        '3arrafni', '3la', '9al', '3lach', 'b7al', 'l9it',
        'sbah', 'msa', 'lkhir',
    }
    if sum(1 for w in words if w in darija_keywords) >= 1:
        return 'ar'

    # 3. Try langdetect (optional — graceful fallback if not installed)
    try:
        from langdetect import detect
        detected = detect(text)
        if detected in ('fr', 'ar', 'en'):
            return detected
    except Exception:
        pass

    # 4. French keywords fallback
    french_keywords = {
        'je', 'tu', 'il', 'elle', 'nous', 'vous', 'ils', 'elles',
        'le', 'la', 'les', 'de', 'du', 'des', 'un', 'une',
        'est', 'sont', 'bonjour', 'bonsoir', 'salut',
        'comment', 'quand', 'pourquoi', 'quoi', 'quel', 'quelle',
        'avec', 'pour', 'dans', 'sur', 'mais', 'donc', 'combien',
    }
    if sum(1 for w in words if w in french_keywords) >= 1:
        return 'fr'

    return 'fr'  # safe default


def get_response_by_lang(responses, lang):
    """Pick response by language: ar→0, fr→1, en→2"""
    lang_index = {'ar': 0, 'fr': 1, 'en': 2}
    idx = lang_index.get(lang, 1)
    if idx < len(responses):
        return responses[idx]
    return responses[0]


def get_fallback_message(lang):
    messages = {
        'ar': "عذراً، ما فهمتش سؤالك مزيان. تقدر تعاود تصيغو بطريقة أخرى؟ 🤔",
        'fr': "Désolé, je n'ai pas compris votre question. Pouvez-vous reformuler ? 🤔",
        'en': "Sorry, I didn't understand. Could you rephrase your question? 🤔",
    }
    return messages.get(lang, messages['fr'])


# ─────────────────────────────────────────────
# Dynamic Formations Response Builder
# ─────────────────────────────────────────────
def get_formations_response(lang, user_message=''):
    if not formations_data:
        return get_fallback_message(lang)

    msg_lower = user_message.lower()

    sector_keywords = {
        'digital':    ['digital', 'raqmi', 'ديجيتال', 'الرقمي', 'الرقمية', 'web',
                       'programmation', 'برمجة', 'informatique', 'cyber', 'data', 'ia', 'ui', 'ux'],
        'industrie':  ['industrie', 'صناع', 'mécanique', 'mecanique', 'الصناعة',
                       'ميكانيك', 'كهروميك', 'automatisation'],
        'gestion':    ['gestion', 'commerce', 'تسيير', 'تجارة', 'comptabilité',
                       'marketing', 'finance', 'التسيير', 'محاسبة'],
        'tourisme':   ['tourisme', 'cuisine', 'سياح', 'hotel', 'restaurant', 'طبخ', 'السياحة'],
        'btp':        ['btp', 'bâtiment', 'batiment', 'génie civil', 'construction',
                       'بناء', 'أشغال', 'البناء'],
        'logistique': ['logistique', 'transport', 'supply chain', 'لوجستيك', 'نقل', 'اللوجستيك'],
    }

    matched_sector = None
    for sector, kws in sector_keywords.items():
        if any(kw in msg_lower for kw in kws):
            matched_sector = sector
            break

    if matched_sector:
        filtered = [
            f for f in formations_data
            if matched_sector in f.get('secteur', {}).get('fr', '').lower()
            or matched_sector in f.get('secteur', {}).get('ar', '').lower()
        ]
        if not filtered:
            filtered = formations_data
    else:
        filtered = formations_data

    titles_ar = '، '.join(f['titre']['ar'] for f in filtered)
    titles_fr = ', '.join(f['titre']['fr'] for f in filtered)
    count = len(filtered)
    sector_fr = filtered[0]['secteur']['fr'] if filtered else 'CMC'
    sector_ar = filtered[0]['secteur']['ar'] if filtered else 'CMC'

    if matched_sector:
        responses = {
            'ar': (
                f"فـ قطاع {sector_ar} 🎓 عندنا {count} تكوين:\n\n"
                f"📚 {titles_ar}\n\n"
                f"بغيتي تعرف أكثر على واحد منهم؟ سول ليا! 😊"
            ),
            'fr': (
                f"Dans le secteur {sector_fr} 🎓, nous proposons {count} formation(s) :\n\n"
                f"📚 {titles_fr}\n\n"
                f"Voulez-vous des détails sur l'une d'elles ? Demandez-moi ! 😊"
            ),
            'en': (
                f"In the {sector_fr} sector 🎓, we offer {count} program(s):\n\n"
                f"📚 {titles_fr}\n\n"
                f"Would you like details on one of them? Just ask! 😊"
            ),
        }
    else:
        responses = {
            'ar': (
                f"CMC Casablanca-Settat كتقدم {count} تكوين 🎓 في قطاعات متعددة:\n\n"
                f"📚 {titles_ar}\n\n"
                f"بغيتي تعرف تكوينات قطاع معين؟ قولي مثلاً: «شنو التكوينات ديال الديجيتال» 😊"
            ),
            'fr': (
                f"La CMC Casablanca-Settat propose {count} formations 🎓 dans plusieurs secteurs :\n\n"
                f"📚 {titles_fr}\n\n"
                f"Souhaitez-vous des détails sur un secteur ? Ex: «formations en Digital» 😊"
            ),
            'en': (
                f"CMC Casablanca-Settat offers {count} programs 🎓 across multiple sectors:\n\n"
                f"📚 {titles_fr}\n\n"
                f"Would you like details on a specific sector? E.g. «Digital programs» 😊"
            ),
        }
    return responses.get(lang, responses['fr'])


# ─────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/bot')
def bot():
    return render_template('bot.html')


@app.route('/orientation')
def orientation():
    return render_template('orientation.html')


@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"response": get_fallback_message('fr')})

    if model is None:
        return jsonify({"response": (
            "عذراً، النموذج غير جاهز. شغّل train_model.py أولاً.<br>"
            "Désolé, le modèle n'est pas prêt. Exécutez train_model.py.<br>"
            "Model not ready. Please run train_model.py first."
        )})

    # Detect language
    lang = detect_language(user_message)

    # Predict intent
    tag = model.predict([user_message])[0]

    # Confidence check via predict_proba
    try:
        probas = model.predict_proba([user_message])[0]
        max_proba = max(probas)
        if max_proba < 0.25:
            return jsonify({"response": get_fallback_message(lang)})
    except Exception:
        pass  # CalibratedClassifierCV always has predict_proba, but just in case

    # Dynamic formations handler
    if tag == 'formations':
        return jsonify({"response": get_formations_response(lang, user_message)})

    # Standard response from responses.json
    responses = responses_dict.get(tag, [])
    if not responses:
        return jsonify({"response": get_fallback_message(lang)})

    response = get_response_by_lang(responses, lang)
    return jsonify({"response": response})


@app.route('/api/feedback', methods=['POST'])
def feedback():
    """Handle feedback (thumbs up/down) without returning 404."""
    data = request.json
    print(f"Feedback received: {data.get('feedback')} for message ID: {data.get('message_id')}")
    # In a real app, you would save this to a database
    return jsonify({"status": "success"})


if __name__ == '__main__':
    app.run(debug=True, port=5000)
