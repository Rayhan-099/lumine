<div align="center">
  <img src="https://via.placeholder.com/150/000000/FFFFFF?text=LUMINE" alt="Lumine Logo" width="120" height="120">
  <h1 align="center">Lumine AI</h1>
  <p align="center">
    <strong>Production-Grade AI Dermatology Platform</strong>
  </p>
  <p align="center">
    An intelligent, cinematic SaaS platform bridging advanced computer vision with personalized skincare analysis.
  </p>
  <p align="center">
    <a href="https://lumineai.vercel.app/"><strong>Live Production Deployment</strong></a>
  </p>
</div>

---

**Lumine AI** is an intelligent AI-powered skin analysis, monitoring, and personalized skincare intelligence platform. 

Combining the visual diagnostic power of Vision Transformers (Hugging Face CNN inference) with the deep contextual intelligence of Google Gemini, Lumine AI allows users to actively monitor their skin health over time, rather than just receiving a static prediction.

> **Disclaimer:** Lumine AI is an informational tool and does not provide medical diagnoses. Always consult a certified dermatologist for professional advice.

---

## 🌟 Key Features

*   **Intelligent Skin Analysis:** Upload an image and describe your symptoms. Lumine cross-references a visual CNN prediction with your text description using Gemini to provide a comprehensive, understandable insight.
*   **Longitudinal Skin Trends:** Track how your skin changes over time with interactive charts mapping your AI match distributions and condition severities.
*   **Before/After Comparisons:** Select any two past scans to view them side-by-side. The AI synthesizes a delta summary explaining if your condition is changing.
*   **Context-Aware AI Assistant:** Chat with Lumine AI about your skin history. Gemini is injected with your past 10 scans to provide deeply personalized answers.
*   **Exportable PDF Reports:** Generate and download professional PDF summaries of any scan to share with your dermatologist.
*   **Secure & Private:** Full JWT authentication, rigorous data ownership boundaries, and "Clear History" privacy controls compliant with modern data retention standards.

---

## 🏗️ Architecture

*   **Frontend:** React (Create React App), Recharts (data visualization), Vanilla CSS (Premium Health-Tech UI).
*   **Backend:** FastAPI (Python), SQLAlchemy (ORM).
*   **Database:** SQLite (local development) / PostgreSQL ready via Alembic migrations.
*   **AI Integration:** 
    *   Hugging Face Inference API (`Jayanth2002/dinov2-base-finetuned-SkinDisease` or configurable via `HF_IMAGE_MODEL`) for image classification.
        *   *Note: If the configured HF model returns a 404, it means free serverless inference is unavailable. (Historically used `dima806/skin-disease-classification` which is deprecated in production).*
    *   Google Generative AI (configurable via `GEMINI_MODEL`, defaults to `gemini-2.5-flash`) for NLP synthesis and conversational memory.

---

## 🚀 Setup Instructions

### 1. Backend (FastAPI)

1. Navigate to the project root.
2. Create a virtual environment: `python -m venv venv`
3. Activate the environment: 
   * Windows: `venv\Scripts\activate`
   * Mac/Linux: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Set up your `.env` file based on `.env.example`. You **must** provide a `GEMINI_API_KEY` and a `JWT_SECRET_KEY`.
6. Run database migrations: `alembic upgrade head`
7. Start the server:
   * Windows: `start.bat`
   * Mac/Linux: `./start.sh`

### 2. Frontend (React)

1. Navigate to the `src` directory (if separate) or stay in the root if combined.
2. Install dependencies: `npm install`
3. Start the development server: `npm start`
4. The application will be available at `http://localhost:3000`.

---

## 🛡️ Privacy & Security

Lumine AI takes user privacy seriously. All endpoints are guarded by JWT authentication. Users have complete control over their data, with the ability to delete individual records or completely wipe their account history via the dashboard.

*Note: This repository is a transformed evolution of the original "Viani" project, refactored into a scalable, production-ready intelligence platform.*
