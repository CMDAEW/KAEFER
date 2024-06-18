# Use the official lightweight Python image.
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create and change to the app directory.
WORKDIR /app

# Install dependencies.
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copy the rest of the application code.
COPY . .

# Run the application.
CMD ["python", "run.py"]
