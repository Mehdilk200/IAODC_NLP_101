import json
import os

new_data = {
  "secteurs": [
    {
      "id_secteur": 1,
      "secteur": "Industrie",
      "filieres": [
        {
          "id_filiere": 101,
          "code_filiere": "IND-GM",
          "nom": "Génie mécanique",
          "niveau": "Technicien Spécialisé",
          "duree": "2 ans",
          "description": "Conception et maintenance des systèmes mécaniques industriels.",
          "debouches": [
            "Technicien mécanique",
            "Responsable maintenance",
            "Technicien production industrielle"
          ]
        },
        {
          "id_filiere": 102,
          "code_filiere": "IND-MI",
          "nom": "Maintenance industrielle",
          "niveau": "Technicien",
          "duree": "2 ans",
          "description": "Maintenance et réparation des machines industrielles.",
          "debouches": [
            "Technicien maintenance",
            "Agent maintenance industrielle"
          ]
        },
        {
          "id_filiere": 103,
          "code_filiere": "IND-AUT",
          "nom": "Automatisation industrielle",
          "niveau": "Technicien Spécialisé",
          "duree": "2 ans",
          "description": "Programmation et gestion des systèmes automatisés.",
          "debouches": [
            "Technicien automatisme",
            "Technicien robotique"
          ]
        },
        {
          "id_filiere": 104,
          "code_filiere": "IND-MEC",
          "nom": "Mécatronique",
          "niveau": "Technicien Spécialisé",
          "duree": "2 ans",
          "description": "Combinaison de mécanique, électronique et informatique industrielle.",
          "debouches": [
            "Technicien mécatronique",
            "Technicien robotique"
          ]
        }
      ]
    },
    {
      "id_secteur": 2,
      "secteur": "Digital et Intelligence Artificielle",
      "filieres": [
        {
          "id_filiere": 201,
          "code_filiere": "DIG-WEB",
          "nom": "Développement Web Full Stack",
          "niveau": "Technicien Spécialisé",
          "duree": "2 ans",
          "description": "Développement d'applications web frontend et backend.",
          "debouches": [
            "Développeur web",
            "Développeur full stack",
            "Freelancer web"
          ]
        },
        {
          "id_filiere": 202,
          "code_filiere": "DIG-PYT",
          "nom": "Développement Python",
          "niveau": "Technicien Spécialisé",
          "duree": "2 ans",
          "description": "Programmation backend et data avec Python.",
          "debouches": [
            "Développeur Python",
            "Backend developer"
          ]
        },
        {
          "id_filiere": 203,
          "code_filiere": "DIG-CYB",
          "nom": "Cybersécurité",
          "niveau": "Technicien Spécialisé",
          "duree": "2 ans",
          "description": "Protection des systèmes informatiques et réseaux.",
          "debouches": [
            "Technicien cybersécurité",
            "Analyste sécurité informatique"
          ]
        },
        {
          "id_filiere": 204,
          "code_filiere": "DIG-UX",
          "nom": "UI / UX Design",
          "niveau": "Technicien",
          "duree": "2 ans",
          "description": "Design d'interfaces utilisateur pour applications web et mobile.",
          "debouches": [
            "UI designer",
            "UX designer",
            "Web designer"
          ]
        },
        {
          "id_filiere": 205,
          "code_filiere": "DIG-DATA",
          "nom": "Data & Business Intelligence",
          "niveau": "Technicien Spécialisé",
          "duree": "2 ans",
          "description": "Analyse et visualisation de données.",
          "debouches": [
            "Data analyst",
            "Business intelligence analyst"
          ]
        }
      ]
    },
    {
      "id_secteur": 3,
      "secteur": "Gestion et Commerce",
      "filieres": [
        {
          "id_filiere": 301,
          "code_filiere": "COM-GE",
          "nom": "Gestion des entreprises",
          "niveau": "Technicien",
          "duree": "2 ans",
          "description": "Gestion administrative et organisation des entreprises.",
          "debouches": [
            "Assistant administratif",
            "Gestionnaire PME"
          ]
        },
        {
          "id_filiere": 302,
          "code_filiere": "COM-CF",
          "nom": "Comptabilité et Finance",
          "niveau": "Technicien",
          "duree": "2 ans",
          "description": "Gestion financière et comptable.",
          "debouches": [
            "Comptable",
            "Assistant financier"
          ]
        },
        {
          "id_filiere": 303,
          "code_filiere": "COM-MD",
          "nom": "Marketing Digital",
          "niveau": "Technicien",
          "duree": "2 ans",
          "description": "Stratégies marketing sur internet et réseaux sociaux.",
          "debouches": [
            "Community manager",
            "Digital marketer"
          ]
        }
      ]
    },
    {
      "id_secteur": 4,
      "secteur": "Bâtiment et Travaux Publics",
      "filieres": [
        {
          "id_filiere": 401,
          "code_filiere": "BTP-GC",
          "nom": "Génie Civil",
          "niveau": "Technicien Spécialisé",
          "duree": "2 ans",
          "description": "Conception et suivi de projets de construction.",
          "debouches": [
            "Technicien génie civil",
            "Conducteur de travaux"
          ]
        },
        {
          "id_filiere": 402,
          "code_filiere": "BTP-DB",
          "nom": "Dessin Bâtiment",
          "niveau": "Technicien",
          "duree": "2 ans",
          "description": "Création de plans techniques de bâtiments.",
          "debouches": [
            "Dessinateur bâtiment",
            "Technicien DAO"
          ]
        }
      ]
    },
    {
      "id_secteur": 5,
      "secteur": "Transport et Logistique",
      "filieres": [
        {
          "id_filiere": 501,
          "code_filiere": "LOG-GL",
          "nom": "Gestion Logistique",
          "niveau": "Technicien",
          "duree": "2 ans",
          "description": "Gestion des flux de marchandises.",
          "debouches": [
            "Agent logistique",
            "Responsable stock"
          ]
        },
        {
          "id_filiere": 502,
          "code_filiere": "LOG-SCM",
          "nom": "Supply Chain Management",
          'niveau': 'Technicien Spécialisé',
          "duree": "2 ans",
          "description": "Gestion globale de la chaîne logistique.",
          "debouches": [
            "Supply chain analyst",
            "Responsable logistique"
          ]
        }
      ]
    }
  ]
}

