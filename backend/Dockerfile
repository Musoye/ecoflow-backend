# 1. Use the official Python 3.10 slim image (lightweight & secure)
FROM python:3.10-slim

# 2. Set environment variables
# PYTHONDONTWRITEBYTECODE: Prevents Python from writing .pyc files to disk
# PYTHONUNBUFFERED: Ensures logs are piped directly to the container logs (vital for debugging)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Set the working directory inside the container
WORKDIR /app

# 4. Install system dependencies
# gcc and libpq-dev are often needed for building Python packages (like psycogp2 or others)
# We clean up the apt cache afterwards to keep the image small
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 5. Copy the requirements file first (Docker caching mechanism)
# This layer is only rebuilt if requirements.txt changes
COPY requirements.txt /app/

# 6. Install Python dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# 7. Copy the rest of the application code
COPY . /app/

# 8. Expose the port the app runs on
EXPOSE 8000

# 9. Define the command to run the application using Gunicorn
# Automatically run migrations on container startup, then start Gunicorn
# Optimized for Cloud Run: 2 workers, 4 threads each, worker class gthread for better I/O
CMD python manage.py migrate --noinput && \
    python manage.py collectstatic --noinput && \
    gunicorn --bind 0.0.0.0:$PORT \
    --workers 2 \
    --threads 4 \
    --worker-class gthread \
    --worker-tmp-dir /dev/shm \
    --timeout 300 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --access-logfile - \
    --error-logfile - \
    kazlat.wsgi:application