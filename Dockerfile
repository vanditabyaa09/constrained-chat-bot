# Stage 1: Build Frontend
FROM node:20-slim AS frontend-build
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Stage 2: Serve with Backend
FROM python:3.11-slim
WORKDIR /app

# Install system dependencies (needed for some python packages like faiss-cpu)
RUN apt-get update && apt-get install -y \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code and built frontend
COPY app/ ./app/
COPY backend/ ./backend/
COPY --from=frontend-build /frontend/dist ./frontend/dist

# Set environment variables
ENV PYTHONPATH=.
ENV HF_API_TOKEN=""

# Expose port
EXPOSE 8000

# Start the application
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