ar_map = {
    'Industrie': 'الصناعة',
    'Digital et Intelligence Artificielle': 'الرقمية والذكاء الاصطناعي',
    'Gestion et Commerce': 'التسيير والتجارة',
    'Bâtiment et Travaux Publics': 'البناء والأشغال العمومية',
    'Transport et Logistique': 'النقل واللوجستيك',
    'Génie mécanique': 'الهندسة الميكانيكية',
    'Maintenance industrielle': 'الصيانة الصناعية',
    'Automatisation industrielle': 'الأتمتة الصناعية',
    'Mécatronique': 'الميكاترونيك',
    'Développement Web Full Stack': 'تطوير الويب المتكامل',
    'Développement Python': 'تطوير بايثون',
    'Cybersécurité': 'الأمن السيبراني',
    'UI / UX Design': 'تصميم واجهة المستخدم',
    'Data & Business Intelligence': 'البيانات وذكاء الأعمال',
    'Gestion des entreprises': 'تسيير المقاولات',
    'Comptabilité et Finance': 'المحاسبة والمالية',
    'Marketing Digital': 'التسويق الرقمي',
    'Génie Civil': 'الهندسة المدنية',
    'Dessin Bâtiment': 'رسم المباني',
    'Gestion Logistique': 'تسيير اللوجستيك',
    'Supply Chain Management': 'إدارة سلسلة التوريد',
    'Technicien': 'تقني',
    'Technicien Spécialisé': 'تقني متخصص',
    # Descriptions
    'Conception et maintenance des systèmes mécaniques industriels.': 'تصميم وصيانة الأنظمة الميكانيكية الصناعية.',
    'Maintenance et réparation des machines industrielles.': 'صيانة وإصلاح الآلات الصناعية.',
    'Programmation et gestion des systèmes automatisés.': 'برمجة وإدارة الأنظمة الآلية.',
    'Combinaison de mécanique, électronique et informatique industrielle.': 'مزيج من الميكانيكا، الإلكترونيات والمعلوماتية الصناعية.',
    'Développement d\'applications web frontend et backend.': 'تطوير تطبيقات الويب الأمامية والخلفية.',
    'Programmation backend et data avec Python.': 'برمجة الخلفية والبيانات باستخدام بايثون.',
    'Protection des systèmes informatiques et réseaux.': 'حماية أنظمة المعلومات والشبكات.',
    'Design d\'interfaces utilisateur pour applications web et mobile.': 'تصميم واجهات المستخدم لتطبيقات الويب والموبايل.',
    'Analyse et visualisation de données.': 'تحليل وتصور البيانات.',
    'Gestion administrative et organisation des entreprises.': 'التسيير الإداري وتنظيم المقاولات.',
    'Gestion financière et comptable.': 'التسيير المالي والمحاسباتي.',
    'Stratégies marketing sur internet et réseaux sociaux.': 'استراتيجيات التسويق عبر الإنترنت والشبكات الاجتماعية.',
    'Conception et suivi de projets de construction.': 'تصميم وتتبع مشاريع البناء.',
    'Création de plans techniques de bâtiments.': 'إنشاء المخططات التقنية للمباني.',
    'Gestion des flux de marchandises.': 'تسيير تدفق السلع.',
    'Gestion globale de la chaîne logistique.': 'الإدارة الشاملة لسلسلة التوريد.',
    # Debouches
    'Technicien mécanique': 'تقني ميكانيك',
    'Responsable maintenance': 'مسؤول الصيانة',
    'Technicien production industrielle': 'تقني إنتاج صناعي',
    'Technicien maintenance': 'تقني صيانة',
    'Agent maintenance industrielle': 'عامل صيانة صناعية',
    'Technicien automatisme': 'تقني أتمتة',
    'Technicien robotique': 'تقني روبوتيك',
    'Technicien mécatronique': 'تقني ميكاترونيك',
    'Développeur web': 'مطور ويب',
    'Développeur full stack': 'مطور متكامل',
    'Freelancer web': 'مستقل في مجال الويب',
    'Développeur Python': 'مطور بايثون',
    'Backend developer': 'مطور خلفية',
    'Technicien cybersécurité': 'تقني أمن سيبراني',
    'Analyste sécurité informatique': 'محلل أمن معلوماتي',
    'UI designer': 'مصمم واجهات المستخدم',
    'UX designer': 'مصمم تجربة المستخدم',
    'Web designer': 'مصمم ويب',
    'Data analyst': 'محلل بيانات',
    'Business intelligence analyst': 'محلل ذكاء الأعمال',
    'Assistant administratif': 'مساعد إداري',
    'Gestionnaire PME': 'مسير مقاولة صغرى ومتوسطة',
    'Comptable': 'محاسب',
    'Assistant financier': 'مساعد مالي',
    'Community manager': 'مدير مجتمعات افتراضية',
    'Digital marketer': 'مسوق رقمي',
    'Technicien génie civil': 'تقني هندسة مدنية',
    'Conducteur de travaux': 'مشرف على الأشغال',
    'Dessinateur bâtiment': 'رسام مباني',
    'Technicien DAO': 'تقني تصميم مدعم بالحاسوب',
    'Agent logistique': 'عامل لوجستيك',
    'Responsable stock': 'مسؤول المخزون',
    'Supply chain analyst': 'محلل سلسلة التوريد',
    'Responsable logistique': 'مسؤول لوجستيك'
}

