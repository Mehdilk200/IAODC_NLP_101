import os
import requests
from dotenv import load_dotenv

load_dotenv()

SERPAPI_KEY = os.getenv("SERPAPI_KEY")


def build_fashion_query(user_query: str) -> str:
    # كنضيف كلمات كتجبر البحث يكون fashion
    boosters = [
        "outfit", "fashion", "style", "look",
        "mens outfit", "streetwear", "formal wear",
        "lookbook", "pinterest inspiration"
    ]
    return user_query + " " + " ".join(boosters)


def search_images(query: str, num: int = 6):
    if not SERPAPI_KEY:
        return []

    # نصلحو الquery
    fashion_query = build_fashion_query(query)

    params = {
        "engine": "google_images",
        "q": fashion_query,
        "api_key": SERPAPI_KEY,
        "ijn": "0"
    }

    response = requests.get("https://serpapi.com/search.json", params=params)
    data = response.json()

    images = []

    # كلمات باش نفلترّيو غير الصور ديال fashion
    fashion_words = [
        "outfit", "fashion", "style", "wear",
        "streetwear", "suit", "jacket",
        "coat", "shoes", "look"
    ]
    
    for item in data.get("images_results", []):
        title = item.get("title", "").lower()
        link = item.get("link", "").lower()

        # فلترة النتائج
        if any(word in title or word in link for word in fashion_words):
            images.append({
                "title": item.get("title"),
                "thumbnail": item.get("thumbnail"),
                "link": item.get("link")
            })

        if len(images) >= num:
            break
        
    return images , data