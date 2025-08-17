# Use slim Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files including service account JSON and placeholder RAG
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Streamlit environment variables
ENV STREAMLIT_SERVER_ENABLECORS=false
ENV STREAMLIT_SERVER_HEADLESS=true

# Set path to service account JSON
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/service_account.json

# Run the app
CMD ["streamlit", "run", "app.py"]