def translate_ar(text):
    return ar_map.get(text, text)

def translate_list(items):
    return [translate_ar(i) for i in items]

out_data = []

file_path = 'static/formations.json'
if os.path.exists(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        existing = json.load(f)
        out_data.extend(existing)

for s in new_data['secteurs']:
    secteur_name = s['secteur']
    for f in s['filieres']:
        entry = {
            'id': f['code_filiere'].lower(),
            'titre': {
                'fr': f['nom'],
                'ar': translate_ar(f['nom'])
            },
            'secteur': {
                'fr': secteur_name,
                'ar': translate_ar(secteur_name)
            },
            'niveau': {
                'fr': f['niveau'],
                'ar': translate_ar(f['niveau'])
            },
            'duree': '2 ans / سنتان',
            'programme': {
                'fr': '<p>' + f['description'] + '</p>',
                'ar': '<p>' + translate_ar(f['description']) + '</p>'
            },
            'debouches': {
                'fr': f['debouches'],
                'ar': translate_list(f['debouches'])
            }
        }
        # Update if exists to overwrite old data, else append
        existing_idx = next((i for i, e in enumerate(out_data) if e['id'] == entry['id']), -1)
        if existing_idx >= 0:
            out_data[existing_idx] = entry
        else:
            out_data.append(entry)

with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(out_data, f, ensure_ascii=False, indent=4)

print('Updated formations.json Successfully!')
