# StyleAI — Production-Grade AI Fashion Stylist

Fully modular AI platform using FastAPI + RAG (FAISS/Numpy) + Multi-language NLP.

## 🚀 Quick Start (Local)

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the API**:
   ```bash
   uvicorn api.main:app --host 127.0.0.1 --port 9000
   ```

3. **Access**:
   - Frontend: `http://localhost:9000`
   - Swagger / docs: `http://localhost:9000/api/docs`
   - Health check: `http://localhost:9000/health`

## 🧪 Testing the Pipeline

**Health Check**:
```bash
curl http://127.0.0.1:9000/health
```

**Recommendation Request**:
```bash
curl -X POST http://127.0.0.1:9000/recommend \
     -H "Content-Type: application/json" \
     -d '{"query": "formal winter wedding outfit for men", "top_k": 2}'
```

## 🐳 Running with Docker

```bash
docker-compose up --build
```

## 🛠 Features
- **Semantic Vector Search**: Uses FAISS (with Numpy fallback) for high-accuracy outfit retrieval.
- **NLP Proxy**: Structured preference extraction from natural language (English, French, Arabic, Darija).
- **Hybrid Ranking**: Combines vector similarity with rule-based scoring (budget, style, gender).
- **Intelligent Image Display**: High-quality images via Pexels API with intelligent local fallbacks.
- **Responsive UI**: Modern chat interface with real-time feedback.

## 🖼 Image Service Setup

### (Option A) Pexels API (Online)
1. Get a free API key from [Pexels](https://www.pexels.com/api/).
2. Create a `.env` file in the root directory.
3. Add your key:
   ```env
   PEXELS_API_KEY=your_key_here
   IMAGES_PROVIDER=auto
   ```

### (Option B) Local Fallback (Offline)
If no API key is provided, the system serves images from `data/images/`.
Folder structure:
- `data/images/placeholder.jpg` (Mandatory)
- `data/images/casual/`
- `data/images/formal/`
- `data/images/streetwear/`
- `data/images/men/`
- `data/images/women/`
