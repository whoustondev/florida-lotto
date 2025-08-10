FROM python:3.12-bullseye

ENV PYTHONUNBUFFERED=1
ENV APP_HOME=/back-end
WORKDIR $APP_HOME
COPY . ./

# Install minimal dependencies for pdfplumber & requests
RUN apt-get update && apt-get install -y \
    libnss3 \
    libxss1 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libasound2 \
    xdg-utils \
    fonts-liberation \
    libgbm1 \
    libu2f-udev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && update-ca-certificates \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port
ENV PORT=5000
EXPOSE 5000

# Run Gunicorn server
CMD exec gunicorn --bind :$PORT --workers 1 --threads 1 --timeout 0 --log-level debug app:app
