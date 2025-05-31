# Use official Python image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Set working directory
WORKDIR /app

# Install system and browser dependencies for Playwright
RUN apt-get update && apt-get install -y \
    wget gnupg ca-certificates curl unzip \
    libglib2.0-0 libnss3 libgconf-2-4 libfontconfig1 libx11-xcb1 \
    libxcomposite1 libxcursor1 libxdamage1 libxext6 libxi6 \
    libxtst6 libxrandr2 libasound2 libatk1.0-0 libatk-bridge2.0-0 \
    libgtk-3-0 libdrm2 libgbm1 lsb-release fonts-liberation \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy the application code
COPY app/ ./app

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install fastapi uvicorn requests beautifulsoup4 lxml python-dateutil pytz playwright

# Install Playwright browser binaries
RUN playwright install --with-deps

# Set the default command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]