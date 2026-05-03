# 📄 DocChat: AI-Powered PDF Conversational Agent

DocChat is a high-performance, full-stack RAG (Retrieval-Augmented Generation) application that allows users to upload PDF documents and have context-aware conversations with them. Built with a focus on precision and transparency, every AI response includes verifiable page citations.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![React](https://img.shields.io/badge/React-19-blue?logo=react)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green?logo=fastapi)
![Tailwind](https://img.shields.io/badge/Tailwind-v4-38B2AC?logo=tailwind-css)

---

## ✨ Key Features

- **Context-Aware Chat**: Advanced RAG pipeline using LangChain and Hugging Face.
- **Verifiable Citations**: Automatic extraction of page numbers for every AI response.
- **Smart Chunking**: Implements sliding window text processing to preserve context at boundaries.
- **Fast Search**: Powered by FAISS (Facebook AI Similarity Search) for millisecond retrieval.
- **Premium UI**: Linear-inspired dark mode, responsive design, and smooth micro-animations.
- **Dockerized**: Simplified deployment using a multi-stage Docker build.

---

## 🛠️ Tech Stack

### **Frontend**
- **Framework**: React 19 (TypeScript + Vite)
- **Styling**: Tailwind CSS v4 (Zero-config)
- **State Management**: Zustand
- **Icons**: Lucide React

### **Backend**
- **API Framework**: FastAPI (Python 3.11+)
- **AI Orchestration**: LangChain & LangChain-HuggingFace
- **Vector Store**: FAISS (faiss-cpu)
- **LLM**: Qwen 2.5 7B Instruct (via Hugging Face Inference API)
- **PDF Processing**: PyPDF

---

## 🚀 Getting Started

### **Prerequisites**
- Python 3.11+
- Node.js 20+
- A Hugging Face User Access Token ([Get it here](https://huggingface.co/settings/tokens))

### **1. Clone & Setup**
```bash
git clone https://github.com/vanditabyaa09/constrained-chat-bot.git
cd constrained-chat-bot
```

### **2. Backend Setup**
```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file
echo "HF_API_TOKEN=your_token_here" > .env

# Run the server
python backend/main.py
```
*Backend runs on `http://localhost:8000`*

### **3. Frontend Setup**
```bash
cd frontend
npm install
npm run dev
```
*Frontend runs on `http://localhost:5173`*

---

## 🐳 Running with Docker

The project includes a multi-stage Dockerfile that bundles the frontend and backend into a single container.

1. **Build the image**:
   ```bash
   docker build -t docchat .
   ```

2. **Run the container**:
   ```bash
   docker run -p 8000:8000 -e HF_API_TOKEN="your_token_here" docchat
   ```
*Access the unified app at `http://localhost:8000`*

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/upload` | Upload a PDF and build the vector index. |
| `POST` | `/chat` | Send a query and get a context-aware response. |
| `DELETE` | `/reset` | Clear the current document and chat history. |

---

## 📝 Design Rationale

- **Hybrid UI**: Combines a persistent sidebar for document management with a focused, conversational main panel.
- **Developer First**: Built with TypeScript for type safety and modular Python classes for easy extensibility.
- **Instruct Model Optimization**: Uses the `ChatHuggingFace` wrapper to properly handle conversational templates for modern LLMs.
