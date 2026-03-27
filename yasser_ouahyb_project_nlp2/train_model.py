import json
import joblib
import numpy as np
import os
import warnings

warnings.filterwarnings('ignore')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def main():
    print("=" * 60)
    print("🚀 Enhanced TF-IDF Training Pipeline")
    print("=" * 60)

    # ── 1. Load intents.json ───────────────────────────────────
    print("\n[1/4] Loading intents.json...")
    intents_path = os.path.join(BASE_DIR, 'data', 'intents.json')
    with open(intents_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    X, y = [], []
    responses = {}

    for intent in data['intents']:
        tag = intent['tag']
        responses[tag] = intent['responses']
        for pattern in intent['patterns']:
            X.append(pattern)
            y.append(tag)

    print(f"      ✔️  {len(X)} patterns from {len(responses)} intents.")

    # ── 2. Load formations.json → auto-generate patterns ───────
    print("\n[2/4] Loading formations.json and generating patterns...")
    formations_path = os.path.join(BASE_DIR, 'static', 'formations.json')
    with open(formations_path, 'r', encoding='utf-8') as f:
        formations = json.load(f)

    added = 0
    for f in formations:
        titre_fr = f['titre']['fr']
        titre_ar = f['titre']['ar']
        sect_fr  = f['secteur']['fr']
        sect_ar  = f['secteur']['ar']

        auto_patterns = [
            # French
            f"formation {titre_fr}",
            f"filière {titre_fr}",
            f"formations en {sect_fr}",
            f"formations {sect_fr}",
            f"qu'est-ce que {titre_fr}",
            f"je veux faire {titre_fr}",
            # Arabic
            f"شنو تكوين {titre_ar}",
            f"شعبة {titre_ar}",
            f"تكوينات في {sect_ar}",
            f"شنو شعب {sect_ar}",
            f"بغيت ندخل {titre_ar}",
            # English
            f"{titre_fr} program",
            f"training in {sect_fr}",
            f"what is {titre_fr}",
        ]
        for p in auto_patterns:
            X.append(p)
            y.append('formations')
            added += 1

    print(f"      ✔️  Added {added} auto-patterns from {len(formations)} formations.")
    print(f"      ✔️  Total training samples: {len(X)}")

    # ── 3. Train Enhanced TF-IDF Pipeline ─────────────────────
    print("\n[3/4] Training enhanced TF-IDF + SVM model...")
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.svm import LinearSVC
    from sklearn.pipeline import make_pipeline
    from sklearn.calibration import CalibratedClassifierCV
    from sklearn.model_selection import cross_val_score

    # Dual TF-IDF: word-level + character-level then concatenate
    from sklearn.pipeline import Pipeline, FeatureUnion

    pipeline = Pipeline([
        ('features', FeatureUnion([
            ('word_tfidf', TfidfVectorizer(
                analyzer='word',
                ngram_range=(1, 2),
                min_df=1,
                sublinear_tf=True,
            )),
            ('char_tfidf', TfidfVectorizer(
                analyzer='char_wb',
                ngram_range=(2, 4),
                min_df=1,
                sublinear_tf=True,
            )),
        ])),
        ('clf', CalibratedClassifierCV(LinearSVC(C=1.0, max_iter=2000), cv=3)),
    ])

    # Cross-validation accuracy
    cv_scores = cross_val_score(pipeline, X, y, cv=3, scoring='accuracy')
    print(f"      ✔️  Cross-validation accuracy: {cv_scores.mean():.2%} (±{cv_scores.std():.2%})")

    # Final fit on all data
    pipeline.fit(X, y)

    # ── 4. Save model and responses ───────────────────────────
    print("\n[4/4] Saving model and responses...")
    joblib.dump(pipeline, os.path.join(BASE_DIR, 'model.joblib'))
    with open(os.path.join(BASE_DIR, 'responses.json'), 'w', encoding='utf-8') as fout:
        json.dump(responses, fout, ensure_ascii=False, indent=2)

    print("      ✔️  'model.joblib' saved.")
    print("      ✔️  'responses.json' saved.")
    print("\n" + "=" * 60)
    print("✅ Done! Run: python app.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
