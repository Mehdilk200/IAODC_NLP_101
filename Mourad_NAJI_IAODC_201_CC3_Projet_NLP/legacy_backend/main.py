from fastapi import FastAPI
from pydantic import BaseModel
from backend.stylist_logic import recommend_outfits
from backend.images_search import search_images
from backend.nlp_extract import extract_preferences, build_search_query

app = FastAPI(title="Stylist Chatbot API")

class StyleRequest(BaseModel):
    message: str
    
class ImagesRequest(BaseModel):
    query: str
    num: int = 6

class ImagesRequest(BaseModel):
    query: str
    num: int = 6

@app.get("/")
def home():
    return {"status": "ok", "message": "Stylist API running"}

@app.post("/recommend")
def recommend(req: StyleRequest):
    return recommend_outfits(req.message)

@app.post("/images")
def images(req: ImagesRequest):
    prefs = extract_preferences(req.query)
    smart_query = build_search_query(prefs)
    imgs , data = search_images(smart_query, req.num)

    return {
        "user_query": req.query,
        "understood": prefs,
        "smart_query": smart_query,
        "images": imgs ,
        "data" : data
    }

@app.post("/images")
def images(req: ImagesRequest):
    return {"query": req.query, "images": search_images(req.query, req.num)}
