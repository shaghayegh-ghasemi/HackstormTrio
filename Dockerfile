# Use Python 3.9 as the base image
FROM python:3.9

# Set the working directory inside the container
WORKDIR /app

# Copy all files into the container
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose ports for Flask (5000) and Streamlit (8501)
EXPOSE 5000 8501

# Start the unified app (Flask + Streamlit)
CMD ["sh", "-c", "streamlit run backend/app.py --server.port=8501 --server.address=127.0.0.1"]
