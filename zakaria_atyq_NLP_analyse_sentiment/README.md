# 🤖 AI Sentiment Analysis of Product Reviews using BERT

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-009688.svg)](https://fastapi.tiangolo.com/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.4.1-EE4C2C.svg)](https://pytorch.org/)
[![HuggingFace](https://img.shields.io/badge/HuggingFace-Transformers-FFAE00.svg)](https://huggingface.co/)

> A powerful AI-driven sentiment analysis system that uses BERT deep learning models to classify product reviews as Positive or Negative, featuring a FastAPI backend and an interactive modern web interface.

![Sentiment Analysis](https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=1200&h=400&fit=crop)

---

## 📋 Project Overview

This project implements a complete **Sentiment Analysis System** for product reviews using state-of-the-art **BERT (Bidirectional Encoder Representations from Transformers)** deep learning model.

The system provides:
- 🔍 **Real-time sentiment classification** using BERT
- 🌐 **RESTful API** built with FastAPI
- 🎨 **Modern web interface** with interactive dashboards
- 📊 **Analytics dashboard** with live metrics
- 🛍️ **Product review management** system

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🤖 **BERT Sentiment Analysis** | State-of-the-art deep learning model for accurate sentiment classification |
| ⚡ **FastAPI Backend** | High-performance REST API with async support |
| 🌐 **Interactive Web Interface** | Modern, responsive UI built with HTML, CSS, and JavaScript |
| 📦 **Product Review System** | Full CRUD operations for product reviews |
| 📈 **Real-time Analytics** | Live statistics dashboard with sentiment distribution |
| 🔎 **Search & Filtering** | Filter reviews by sentiment, search products by name |
| ⭐ **Star Ratings** | 5-star rating system for products |
| 🖼️ **Product Cards** | Beautiful product displays with images and prices |
| 📱 **Responsive Design** | Works on desktop, tablet, and mobile devices |

---

## 🛠️ Technologies Used

### Backend
- **Python** (3.8+) - Core programming language
- **FastAPI** - Modern web framework for building APIs
- **Transformers** (HuggingFace) - Pre-trained BERT models
- **PyTorch** - Deep learning framework
- **Pydantic** - Data validation
- **Uvicorn** - ASGI server

### Frontend
- **HTML5** - Markup language
- **CSS3** - Modern styling with animations
- **JavaScript** - Interactive functionality
- **Fetch API** - API communication

### Tools
- **Git** - Version control
- **VS Code** - Development environment

---

## 📁 Project Structure

```
zakaria_atyq_NLP_analyse_sentiment/
├── README.md                    # Project documentation
├── .gitignore                   # Git ignore file
├── Analyse de Sentiments avec BERT/
│   ├── main.py                  # FastAPI application entry point
│   ├── model.py                 # BERT sentiment model wrapper
│   ├── schemas.py               # Pydantic schemas for API
│   ├── requirements.txt         # Python dependencies
│   │
│   ├── interface/               # Frontend web interface
│   │   ├── index.html          # Main HTML page
│   │   ├── style.css           # CSS styles
│   │   └── app.js              # JavaScript functionality
│   │
│   ├── model/                   # Trained BERT model directory
│   │   └── (model files)
│   │
│   └── src/
│       ├── controller/
│       │   └── config.py       # Application configuration
│       └── database/
│           └── .gitkeep        # Database placeholder
```

---

## 📦 Installation Guide

### Prerequisites

| Requirement | Version |
|-------------|---------|
| Python | 3.8+ |
| pip | Latest |

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd zakaria_atyq_NLP_analyse_sentiment
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
cd "Analyse de Sentiments avec BERT"
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Create a `.env` file in the `Analyse de Sentiments avec BERT` directory:

```env
# Server Configuration
HOST=0.0.0.0
PORT=8000

# Model Configuration
MODEL_DIR=./model
MODEL_FALLBACK=bert-base-uncased
MAX_LEN=128

# CORS Configuration
CORS_ORIGINS=*

# Logging
LOG_LEVEL=INFO
```

---

## 🚀 How to Run the Backend (FastAPI)

### Starting the API Server

```bash
cd "Analyse de Sentiments avec BERT"
python main.py
```

Or with uvicorn directly:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Expected Output

```
✅ Modèle BERT chargé sur cpu (or cuda)
INFO:     Application startup complete
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🌐 How to Run the Frontend

### Option 1: Open Directly

Simply open the `index.html` file in your browser:

```bash
# Windows
start interface/index.html

# Mac
open interface/index.html

# Linux
xdg-open interface/index.html
```

### Option 2: Use a Local Server (Recommended)

```bash
# Using Python's http.server
cd interface
python -m http.server 3000
```

Then visit: http://localhost:3000

### Option 3: Using VS Code Live Server

1. Install the "Live Server" extension in VS Code
2. Right-click on `interface/index.html`
3. Select "Open with Live Server"

---

## 📡 Example API Request

### Predict Sentiment

**Endpoint:** `POST /predict`

```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"text": "This product is amazing! I love it so much."}'
```

**Response:**

```json
{
  "text": "This product is amazing! I love it so much.",
  "sentiment": "positif",
  "label": 1,
  "confidence": 0.9987,
  "proba_pos": 0.9987,
  "proba_neg": 0.0013,
  "inference_ms": 45.32
}
```

### Get All Products

**Endpoint:** `GET /products`

```bash
curl "http://localhost:8000/products"
```

### Get Health Status

**Endpoint:** `GET /health`

```bash
curl "http://localhost:8000/health"
```

### Create a Review

**Endpoint:** `POST /reviews`

```bash
curl -X POST "http://localhost:8000/reviews" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 1,
    "author": "John Doe",
    "text": "Great product! Highly recommended."
  }'
```

---

## 📊 API Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Root endpoint |
| `GET` | `/health` | Health check |
| `GET` | `/model/info` | Model information |
| `GET` | `/products` | Get all products |
| `POST` | `/predict` | Predict sentiment |
| `POST` | `/reviews` | Create a review |
| `GET` | `/stats` | Get statistics |

---

## 📸 Screenshots

### Home Page
The main landing page featuring the hero section with BERT-powered sentiment analysis capabilities.

### Analytics Dashboard
Real-time statistics showing:
- Total reviews count
- Positive vs Negative sentiment distribution
- Average confidence score
- Average rating

### Products Section
Product cards with:
- Product images
- Names and prices
- Star ratings
- Review counts
- Sentiment indicators

### AI Analyzer
Interactive sentiment analyzer where users can:
- Enter custom review text
- Get instant BERT predictions
- View confidence scores

---

## 🔮 Future Improvements

- [ ] **Model Fine-tuning** - Fine-tune BERT on domain-specific product reviews
- [ ] **Database Integration** - Add PostgreSQL/MongoDB for persistent storage
- [ ] **User Authentication** - Implement JWT-based authentication
- [ ] **Multi-language Support** - Add support for French, Spanish, Arabic
- [ ] **Deployment** - Docker containerization and cloud deployment
- [ ] **Batch Processing** - Process multiple reviews at once
- [ ] **Export Features** - Export analysis results to CSV/Excel
- [ ] **WebSocket Support** - Real-time streaming updates
- [ ] **Model Ensemble** - Combine multiple models for better accuracy

---

## 👤 Author

<div align="center">

**Zakaria**

*AI & Machine Learning Developer*

[![GitHub](https://img.shields.io/badge/GitHub-100000?style=flat&logo=github&logoColor=white)](https://github.com/)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=flat&logo=linkedin&logoColor=white)](https://linkedin.com/)

</div>

---

## 📄 License

This project is licensed under the MIT License.

---

## ⭐ Show Your Support

If you found this project useful, give it a ⭐️ on GitHub!

---

<div align="center">

*Built with ❤️ using BERT, FastAPI, and Python*

</div>

