# 🧠 AI Resume Screening System

> **NLP-powered CV matching and candidate ranking using Sentence Transformers & KeyBERT**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react)](https://react.dev)
[![MongoDB](https://img.shields.io/badge/MongoDB-7.0-47A248?logo=mongodb)](https://mongodb.com)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python)](https://python.org)

---

## 🎯 What It Does

This system allows recruiters to:

1. **Upload candidate CVs** (PDF or DOCX)
2. **Create job descriptions** with required skills
3. **Compute semantic similarity** using Sentence Transformers
4. **Extract skills** using KeyBERT + curated dictionary
5. **View match scores** (0–100%) with matched/missing skills
6. **Rank multiple candidates** by job relevance
7. **Download PDF reports** for each match
8. **Multilingual support** (English & French CVs)

---

## 🏗️ Architecture

```
React Frontend (Vite)
       │
       ▼ HTTP / REST API
FastAPI Backend
       │
       ├── NLP Pipeline
       │     ├── PDF/DOCX Parser (pdfplumber / PyMuPDF / python-docx)
       │     ├── Text Cleaner (NLTK stopwords, regex)
       │     ├── Skill Extractor (KeyBERT + curated dictionary)
       │     ├── Embedding Generator (sentence-transformers/all-MiniLM-L6-v2)
       │     └── Similarity Engine (cosine similarity → 0–100%)
       │
       └── MongoDB (Motor async driver)
```

---

## 📁 Project Structure

```
nlp_project_cv/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI app entry point
│   │   ├── core/
│   │   │   ├── config.py            # Pydantic settings
│   │   │   └── security.py          # JWT auth utilities
│   │   ├── routes/
│   │   │   ├── auth.py              # Login / Register
│   │   │   ├── upload.py            # CV upload & candidates
│   │   │   ├── job.py               # Job descriptions CRUD
│   │   │   └── match.py             # Matching & ranking
│   │   ├── services/
│   │   │   ├── parser.py            # PDF/DOCX text extraction
│   │   │   ├── text_cleaning.py     # NLP text preprocessing
│   │   │   ├── skill_extractor.py   # KeyBERT + dictionary
│   │   │   ├── embedding.py         # Sentence Transformers
│   │   │   ├── similarity.py        # Cosine similarity
│   │   │   └── report_generator.py  # PDF report (ReportLab)
│   │   ├── models/
│   │   │   ├── candidate.py         # Pydantic schemas
│   │   │   └── job.py               # Pydantic schemas
│   │   └── database/
│   │       └── connection.py        # MongoDB Motor connection
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Sidebar.jsx          # Navigation sidebar
│   │   │   ├── UploadCV.jsx         # CV upload + candidate list
│   │   │   ├── JobForm.jsx          # Job creation/editing
│   │   │   ├── MatchResult.jsx      # Single match view
│   │   │   └── CandidateRanking.jsx # Bulk ranking table
│   │   ├── pages/
│   │   │   ├── AuthPage.jsx         # Login / Register
│   │   │   └── Dashboard.jsx        # Overview & stats
│   │   ├── services/
│   │   │   └── api.js               # Axios API client
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css                # Full design system
│   ├── Dockerfile
│   └── .env
│
├── docker-compose.yml
└── README.md
```

---

## 🚀 Quick Start (Local Development)

### Prerequisites

- Python 3.10+
- Node.js 18+
- MongoDB (local or Atlas)
- Git

---

### 1️⃣ Clone & Setup Backend

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate
# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
copy .env.example .env
# Edit .env with your MongoDB URL and secret key
```

### 2️⃣ Start Backend

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: http://localhost:8000
Interactive docs: http://localhost:8000/docs

---

### 3️⃣ Setup & Start Frontend

```bash
cd frontend
npm install
npm run dev
```

The app will be available at: http://localhost:5173

---

## 🐳 Docker Deployment

```bash
# Build and start all services
docker-compose up --build

# Run in background
docker-compose up -d --build

# Stop all services
docker-compose down
```

Services:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **MongoDB**: localhost:27017

---

## 🔌 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register recruiter |
| POST | `/api/auth/login` | Login (returns JWT) |

### CV Upload
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/upload/cv` | Upload PDF/DOCX CV |
| GET | `/api/upload/candidates` | List all candidates |
| GET | `/api/upload/candidates/{id}` | Get candidate |
| DELETE | `/api/upload/candidates/{id}` | Delete candidate |

### Job Descriptions
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/jobs/` | Create job |
| GET | `/api/jobs/` | List all jobs |
| GET | `/api/jobs/{id}` | Get job |
| PUT | `/api/jobs/{id}` | Update job |
| DELETE | `/api/jobs/{id}` | Delete job |

### Matching
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/match/single` | Match one candidate to job |
| POST | `/api/match/bulk` | Rank all candidates for job |
| GET | `/api/match/report/{cid}/{jid}` | Download PDF report |
| GET | `/api/match/dashboard/stats` | Dashboard statistics |

---

## 🤖 NLP Pipeline

### 1. Text Extraction
- **PDF**: pdfplumber (primary) → PyMuPDF (fallback)
- **DOCX**: python-docx (paragraphs + tables)

### 2. Language Detection
- `langdetect` library
- Supports English and French
- Affects stopword removal

### 3. Text Cleaning
- Lowercase normalization
- URL and email removal
- Special character removal
- NLTK stopword removal (EN + FR)

### 4. Skill Extraction
- **Dictionary matching**: 100+ curated tech/soft skills
- **KeyBERT**: Semantic keyword extraction (1-2 gram phrases)
- **French aliases**: Normalized to English equivalents

### 5. Embedding Generation
- Model: `sentence-transformers/all-MiniLM-L6-v2`
- 384-dimensional dense vectors
- Cached after first load

### 6. Similarity Computation
- Cosine similarity between CV and JD embeddings
- Normalized to 0–100% score
- Score interpretation:
  - ≥ 80%: Excellent match 🌟
  - ≥ 65%: Good match ✅
  - ≥ 45%: Partial match ⚠️
  - < 45%: Poor match ❌

---

## 📊 Example Output

```
Match Score: 82%

Matched Skills:
✔ Python
✔ Machine Learning
✔ SQL
✔ NLP
✔ Pandas

Missing Skills:
✘ Docker
✘ AWS
✘ Kubernetes
```

---

## ⚙️ Environment Variables

### Backend (.env)
```env
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=cv_screening
SECRET_KEY=your-super-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

### Frontend (.env)
```env
VITE_API_URL=http://localhost:8000/api
```

---

## 🗄️ Database Schema

### Candidates Collection
```json
{
  "_id": "ObjectId",
  "name": "John Doe",
  "email": "john@example.com",
  "cv_text": "raw extracted text...",
  "cleaned_text": "cleaned version...",
  "skills": ["python", "machine learning", "sql"],
  "embedding": [0.123, -0.456, ...],  // 384 floats
  "language": "en",
  "filename": "john_cv.pdf",
  "score": 82.5
}
```

### Jobs Collection
```json
{
  "_id": "ObjectId",
  "title": "Senior Data Scientist",
  "description": "full job description...",
  "cleaned_text": "cleaned version...",
  "required_skills": ["python", "machine learning", "docker"],
  "company": "TechCorp",
  "location": "Remote",
  "embedding": [0.789, -0.012, ...]  // 384 floats
}
```

---

## 🔒 Security

- JWT authentication with bcrypt password hashing
- Token expiry (configurable, default 30 min)
- CORS configured for specific origins
- File size limit (10 MB)
- File type validation (PDF/DOCX only)

---

## 📦 Key Dependencies

### Backend
| Package | Version | Purpose |
|---------|---------|---------|
| fastapi | 0.109 | Web framework |
| sentence-transformers | 2.6 | NLP embeddings |
| keybert | 0.8 | Skill extraction |
| pdfplumber | 0.10 | PDF parsing |
| PyMuPDF | 1.23 | PDF fallback |
| python-docx | 1.1 | DOCX parsing |
| motor | 3.3 | Async MongoDB |
| reportlab | 4.1 | PDF reports |
| langdetect | 1.0 | Language detection |
| nltk | 3.8 | Text processing |

### Frontend
| Package | Version | Purpose |
|---------|---------|---------|
| react | 18 | UI framework |
| react-router-dom | 6 | Routing |
| axios | 1.6 | HTTP client |
| react-dropzone | 14 | File upload |
| react-hot-toast | 2 | Notifications |
| lucide-react | 0.3 | Icons |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit changes: `git commit -m 'Add my feature'`
4. Push: `git push origin feature/my-feature`
5. Open a Pull Request

---

## 📄 License

MIT License — feel free to use for personal and commercial projects.

---

*Built with ❤️ using FastAPI, React, Sentence Transformers, and MongoDB*
