FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the FastAPI app code into the container
COPY serve.py .

# Expose port 8000
EXPOSE 8000

# Start the FastAPI app when the container starts
CMD ["uvicorn", "serve:app", "--host", "0.0.0.0", "--port", "8000"]