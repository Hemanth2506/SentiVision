# SentiVision AI — "Understand Every Word. Instantly."

SentiVision AI is a production-grade full-stack sentiment analysis SaaS platform designed to extract user emotion from customer feedback, reviews, and transcripts. 

It leverages an advanced Natural Language Processing (NLP) pipeline evaluating multiple classifiers (Logistic Regression, Naive Bayes, Random Forest, SVM) and serving predictions through a FastAPI service and an interactive React web app.

---

## Key Features

1. **AI Preprocessing & ML Pipeline**: Auto-optimized stopword removal, tokenization, lemmatization, and TF-IDF extraction. Evaluates 4 classifiers and deploys the best based on weighted F1 score.
2. **Confidence stacking**: Returns probability distributions for Positive, Neutral, and Negative sentiments.
3. **Keyword highlighting**: Instantly highlights positive and negative influencing words in context.
4. **Bulk File Uploads**: Process hundreds of rows simultaneously from uploaded CSV/TXT files and export outputs.
5. **Analytics Dashboard**: Custom interactive charts tracking overall distribution, positivity index, daily counts, and logs.
6. **JWT Cookie Authentication**: Secure session control utilizing httpOnly token verification.

---

## Directory Structure

```text
sentivision-ai/
├── frontend/             # React + Vite + Tailwind CSS + ChartJS Web App
├── backend/              # Python FastAPI + SQLAlchemy + SQLite Server
├── ml/                   # ML preprocessor, evaluation, training and inference
├── dataset/              # Review samples for ML training
├── docker-compose.yml    # Main multi-container service orchestrator
└── .env.example          # Environment variables blueprint
```

---

## Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+ & npm
- Docker & Docker Compose (Optional)

### Quick Start with Docker
The fastest way to spin up the entire platform:
```bash
# 1. Clone/copy this directory
# 2. Spin up containers
docker-compose up --build
```
Once complete:
- **Web App**: `http://localhost:3000`
- **FastAPI Backend / Docs**: `http://localhost:8000/docs`

---

## Local Development Setup

### 1. Train the ML Model
First, generate the reviews training set and train the ML models:
```bash
# Clean, tokenize, and train all 4 classifiers (Logistic Regression, NB, RF, SVM)
python ml/download_dataset.py
python ml/train.py
```
This output-caches `model.pkl` and `vectorizer.pkl` within the `ml/` directory.

### 2. Run Python Backend
```bash
# Navigate to backend and install packages
cd backend
pip install -r requirements.txt

# Start local server
uvicorn main:app --reload --port 8000
```
Swagger docs will be generated automatically at `http://localhost:8000/docs`.

### 3. Run React Frontend
```bash
# Navigate to frontend and install packages
cd frontend
npm install

# Start local development server
npm run dev
```
Open `http://localhost:5173` in your browser.

---

## Tech Stack Details

- **Frontend**: React.js, Tailwind CSS (v3), Framer Motion (Transitions), Chart.js (Interactive dashboards), Axios (API client)
- **Backend**: Python, FastAPI, SQLAlchemy ORM, SQLite
- **ML Pipeline**: Scikit-Learn, NLTK, Joblib, Pandas, NumPy
- **Auth**: JWT session token stored in secure httpOnly cookies
